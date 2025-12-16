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
    stack = StackLayout(height="100%")\
            .addElement(ConfigText("Schema").bindPlaceholder("Enter Schema Name").bindProperty("properties.tableFullName.schema"))\
            .addElement(ConfigText("Name").bindPlaceholder("Enter Table Name").bindProperty("properties.tableFullName.name"))\
            .addElement(TextBox("Query (It will take precedence over other properties)")\
                .bindPlaceholder("SELECT COL_CHAR, COL_NCHAR FROM CHAR_TYPES_EXAMPLE")\
                .bindProperty("properties.warehouseQuery.query"))
    return SpecBox(stack, "LOCATION")