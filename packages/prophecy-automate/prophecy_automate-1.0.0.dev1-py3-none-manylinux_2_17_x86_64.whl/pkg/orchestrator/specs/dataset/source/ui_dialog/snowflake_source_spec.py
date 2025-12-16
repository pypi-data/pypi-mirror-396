from typing import Dict, Any, Optional

from pyspark.sql import SparkSession
from pyspark.sql import DataFrame

def dialog():
    # Import UI dependencies only when generating UI
    import prophecy.cb.ui.uispec as uispec

    class SpecBox():
        spec: 'uispec.Atom'
        id: str
        title: str
        def __init__(self, spec, title: str):
            self.spec = spec
            self.title = title
            self.id = uispec.UISpec().getId()
        def json(self):
            return {
                "spec": self.spec.json(),
                "id": self.id,
                "title": self.title
            }

    stack = uispec.StackLayout(height="100%") \
        .addElement(uispec.ConfigText("Database").bindPlaceholder("Enter Database Name").bindProperty("properties.tableFullName.database")) \
        .addElement(uispec.ConfigText("Schema").bindPlaceholder("Enter Schema Name").bindProperty("properties.tableFullName.schema")) \
        .addElement(uispec.ConfigText("Name").bindPlaceholder("Enter Table Name").bindProperty("properties.tableFullName.name"))
    return SpecBox(stack, "LOCATION")

def config_transform(
        process_id: str,
        connection: Dict[str, Any],
        schema: str,
        table: str,
) -> Dict[str, Any]:

    account = connection.get("account")
    username = connection.get("username")
    password = connection.get("password")
    database = connection.get("database")
    warehouse = connection.get("warehouse")

    # Validate required fields
    missing_fields = []
    if not account:
        missing_fields.append("account")
    if not username:
        missing_fields.append("username")
    if not password:
        missing_fields.append("password")
    if not database:
        missing_fields.append("database")
    if not warehouse:
        missing_fields.append("warehouse")

    if missing_fields:
        raise ValueError(
            f"Missing required fields in connection: {', '.join(missing_fields)}"
        )

    # Extract optional fields
    role = connection.get("role", "ACCOUNTADMIN")

    return {
        "gemName": "SnowflakeSource",
        "processId": process_id,
        "config": {
            "properties": {
                "tableFullName": {
                    "database": database,
                    "schema": schema,
                    "name": table
                }
            },
            "connector": {
                "kind": "snowflake",
                "properties": {
                    "account": account,
                    "username": username,
                    "password": {
                        "kind": "plain",
                        "properties": {
                            "scope": "project",
                            "value": password
                        }
                    },
                    "database": database,
                    "schema": schema,
                    "warehouse": warehouse,
                    "role": role
                }
            },
            "format": {
                "kind": "snowflake",
                "properties": {}
            }
        }
    }

def applyPython(self, spark: SparkSession) -> DataFrame:
    out = prophecy.read.snowflake(
        schema = self.props.properties.tableFullName.schema,
        table = self.props.properties.tableFullName.name,
        connection_name = self.props.connector.id
    )
    
    # UISpecProperties
    # {}_connector.go for connector id
    
    return out
