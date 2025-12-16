from typing import Dict, Any

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
        .addElement(uispec.ConfigText("File Path").bindPlaceholder("Enter File Path").bindProperty("properties.filePath")) \
        .addElement(uispec.Condition().ifEqual(uispec.PropExpr("component.properties.format.kind"), uispec.StringExpr("xml")).then(uispec.StackLayout(gap="1rem")
                    .addElement(uispec.Switch("Enable XSD Schema Validation").bindProperty("properties.fileOperationProperties.enableXSDValidation")) \
                    .addElement(uispec.Condition().ifEqual(uispec.PropExpr("component.properties.properties.fileOperationProperties.enableXSDValidation"), uispec.BooleanExpr(True)).then(uispec.StackLayout(gap="1rem", width="100%").addElement(uispec.ConfigText("XSD Schema File Path").bindPlaceholder("Enter the path to the XSD schema file").bindProperty("properties.fileOperationProperties.xsdFilePath")))) \
                    )) \
        .addElement(uispec.Condition().ifEqual(uispec.PropExpr("component.properties.format.kind"), uispec.StringExpr("json")).then(uispec.StackLayout(gap="1rem")
                    .addElement(uispec.Switch("Enable JSON Schema Validation").bindProperty("properties.fileOperationProperties.enableJSONSchemaValidation")) \
                    .addElement(uispec.Condition().ifEqual(uispec.PropExpr("component.properties.properties.fileOperationProperties.enableJSONSchemaValidation"), uispec.BooleanExpr(True)).then(uispec.StackLayout(gap="1rem", width="100%").addElement(uispec.ConfigText("JSON Schema File Path").bindPlaceholder("Enter the path to the JSON schema file").bindProperty("properties.fileOperationProperties.jsonSchemaFilePath")))) \
                    ))
    return SpecBox(stack, "LOCATION")


def config_transform(
    process_id: str,
    config: Dict[str, Any],
) -> Dict[str, Any]:
    
    jdbc_url = config.get("jdbcUrl")
    token = config.get("token")
    catalog = config.get("catalog")
    file_path = config.get("filePath")
    file_format = config.get("fileFormat", "csv")
    
    # Validate required fields
    missing_fields = []
    if not jdbc_url:
        missing_fields.append("jdbcUrl")
    if not token:
        missing_fields.append("token")
    if not file_path:
        missing_fields.append("filePath")
    
    if missing_fields:
        raise ValueError(
            f"Missing required fields: {', '.join(missing_fields)}"
        )
    
    # Ensure file path starts with /Volumes
    if not file_path.startswith("/Volumes"):
        file_path = "/Volumes" + file_path.lstrip("/")
    
    return {
        "gemName": "DatabricksVolumeSource",
        "processId": process_id,
        "config": {
            "properties": {
                "filePath": file_path
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
                    "catalog": catalog
                }
            },
            "format": {
                "kind": file_format,
                "properties": {}
            }
        }
    }

def applyPython(self, spark: SparkSession) -> DataFrame:
    out = prophecy.read.databricks_volume(
        file_path = self.props.properties.filePath,
        file_format = self.props.format.kind,
        connection_name = self.props.connector.id
    )
    return out
