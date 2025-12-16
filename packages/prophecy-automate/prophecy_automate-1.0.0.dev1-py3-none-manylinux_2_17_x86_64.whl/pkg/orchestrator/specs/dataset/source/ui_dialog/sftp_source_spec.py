from typing import Dict, Any

from pyspark.sql import SparkSession
from pyspark.sql import DataFrame

def dialog():

    import prophecy.cb.ui.uispec as uispec

    class SpecBox():
        spec: uispec.Atom
        id: str
        title: str
        def __init__(self, spec: uispec.Atom, title: str):
            self.spec = spec
            self.title = title
            self.id = uispec.UISpec().getId()
        def json(self):
            return {
                "spec": self.spec.json(),
                "id": self.id,
                "title": self.title
            }


    stack = uispec.StackLayout(gap="32px") \
        .addElement(uispec.StackLayout(width="320px").addElement(uispec.SelectBox("Choose Path or Configuration").addOption("File Path", "filepath").addOption("Configuration", "configuration").withDefault("filepath").bindProperty("properties.fileOperationProperties.fileLoadingType"))) \
        .addElement(uispec.StackLayout(width="50%").addElement(uispec.Condition().ifEqual(uispec.PropExpr("component.properties.properties.fileOperationProperties.fileLoadingType"), uispec.StringExpr("configuration")).then(uispec.FileTriggerConfigurationSelector("Select Configuration", "${component.properties.connector.properties.id}").bindProperty("properties.fileOperationProperties.configurationName")).otherwise(uispec.ConfigText("File Path").bindPlaceholder("Enter File Path").bindProperty("properties.filePath")))) \
        .addElement(uispec.StackLayout(gap="16px") \
                    .addElement(uispec.Switch("Include filename Column").withToolTip("Adds a filename column to track the provenance of each row delivered.").bindProperty("properties.fileOperationProperties.includeFileNameColumn")) \
                    .addElement(uispec.Switch("Delete files after successfully processed").withToolTip("Deletes files from the SFTP server after all its rows have been successfully processed.").bindProperty("properties.fileOperationProperties.deleteFilesAfterProcessing")) \
                    .addElement(uispec.StackLayout(gap="8px")
                                .addElement(uispec.Switch("Move files after successfully processed").withToolTip("Move files from the SFTP server after all its rows have been successfully processed.").bindProperty("properties.fileOperationProperties.moveFilesToDestinationFolder")) \
                                .addElement(uispec.Condition().ifEqual(uispec.PropExpr("component.properties.properties.fileOperationProperties.moveFilesToDestinationFolder"), uispec.BooleanExpr(True)).then(uispec.StackLayout(width="50%", padding="0 0 0 50px").addElement(uispec.ConfigText("Move File Directory").bindPlaceholder("Enter Directory Path").bindProperty("properties.fileOperationProperties.destinationFolderPath")))) \
                                ) \
                    .addElement(uispec.Condition().ifEqual(uispec.PropExpr("component.properties.format.kind"), uispec.StringExpr("xml")).then(uispec.StackLayout(gap="1rem")
                                .addElement(uispec.Switch("Enable XSD Schema Validation").bindProperty("properties.fileOperationProperties.enableXSDValidation")) \
                                .addElement(uispec.Condition().ifEqual(uispec.PropExpr("component.properties.properties.fileOperationProperties.enableXSDValidation"), uispec.BooleanExpr(True)).then(uispec.StackLayout(gap="1rem", width="100%").addElement(uispec.ConfigText("XSD Schema File Path").bindPlaceholder("Enter the path to the XSD schema file").bindProperty("properties.fileOperationProperties.xsdFilePath")))) \
                                )) \
                    .addElement(uispec.Condition().ifEqual(uispec.PropExpr("component.properties.format.kind"), uispec.StringExpr("json")).then(uispec.StackLayout(gap="1rem")
                                .addElement(uispec.Switch("Enable JSON Schema Validation").bindProperty("properties.fileOperationProperties.enableJSONSchemaValidation")) \
                                .addElement(uispec.Condition().ifEqual(uispec.PropExpr("component.properties.properties.fileOperationProperties.enableJSONSchemaValidation"), uispec.BooleanExpr(True)).then(uispec.StackLayout(gap="1rem", width="100%").addElement(uispec.ConfigText("JSON Schema File Path").bindPlaceholder("Enter the path to the JSON schema file").bindProperty("properties.fileOperationProperties.jsonSchemaFilePath")))) \
                                ))
        )
    return SpecBox(stack, "LOCATION")


def config_transform(
    process_id: str,
    connection: dict,
    source_path: str,
    file_format: str = "csv",
) -> dict:
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
        "gemName": "SFTPSource",
        "processId": process_id,
        "config": {
            "properties": {
                "filePath": source_path,
                "fileOperationProperties": {
                    "fileLoadingType": "filepath",
                    "includeFileNameColumn": False,
                    "deleteFilesAfterProcessing": False,
                    "moveFilesToDestinationFolder": False
                }
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

def applyPython(self, spark: SparkSession) -> DataFrame:
    out = prophecy.read.sftp(
        file_path = self.props.properties.filePath,
        file_format = self.props.format.kind,
        connection_name = self.props.connector.id
    )
    return out
