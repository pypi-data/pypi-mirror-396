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
            .addElement(ConfigText("Database").bindPlaceholder("Enter Database Name").bindProperty("properties.tableFullName.database"))\
            .addElement(ConfigText("Schema").bindPlaceholder("Enter Schema Name").bindProperty("properties.tableFullName.schema"))\
            .addElement(ConfigText("Name").bindPlaceholder("Enter Table Name").bindProperty("properties.tableFullName.name"))
    return SpecBox(stack, "LOCATION")
