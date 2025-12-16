from typing import Dict, Any, Optional

from pyspark.sql import SparkSession
from pyspark.sql import DataFrame

# UI imports (optional - only needed for dialog() function)
try:
    from prophecy.cb.ui.uispec import *
    _UI_AVAILABLE = True
    
    class SpecBox():
        spec: Atom
        id: str
        title: str
        def __init__(self, spec: Atom, title: str):
            self.spec = spec
            self.title = title
            self.id = UISpec().getId()
        def json(self):
            return {
                "spec": self.spec.json(),
                "id": self.id,
                "title": self.title
            }
    
    def dialog() -> Dialog:
        stack = StackLayout(height="100%")\
                .addElement(ConfigText("Catalog").bindPlaceholder("Enter Catalog Name").bindProperty("properties.tableFullName.database"))\
                .addElement(ConfigText("Schema").bindPlaceholder("Enter Schema Name").bindProperty("properties.tableFullName.schema"))\
                .addElement(ConfigText("Name").bindPlaceholder("Enter Table Name").bindProperty("properties.tableFullName.name"))
        return SpecBox(stack, "LOCATION")
    
except ImportError:
    _UI_AVAILABLE = False
    def dialog():
        raise ImportError("prophecy.cb.ui.uispec not available - dialog() requires UI framework")


def config_transform(
    process_id: str,
    config: Dict[str, Any],
) -> Dict[str, Any]:
    
    jdbc_url = config.get("jdbcUrl")
    token = config.get("token")
    catalog = config.get("catalog")
    schema = config.get("schema")
    table = config.get("table")
    write_mode = config.get("writeMode", "overwrite")
    
    # Validate required fields
    missing_fields = []
    if not jdbc_url:
        missing_fields.append("jdbcUrl")
    if not token:
        missing_fields.append("token")
    if not catalog:
        missing_fields.append("catalog")
    if not schema:
        missing_fields.append("schema")
    if not table:
        missing_fields.append("table")
    
    if missing_fields:
        raise ValueError(
            f"Missing required fields: {', '.join(missing_fields)}"
        )
    
    return {
        "gemName": "DatabricksTarget",
        "processId": process_id,
        "config": {
            "properties": {
                "tableFullName": {
                    "database": catalog,
                    "schema": schema,
                    "name": table
                }
            },
            "connector": {
                "kind": "databricks",
                "properties": {
                    "jdbcUrl": jdbc_url,
                    "token": {
                        "kind": "plain",
                        "properties": {
                            "scope": "project",
                            "value": token
                        }
                    },
                    "catalog": catalog,
                    "schema": schema
                }
            },
            "format": {
                "kind": "databricks",
                "properties": {
                    "writeMode": write_mode
                }
            }
        }
    }

def applyPython(self, spark: SparkSession, in0: DataFrame):
    prophecy.write.databricks(
        data=in0,
        catalog = self.props.properties.tableFullName.database,
        schema = self.props.properties.tableFullName.schema,
        table = self.props.properties.tableFullName.name,
        write_mode = self.props.format.properties.writeMode,
        connection_name = self.props.connector.id
    )
