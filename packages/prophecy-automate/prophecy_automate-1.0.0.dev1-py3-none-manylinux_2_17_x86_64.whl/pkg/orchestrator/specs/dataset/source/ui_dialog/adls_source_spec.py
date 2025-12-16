from prophecy.cb.ui.uispec import *


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
    stack = StackLayout(gap="32px") \
        .addElement(StackLayout(width="320px").addElement(SelectBox("Choose Path or Configuration").addOption("File Path", "filepath").addOption("Configuration", "configuration").withDefault("filepath").bindProperty("properties.fileOperationProperties.fileLoadingType"))) \
        .addElement(StackLayout(width="50%").addElement(Condition().ifEqual(PropExpr("component.properties.properties.fileOperationProperties.fileLoadingType"), StringExpr("configuration")).then(FileTriggerConfigurationSelector("Select Configuration", "${component.properties.connector.properties.id}").bindProperty("properties.fileOperationProperties.configurationName")).otherwise(StackLayout(gap="0.5rem")
                                                                                                                                                                                                                                                                                           .addElement(ConfigText("File Path").bindPlaceholder("Enter File Path").bindProperty("properties.filePath"))
                                                                                                                                                                                                                                                                                           .addElement(Switch("Recursive").bindProperty("properties.recursive"))
                                                                                                                                                                                                                                                                                           .addElement(Condition().ifEqual(PropExpr("component.properties.properties.recursive"), BooleanExpr(True)).then(ConfigText("Recursive File Extension").bindPlaceholder("Enter file extension (e.g. csv)").bindProperty("properties.recursiveFileExtension")))))) \
        .addElement(StackLayout(gap="16px") \
                    .addElement(Switch("Include filename Column").withToolTip("Adds a filename column to track the provenance of each row delivered.").bindProperty("properties.fileOperationProperties.includeFileNameColumn")) \
                    .addElement(Switch("Delete files after successfully processed").withToolTip("Deletes files from the ADLS server after all its rows have been successfully processed.").bindProperty("properties.fileOperationProperties.deleteFilesAfterProcessing")) \
                    .addElement(StackLayout(gap="8px")
                                .addElement(Switch("Move files after successfully processed").withToolTip("Move files from the ADLS server after all its rows have been successfully processed.").bindProperty("properties.fileOperationProperties.moveFilesToDestinationFolder")) \
                                .addElement(Condition().ifEqual(PropExpr("component.properties.properties.fileOperationProperties.moveFilesToDestinationFolder"), BooleanExpr(True)).then(StackLayout(width="50%", padding="0 0 0 50px").addElement(ConfigText("Move File Directory").bindPlaceholder("Enter Directory Path").bindProperty("properties.fileOperationProperties.destinationFolderPath")))) \
                                ) \
                    .addElement(Condition().ifEqual(PropExpr("component.properties.format.kind"), StringExpr("xml")).then(StackLayout(gap="1rem")
                                .addElement(Switch("Enable XSD Schema Validation").bindProperty("properties.fileOperationProperties.enableXSDValidation")) \
                                .addElement(Condition().ifEqual(PropExpr("component.properties.properties.fileOperationProperties.enableXSDValidation"), BooleanExpr(True)).then(StackLayout(gap="1rem", width="100%").addElement(ConfigText("XSD Schema File Path").bindPlaceholder("Enter the path to the XSD schema file").bindProperty("properties.fileOperationProperties.xsdFilePath")))) \
                                )) \
                    .addElement(Condition().ifEqual(PropExpr("component.properties.format.kind"), StringExpr("json")).then(StackLayout(gap="1rem")
                                .addElement(Switch("Enable JSON Schema Validation").bindProperty("properties.fileOperationProperties.enableJSONSchemaValidation")) \
                                .addElement(Condition().ifEqual(PropExpr("component.properties.properties.fileOperationProperties.enableJSONSchemaValidation"), BooleanExpr(True)).then(StackLayout(gap="1rem", width="100%").addElement(ConfigText("JSON Schema File Path").bindPlaceholder("Enter the path to the JSON schema file").bindProperty("properties.fileOperationProperties.jsonSchemaFilePath")))) \
                                ))
        )
    return SpecBox(stack, "LOCATION")
