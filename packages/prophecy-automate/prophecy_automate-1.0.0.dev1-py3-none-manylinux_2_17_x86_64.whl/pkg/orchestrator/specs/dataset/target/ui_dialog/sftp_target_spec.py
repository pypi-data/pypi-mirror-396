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
    
    stack = uispec.StackLayout(height="100%").addElement(uispec.ConfigText("File path").bindPlaceholder("Enter File Path").bindProperty("properties.filePath"))
    return SpecBox(stack, "LOCATION")


def config_transform(
    process_id: str,
    connection: Dict[str, Any],
    target_path: str,
    file_format: str = "csv",
) -> Dict[str, Any]:
    
    host = connection.get("host")
    port = connection.get("port")
    username = connection.get("username")
    password = connection.get("password")
    private_key = connection.get("privateKey")
    
    # Validate required fields
    missing_fields = []
    if not host:
        missing_fields.append("host")
    if not port:
        missing_fields.append("port")
    if not username:
        missing_fields.append("username")
    if not password and not private_key:
        missing_fields.append("password or privateKey")
    
    if missing_fields:
        raise ValueError(
            f"Missing required fields in connection: {', '.join(missing_fields)}"
        )
    
    auth_method = "private_key" if private_key else "password"
    
    connector_props = {
        "host": host,
        "port": port,
        "authMethod": auth_method,
        "username": username,
    }
    
    if private_key:
        connector_props["privateKey"] = private_key
    else:
        connector_props["password"] = {
            "kind": "plain",
            "properties": {
                "scope": "project",
                "value": password
            }
        }
    
    return {
        "gemName": "SFTPTarget",
        "processId": process_id,
        "config": {
            "properties": {
                "filePath": target_path
            },
            "connector": {
                "kind": "sftp",
                "properties": connector_props
            },
            "format": {
                "kind": file_format,
                "properties": {}
            }
        }
    }

def applyPython(self, spark: SparkSession, in0: DataFrame):
    prophecy.write.sftp(
        data=in0,
        file_path = self.props.properties.filePath,
        file_format = self.props.format.kind,
        connection_name = self.props.connector.id
    )
