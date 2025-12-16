from typing import Dict, Any

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
        stack = StackLayout(height="100%") \
            .addElement(ConfigText("File Path").bindPlaceholder("Enter File Path").bindProperty("properties.filePath"))
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
    file_path = config.get("filePath")
    file_format = config.get("fileFormat", "csv")
    write_mode = config.get("writeMode", "overwrite")
    
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
        "gemName": "DatabricksVolumeTarget",
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
                "properties": {
                    "writeMode": write_mode
                }
            }
        }
    }

def applyPython(self, spark: SparkSession, in0: DataFrame):
    prophecy.write.databricks_volume(
        data=in0,
        file_path = self.props.properties.filePath,
        file_format = self.props.format.kind,
        write_mode = self.props.format.properties.writeMode,
        connection_name = self.props.connector.id
    )
