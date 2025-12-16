import logging
import json
import os
import re
import time
from functools import wraps
from pathlib import Path
from typing import Callable, List, Optional, Dict, Any

from pyspark.sql.dataframe import DataFrame 

try:
    import yaml
except ImportError:
    yaml = None

from pyspark.sql import SparkSession, DataFrame


def _is_dataframe(obj) -> bool:
    from pyspark.sql.dataframe import DataFrame as PySparkDataFrame
    try:
        from pyspark.sql.connect.dataframe import DataFrame as SparkConnectDataFrame
        return isinstance(obj, (PySparkDataFrame, SparkConnectDataFrame))
    except ImportError:
        return isinstance(obj, PySparkDataFrame)

from pyspark.sql.readwriter import DataFrameReader

from .lib_wrapper import load_lib, ProphecyLibError, ProphecyLib
from .prophecy_dataframe import ProphecyDataFrame
from .utils import _get_caller_name
from .common import wf
from .secrets import ProphecySecrets, SecretsProvider

_spark: Optional[SparkSession] = None
_lib: Optional[ProphecyLib] = None
_connections: Dict[str, Dict[str, Any]] = {}


logger = logging.getLogger(__name__)
lib = load_lib()


def instrument(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        load_connections_from_yaml()
        try:
            return func(*args, **kwargs)
        finally:
            close()
    return wrapper

class ProphecyDataFrameReader:
   
    def __init__(self, reader: DataFrameReader):
        self._reader = reader
    
    def __getattr__(self, name: str):
        attr = getattr(self._reader, name) 
        if callable(attr):
            def wrapper(*args, **kwargs):
                result = attr(*args, **kwargs)
                if _is_dataframe(result):
                    gem_name = _get_caller_name()
                    pdf = wf.create_pdf(gem_name)
                    pdf.df = result
                    pdf.is_pyspark_gem = True
                    logger.info(f"Created ProphecyDataFrame from spark.read operation in gem '{gem_name}'")
                    return pdf.df
                else:
                    if isinstance(result, DataFrameReader):
                        return ProphecyDataFrameReader(result)
                    return result
            
            return wrapper
        else:
            return attr


class ProphecySparkSession:

    def __init__(self, spark_session: SparkSession):
        self._spark = spark_session
    
    @property
    def read(self) -> ProphecyDataFrameReader:
        return ProphecyDataFrameReader(self._spark.read)
    
    def createDataFrame(self, data, schema=None, samplingRatio=None, verifySchema=True):
        result_df = self._spark.createDataFrame(data, schema, samplingRatio, verifySchema)
        
        gem_name = _get_caller_name(2)
        
        pdf = wf.create_pdf(gem_name)
        pdf.df = result_df
        pdf.is_pyspark_gem = True
         
        return pdf.df

_prophecy_spark: Optional[ProphecySparkSession] = None


def _get_or_create_prophecy_spark() -> ProphecySparkSession:
    global _prophecy_spark
    
    if _prophecy_spark is None:
        from .utils import get_spark
        real_spark = get_spark()
        _prophecy_spark = ProphecySparkSession(real_spark)
    
    return _prophecy_spark


class _SparkProxy:
    def __getattr__(self, name: str):
        return getattr(_get_or_create_prophecy_spark(), name)

spark = _SparkProxy()


# ============================================================================
# DSL-STYLE API - Read / Write
# ============================================================================

class _ReadAPI:

    def snowflake(
        self,
        schema: str,
        table: str,
        connection_name: str
    ) -> DataFrame:
        return snowflake_read(schema, table, connection_name)
    
    def databricks(
        self,
        catalog: str,
        schema: str,
        table: str,
        connection_name: str
    ) -> DataFrame:
        return databricks_read(
            user_config={
                "catalog": catalog,
                "schema": schema,
                "table": table
            },
            connection_name=connection_name
        )

    def databricks_volume(
        self,
        file_path: str,
        file_format: str = "csv",
        connection_name: str = None
    ) -> DataFrame:
        return databricks_volume_read(
            user_config={
                "filePath": file_path,
                "fileFormat": file_format
            },
            connection_name=connection_name
        )

    def sftp(
        self,
        file_path: str,
        file_format: str = "csv",
        connection_name: str = None
    ) -> DataFrame:
        return sftp_read(
            file_path=file_path,
            file_format=file_format,
            connection_name=connection_name
        )


class _WriteAPI:
    """
    DSL-style API for write operations.
    
    Provides a clean interface: orchestrate.write.email(...)
    """
    
    def databricks(
        self,
        data: DataFrame,
        catalog: str,
        schema: str,
        table: str,
        write_mode: str = "overwrite",
        connection_name: str = None
    ):
        return databricks_write(
            data=data,
            user_config={
                "catalog": catalog,
                "schema": schema,
                "table": table,
                "writeMode": write_mode
            },
            connection_name=connection_name
        )
    
    def databricks_volume(
        self,
        data: DataFrame,
        file_path: str,
        file_format: str = "csv",
        write_mode: str = "overwrite",
        connection_name: str = None
    ):
        return databricks_volume_write(
            data=data,
            user_config={
                "filePath": file_path,
                "fileFormat": file_format,
                "writeMode": write_mode
            },
            connection_name=connection_name
        )
    
    def tableau(
        self,
        data: DataFrame,
        project_name: str,
        datasource_name: str,
        connection_name: str
    ):
        return tableau_write(
            data=data,
            project_name=project_name,
            datasource_name=datasource_name,
            connection_name=connection_name
        )
    
    def email(
        self,
        data: DataFrame,
        to: List[str],
        subject: str,
        body: str,
        cc: List[str] = None,
        bcc: List[str] = None,
        file_format: str = "csv",
        file_name: str = "data.csv",
        connection_name: str = None
    ):
        return send_email(
            data=data,
            to=to,
            subject=subject,
            body=body,
            cc=cc,
            bcc=bcc,
            file_format=file_format,
            file_name=file_name,
            connection_name=connection_name
        )

    def sftp(
        self,
        data: DataFrame,
        file_path: str,
        file_format: str = "csv",
        connection_name: str = None
    ):
        return sftp_write(
            data=data,
            file_path=file_path,
            file_format=file_format,
            connection_name=connection_name
        )
    
    def rest_api(
        self,
        data: Optional[DataFrame],
        url: str,
        method: str = "POST",
        body: Optional[str] = None,
        params: Optional[List[Dict[str, str]]] = None,
        headers: Optional[List[Dict[str, str]]] = None,
        target_column_name: str = "api_response",
        parse_api_response: bool = True,
        auth_type: str = "none",
        credentials: Optional[Dict[str, Any]] = None
    ) -> DataFrame:
        return rest_api_call(
            data=data,
            url=url,
            method=method,
            body=body,
            params=params,
            headers=headers,
            target_column_name=target_column_name,
            parse_api_response=parse_api_response,
            auth_type=auth_type,
            credentials=credentials
        )


read = _ReadAPI()
write = _WriteAPI()


# ============================================================================
# CONNECTION MANAGEMENT
# ============================================================================

def add_connection(name: str, config: Dict[str, Any]) -> None:
    _connections[name] = config
    logger.info(f"Connection '{name}' registered")


def get_connection(name: str) -> Dict[str, Any]:
    if name not in _connections:
        raise KeyError(
            f"Connection '{name}' not found. Available connections: {list(_connections.keys())}"
        )
    return _connections[name]


def list_connections() -> List[str]:
    return list(_connections.keys())


def load_connections_from_yaml(yaml_path: Optional[str] = None) -> None:
    if yaml_path is None:
        import inspect
        caller_frame = inspect.stack()[1]
        caller_file = caller_frame.filename
        curr = Path(caller_file)
        yaml_path = curr.parent.parent.parent / "connections" / "connections.yml"
    else:
        
        yaml_path = Path(yaml_path)
    
    if not yaml_path.exists():
        raise FileNotFoundError(
            f"connections.yml not found at: {yaml_path}"
        )
    
    # Check if yaml module is available
    if yaml is None:
        raise ImportError(
            "PyYAML is not installed. Please install it with: pip install pyyaml"
        )
    
    # Read and parse YAML
    with open(yaml_path, 'r') as f:
        yaml_content = yaml.safe_load(f)
    
    if not isinstance(yaml_content, dict) or 'fabrics' not in yaml_content:
        raise ValueError(
            "Invalid YAML structure: expected 'fabrics' key at root level"
        )
    
    fabrics = yaml_content.get('fabrics', {})
    
    # Process each fabric
    for fabric_name, fabric_config in fabrics.items():
        if not isinstance(fabric_config, dict):
            logger.warning(f"Skipping invalid fabric config for '{fabric_name}'")
            continue
        
        connections = fabric_config.get('connections', {})
        if not isinstance(connections, dict):
            logger.warning(f"No connections found for fabric '{fabric_name}'")
            continue
        
        # Process each connection in the fabric
        for conn_name, conn_config in connections.items():
            try:
                converted_config = _convert_yaml_connection_to_dict(conn_config)
                add_connection(conn_name, converted_config)
                logger.info(f"Loaded connection '{conn_name}' from fabric '{fabric_name}'")
            except Exception as e:
                logger.error(
                    f"Failed to load connection '{conn_name}' from fabric '{fabric_name}': {e}"
                )
                raise


def _parse_secret_function_args(args_str: str) -> List[str]:
    args = []
    # Match quoted strings
    pattern = r"'([^']*)'|\"([^\"]*)\""
    matches = re.findall(pattern, args_str)
    for match in matches:
        # Each match is a tuple of (single_quoted, double_quoted)
        # One will be empty, the other will have the value
        arg = match[0] if match[0] else match[1]
        args.append(arg)
    return args


def _parse_and_resolve_secret(value: str) -> str:
    pattern = r'^(\w+)_secret\(([^)]+)\)$'
    match = re.match(pattern, value)
    
    if not match:
        raise ValueError(
            f"Invalid secret format: '{value}'. "
            f"Expected format: provider_secret('arg1', 'arg2')\n"
            f"Examples:\n"
            f"  - databricks_secret('scope', 'key')\n"
            f"  - prophecy_secret('scope', 'name')\n"
            f"  - hashicorp_secret('path', 'key')\n"
            f"  - environment_secret('var_name')"
        )
    
    provider_str = match.group(1).lower()
    args_str = match.group(2)
    
    # Parse arguments
    args = _parse_secret_function_args(args_str)
    
    # Validate provider
    provider_map = {
        'databricks': SecretsProvider.DATABRICKS,
        'hashicorp': SecretsProvider.HASHICORP,
        'environment': SecretsProvider.ENVIRONMENT,
        'prophecy': SecretsProvider.PROPHECY,
    }
    
    if provider_str not in provider_map:
        raise ValueError(
            f"Unsupported secret provider: '{provider_str}'. "
            f"Supported providers: {', '.join(provider_map.keys())}"
        )
    
    provider = provider_map[provider_str]
    
    # Parse scope and key based on provider and arguments
    if provider == SecretsProvider.ENVIRONMENT:
        # environment_secret('VAR_NAME')
        if len(args) != 1:
            raise ValueError(
                f"environment_secret expects 1 argument (var_name), got {len(args)}: {value}"
            )
        scope = ""
        key = args[0]
    
    elif provider == SecretsProvider.PROPHECY:
        # prophecy_secret('scope', 'name') or prophecy_secret('name')
        if len(args) == 1:
            # Single argument: use empty scope or get from environment
            scope = os.environ.get('PROPHECY_FABRIC_ID', '')
            key = args[0]
            if not scope:
                logger.warning(
                    f"prophecy_secret called with single argument but PROPHECY_FABRIC_ID not set. "
                    f"Using empty scope."
                )
        elif len(args) == 2:
            scope = args[0]
            key = args[1]
        else:
            raise ValueError(
                f"prophecy_secret expects 1 or 2 arguments (name) or (scope, name), got {len(args)}: {value}"
            )
    
    elif provider in [SecretsProvider.DATABRICKS, SecretsProvider.HASHICORP]:
        # databricks_secret('scope', 'key') or hashicorp_secret('path', 'key')
        if len(args) != 2:
            raise ValueError(
                f"{provider_str}_secret expects 2 arguments (scope, key), got {len(args)}: {value}"
            )
        scope = args[0]
        key = args[1]
    
    else:
        raise ValueError(f"Unsupported provider: {provider}")
    
    # Validate HashiCorp environment variables
    if provider == SecretsProvider.HASHICORP:
        vault_addr = os.environ.get('VAULT_ADDR')
        vault_token = os.environ.get('VAULT_TOKEN')
        
        if not vault_addr:
            raise RuntimeError(
                f"HashiCorp Vault secret requested but VAULT_ADDR environment variable is not set. "
                f"Please set VAULT_ADDR to your Vault server address."
            )
        
        if not vault_token:
            raise RuntimeError(
                f"HashiCorp Vault secret requested but VAULT_TOKEN environment variable is not set. "
                f"Please set VAULT_TOKEN to authenticate with Vault."
            )
        
        logger.info(f"Using HashiCorp Vault at: {vault_addr}")
    
    logger.info(f"Resolving secret: provider={provider_str}, scope={scope or 'N/A'}, key={key}")
    
    try:
        # Resolve the secret
        resolved_value = ProphecySecrets.get(scope, key, provider_str)
        logger.info(f"Successfully resolved secret for key '{key}'")
        return resolved_value
    except Exception as e:
        raise ValueError(
            f"Failed to resolve secret (provider={provider_str}, scope={scope}, key={key}): {str(e)}"
        ) from e


def _convert_yaml_connection_to_dict(conn_config: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(conn_config, dict):
        raise ValueError("Connection config must be a dictionary")
    
    result = {}
    
    if 'properties' in conn_config:
        properties = conn_config.get('properties', {})
        if isinstance(properties, dict):
            for key, value in properties.items():
                _process_and_store(key, value, result)
    else:
        raise Exception('Invalid yaml format. Expecting `properties` keyword')
    
    return result


def _is_secret_reference(value: str) -> bool:
    # Match pattern: provider_secret('args')
    pattern = r'^\w+_secret\([^)]+\)$'
    return bool(re.match(pattern, value))


def _process_and_store(key: str, value: Any, result: Dict[str, Any]) -> None:
    if isinstance(value, dict):
        # For nested dictionaries, merge their contents directly into result
        # This flattens structures like authentication.method -> method
        for nested_key, nested_value in value.items():
            # Recursively process nested values
            _process_and_store(nested_key, nested_value, result)
    elif isinstance(value, list):
        # Keep lists as-is
        result[key] = value
    else:
        # Primitive values (strings, numbers, booleans)
        # Check if string value is a secret reference
        if isinstance(value, str) and _is_secret_reference(value):
            try:
                # Resolve the secret and store the actual value
                resolved_value = _parse_and_resolve_secret(value)
                result[key] = resolved_value
                logger.info(f"Resolved secret for connection field '{key}'")
            except (ValueError, RuntimeError) as e:
                # Re-raise with more context
                raise ValueError(f"Error resolving secret for field '{key}': {str(e)}") from e
        else:
            # Store primitive value as-is
            result[key] = value


def close():
    wf.close_all()


def reset():
    global _prophecy_spark
    
    logger.info("Resetting prophecy module state")
    
    # Close all PDFs and clear workflow registry
    wf.close_all()
    
    # Reset global Spark session proxy
    _prophecy_spark = None
    
    logger.info("Prophecy module state reset complete")

# ============================================================================
#      HELPER FUNCTIONS
# ============================================================================

def _eagerly_materialize_and_cleanup(pdf: ProphecyDataFrame) -> None:
    pdf.df = pdf.populate_pyspark_df()
    pdf.df.persist()
    pdf.df.count() # trigger action for truly materialize 
    
    close_pdf(pdf)
    
def close_pdf(pdf: ProphecyDataFrame):
    pdf.close_fd()
    pdf.close_data_client()


# ============================================================================
#      SCRIPT GEM - Custom PySpark Transformations
# ============================================================================

def script_gem(
    code: str,
    inputs: Optional[Dict[str, DataFrame]] = None
) -> Dict[str, DataFrame]:

    from pyspark.sql import functions as F
    from pyspark.sql.functions import col, lit, when, sum as spark_sum, avg, count as spark_count
    from pyspark.sql.window import Window
    
    gem_name = _get_caller_name()
    
    # Get the active Spark session
    spark = _get_or_create_prophecy_spark()._spark
    
    # Prepare execution context with common imports
    exec_context = {
        'spark': spark,
        'col': col,
        'lit': lit,
        'when': when,
        'sum': spark_sum,
        'avg': avg,
        'count': spark_count,
        'F': F,
        'Window': Window,
    }
    
    # Keep track of initial variables to identify outputs later
    initial_vars = set(exec_context.keys())
    
    # Extract DataFrames from ProphecyDataFrames and add to execution context
    if inputs:
        for var_name, df in inputs.items():
            if not _is_dataframe(df):
                raise TypeError(f"Input '{var_name}' must be a DataFrame, got {type(df)}")
            
            exec_context[var_name] = df
            initial_vars.add(var_name)  # Track input variables
            logger.info(f"  Input '{var_name}' loaded")
    
    # Execute the custom code
    try:
        logger.info(f"Executing custom code...")
        exec(code, exec_context)
    except Exception as e:
        logger.error(f"Error executing script gem code: {e}")
        raise Exception(f"Error in script gem '{gem_name}': {str(e)}")
    
    # Auto-detect output variables (new variables created by user's code)
    # Look for any new DataFrame variables created during execution
    result_dict = {}
    for var_name, var_value in exec_context.items():
        # Skip initial variables and private/magic variables
        if var_name in initial_vars or var_name.startswith('_'):
            continue
        
        # Check if it's a DataFrame (potential output)
        if _is_dataframe(var_value):
            # Create ProphecyDataFrame for this output
            output_pdf = wf.create_pdf(f"{gem_name}_output_{var_name}")
            output_pdf.df = var_value
            output_pdf.is_pyspark_gem = True
            result_dict[var_name] = output_pdf.df
            logger.info(f"  Detected output '{var_name}'")
    
    if len(result_dict) == 0:
        logger.info(f"Script gem '{gem_name}' produced 0 outputs")
        return {}
    
    logger.info(f"Script gem '{gem_name}' produced {len(result_dict)} outputs: {list(result_dict.keys())}")
    return result_dict


# ============================================================================
#      GO SOURCES
# ============================================================================

def snowflake_read(
    schema: str,
    table: str,
    connection_name: str
) -> DataFrame:
   
    conn = get_connection(connection_name)
    gem_name = _get_caller_name()
    pdf = wf.create_pdf(gem_name)

    from pkg.orchestrator.specs.dataset.source.ui_dialog.snowflake_source_spec import config_transform
    
    config = config_transform(
        process_id=gem_name,
        connection=conn,
        schema=schema,
        table=table
    )
    
    lib.prophecy_read(
        "SnowflakeSource",
        json.dumps(config),
        pdf.data_client_handle
    )
    
    _eagerly_materialize_and_cleanup(pdf)
    
    return pdf.df


def databricks_read(
    user_config: dict,
    connection_name: str
) -> DataFrame:

    conn = get_connection(connection_name)
    gem_name = _get_caller_name()
    pdf = wf.create_pdf(gem_name)

    from pkg.orchestrator.specs.dataset.source.ui_dialog.databricks_source_spec import config_transform

    config = config_transform(
        process_id=gem_name,
        config={"jdbcUrl": conn.get("jdbcUrl"), "token": conn.get("token"), **user_config}
    )

    lib.prophecy_read(
        "DatabricksSource", 
        json.dumps(config), 
        pdf.data_client_handle
    )
    
    _eagerly_materialize_and_cleanup(pdf)

    return pdf.df

def databricks_volume_read(
        user_config: dict,
        connection_name: str
) -> DataFrame:

    conn = get_connection(connection_name)
    gem_name = _get_caller_name()
    pdf = wf.create_pdf(gem_name)
   
    from pkg.orchestrator.specs.dataset.source.ui_dialog.databricks_volume_source_spec import config_transform

    config = config_transform(
        process_id=gem_name,
        config={"jdbcUrl": conn.get("jdbcUrl"), "token": conn.get("token"), **user_config}
    )

    lib.prophecy_read(
        "DatabricksVolumeSource", 
        json.dumps(config), 
        pdf.data_client_handle
    )

    _eagerly_materialize_and_cleanup(pdf)

    return pdf.df

def sftp_read(
        file_path: str,
        file_format: str = "csv",
        connection_name: str = None
) -> DataFrame:
    
    conn = get_connection(connection_name)
    gem_name = _get_caller_name()
    pdf = wf.create_pdf(gem_name)

    from pkg.orchestrator.specs.dataset.source.ui_dialog.sftp_source_spec import config_transform

    config = config_transform(
        process_id=gem_name,
        connection=conn,
        source_path=file_path,
        file_format=file_format
    )

    lib.prophecy_read(
        "SFTPSource",
        json.dumps(config),
        pdf.data_client_handle
    )

    _eagerly_materialize_and_cleanup(pdf)

    return pdf.df


# ============================================================================
#       GO TARGETS
# ============================================================================

def send_email(
    data: DataFrame,
    to: List[str],
    subject: str,
    body: str,
    cc: List[str] = None,
    bcc: List[str] = None,
    file_format: str = "csv",
    file_name: str = "data.csv",
    connection_name: str = None
):
    
    conn = get_connection(connection_name)
    gem_name = _get_caller_name()

    write_pdf = wf.create_pdf(gem_name)    
    write_pdf.df = data
    write_pdf.populate_data_handle()

    from pkg.orchestrator.specs.target.ui_dialog.email import config_transform
    
    config = config_transform(
        process_id=gem_name,
        connection=conn,
        to=to,
        subject=subject,
        body=body,
        cc=cc,
        bcc=bcc,
        include_data=True,
        file_format=file_format,
        file_name=file_name,
    )

    lib.prophecy_write(
        "Email",
        json.dumps(config),
        write_pdf.reader_handles[0]
    )

    close_pdf(write_pdf)
    
    
def databricks_write(
    data: DataFrame,
    user_config: dict,
    connection_name: str
):

    conn = get_connection(connection_name)
    gem_name = _get_caller_name()

    write_pdf = wf.create_pdf(gem_name)
    write_pdf.df = data
    write_pdf.populate_data_handle()

    
    from pkg.orchestrator.specs.dataset.target.ui_dialog.databricks_target_spec import config_transform
    
    config = config_transform(
        process_id=gem_name,
        config={"jdbcUrl": conn.get("jdbcUrl"), "token": conn.get("token"), **user_config}
    )

    lib.prophecy_write(
        "DatabricksTarget", 
        json.dumps(config), 
        write_pdf.reader_handles[0]
    )

    close_pdf(write_pdf)


def databricks_volume_write(
    data: DataFrame,
    user_config: dict,
    connection_name: str
):
    conn = get_connection(connection_name)
    gem_name = _get_caller_name()

    write_pdf = wf.create_pdf(gem_name)
    write_pdf.df = data
    write_pdf.populate_data_handle()

    from pkg.orchestrator.specs.dataset.target.ui_dialog.databricks_volume_target_spec import config_transform
    
    config = config_transform(
        process_id=gem_name,
        config={"jdbcUrl": conn.get("jdbcUrl"), "token": conn.get("token"), **user_config}
    )

    lib.prophecy_write(
        "DatabricksVolumeTarget", 
        json.dumps(config), 
        write_pdf.reader_handles[0]
    )

    close_pdf(write_pdf)

def tableau_write(
    data: DataFrame,
    project_name: str,
    datasource_name: str,
    connection_name: str
):
    conn = get_connection(connection_name)
    gem_name = _get_caller_name()
    
    write_pdf = wf.create_pdf(gem_name)
    write_pdf.df = data
    write_pdf.populate_data_handle()
    
    from pkg.orchestrator.specs.target.ui_dialog.tableau_write import config_transform
    
    config = config_transform(
        process_id=gem_name,
        connection=conn,
        project_name=project_name,
        datasource_name=datasource_name
    )
    
    lib.prophecy_write(
        "TableauWrite", 
        json.dumps(config), 
        write_pdf.reader_handles[0]
    )

    close_pdf(write_pdf)


def sftp_write(
    data: DataFrame,
    file_path: str,
    file_format: str = "csv",
    connection_name: str = None
):
    conn = get_connection(connection_name)
    gem_name = _get_caller_name()
    
    write_pdf = wf.create_pdf(gem_name)
    write_pdf.df = data
    write_pdf.populate_data_handle()
    
    from pkg.orchestrator.specs.dataset.target.ui_dialog.sftp_target_spec import config_transform
    
    config = config_transform(
        process_id=gem_name,
        connection=conn,
        target_path=file_path,
        file_format=file_format
    )
    
    lib.prophecy_write(
        "SFTPTarget",
        json.dumps(config),
        write_pdf.reader_handles[0]
    )
    
    close_pdf(write_pdf)


# ============================================================================
# REST API
# ============================================================================

def rest_api_call(
    data: Optional[DataFrame] = None,
    url: str = None,
    method: str = "GET",
    body: Optional[str] = None,
    params: Optional[List[Dict[str, str]]] = None,
    headers: Optional[List[Dict[str, str]]] = None,
    target_column_name: str = "api_response",
    parse_api_response: bool = True,
    auth_type: str = "none",
    credentials: Optional[Dict[str, Any]] = None
) -> DataFrame:
    gem_name = _get_caller_name()
    
    from pkg.orchestrator.specs.transformation.ui_dialog.rest_api import config_transform
    
    config = config_transform(
        process_id=gem_name,
        url=url,
        method=method,
        body=body,
        params=params,
        headers=headers,
        target_column_name=target_column_name,
        parse_api_response=parse_api_response,
        auth_type=auth_type,
        credentials=credentials
    )
    
    # REST API gem can work both as transformation (with input) or source (without input)
    if data is not None:
        # Transformation mode: has input data
        # Create output PDF
        output_pdf = wf.create_pdf(gem_name)
        
        # Create write PDF for input
        write_pdf = wf.create_pdf(f"{gem_name}_input")
        write_pdf.df = data
        write_pdf.populate_data_handle()
        
        # Execute REST API gem with input using ProphecyTransform
        lib.prophecy_transform(
            "RestAPI",
            json.dumps(config),
            write_pdf.reader_handles[0],
            output_pdf.data_client_handle
        )
        
        # Materialize output first, then close input
        _eagerly_materialize_and_cleanup(output_pdf)
        close_pdf(write_pdf)
        
        return output_pdf.df
    else:
        # Source mode: no input data (pure GET request)
        pdf = wf.create_pdf(gem_name)
        
        lib.prophecy_read(
            "RestAPI",
            json.dumps(config),
            pdf.data_client_handle
        )
        
        _eagerly_materialize_and_cleanup(pdf)
        
        return pdf.df
