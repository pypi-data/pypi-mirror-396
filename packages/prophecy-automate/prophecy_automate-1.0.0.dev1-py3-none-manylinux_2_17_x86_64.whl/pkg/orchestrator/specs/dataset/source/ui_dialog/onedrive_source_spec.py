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
    stack = StackLayout(height="100%") \
        .addElement(ConfigText("File path").bindPlaceholder("/landing-zn/test.csv").bindProperty("properties.filePath")) \
        .addElement(Condition().ifEqual(PropExpr("component.properties.format.kind"), StringExpr("xml")).then(StackLayout(gap="1rem")
                    .addElement(Switch("Enable XSD Schema Validation").bindProperty("properties.fileOperationProperties.enableXSDValidation")) \
                    .addElement(Condition().ifEqual(PropExpr("component.properties.properties.fileOperationProperties.enableXSDValidation"), BooleanExpr(True)).then(StackLayout(gap="1rem", width="100%").addElement(ConfigText("XSD Schema File Path").bindPlaceholder("Enter the path to the XSD schema file").bindProperty("properties.fileOperationProperties.xsdFilePath")))) \
                    )) \
        .addElement(Condition().ifEqual(PropExpr("component.properties.format.kind"), StringExpr("json")).then(StackLayout(gap="1rem")
                    .addElement(Switch("Enable JSON Schema Validation").bindProperty("properties.fileOperationProperties.enableJSONSchemaValidation")) \
                    .addElement(Condition().ifEqual(PropExpr("component.properties.properties.fileOperationProperties.enableJSONSchemaValidation"), BooleanExpr(True)).then(StackLayout(gap="1rem", width="100%").addElement(ConfigText("JSON Schema File Path").bindPlaceholder("Enter the path to the JSON schema file").bindProperty("properties.fileOperationProperties.jsonSchemaFilePath")))) \
                    ))
    return SpecBox(stack, "LOCATION")