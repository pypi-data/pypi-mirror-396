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
    tableFullNameDialog = (StackLayout(direction=("vertical"), gap=("1rem"))
                        .addElement(
                            ConfigText("Schema")
                                .bindPlaceholder("Enter Schema Name")
                                .bindProperty("properties.tableFullName.schema")
                        )
                        .addElement(
                            ConfigText("Name")
                                .bindPlaceholder("Enter Table Name")
                                .bindProperty("properties.tableFullName.name")
                        )
                    )
    warehouseQueryDialog = (StackLayout(direction=("vertical"), gap=("1rem"))
                        .addElement(
                            TextArea("Query", 10, placeholder="SELECT a, b FROM TWEET").bindProperty("properties.warehouseQuery.query")
                        )
                    )

    locationSelection = (SelectBox("Read Using")
                         .addOption("Table", "tableFullName")
                         .addOption("Query", "warehouseQuery")
                         .bindProperty("properties.pathSelection"))

    stack = (StackLayout().addElement(locationSelection)
        .addElement(
            Condition()
                .ifEqual(PropExpr("component.properties.properties.pathSelection"), StringExpr("warehouseQuery"))
                .then(warehouseQueryDialog)
                .otherwise(tableFullNameDialog)
        )
    )
    return SpecBox(stack, "LOCATION")
