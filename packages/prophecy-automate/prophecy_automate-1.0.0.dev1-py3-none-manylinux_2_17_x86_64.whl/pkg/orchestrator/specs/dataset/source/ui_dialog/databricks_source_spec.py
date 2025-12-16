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
        .addElement(uispec.ConfigText("Catalog").bindPlaceholder("Enter Catalog Name").bindProperty("properties.tableFullName.database")) \
        .addElement(uispec.ConfigText("Schema").bindPlaceholder("Enter Schema Name").bindProperty("properties.tableFullName.schema")) \
        .addElement(uispec.ConfigText("Name").bindPlaceholder("Enter Table Name").bindProperty("properties.tableFullName.name"))
    return SpecBox(stack, "LOCATION")

def config_transform(
    process_id: str,
    config: Dict[str, Any],
) -> Dict[str, Any]:
    
    jdbc_url = config.get("jdbcUrl")
    token = config.get("token")
    catalog = config.get("catalog")
    schema = config.get("schema")
    table = config.get("table")
    
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
        "gemName": "DatabricksSource",
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
                "properties": {}
            }
        }
    }

def applyPython(self, spark: SparkSession) -> DataFrame:
    out = prophecy.read.databricks(
        catalog = self.props.properties.tableFullName.database,
        schema = self.props.properties.tableFullName.schema,
        table = self.props.properties.tableFullName.name,
        connection_name = self.props.connector.id
    )
    return out
