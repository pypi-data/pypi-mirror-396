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
    stack =  StackLayout(height="100%") \
                            .addElement(
                                RadioGroup("Data Source")
                                    .addOption("SAQL", "saql",
                                                description=(
                                                    "Run a SAQL query against Wave datasets."))
                                    .addOption("SOQL", "soql",
                                                description="Run a Salesforce SOQL query against org’s objects. This mode reads live records by default, and can retrieve deleted/archived rows if Query All is enabled, enable Bulk Query for maximum performance."
                                                )
                                    .addOption("Salesforce Object", "sfobj",
                                                description="Specify the API name of a Salesforce sObject (e.g., Account, Contact) to read all its records and fields. For large data volumes, enable Bulk Query for maximum performance."
                                                )
                                    .setOptionType("button")
                                    .setVariant("medium")
                                    .setButtonStyle("solid")
                                    .bindProperty("component.properties.properties.readFromSource")
                            ) \
                            .addElement(
                                Condition()
                                    .ifEqual(
                                    PropExpr("component.properties.properties.readFromSource"),
                                    StringExpr("saql"),
                                )
                                    .then(
                                        TextArea("SAQL query to query Salesforce Wave", 10, placeholder="q = load 'OpsDates1';").bindProperty("component.properties.properties.saql")
                                )
                            ) \
                            .addElement(
                                Condition()
                                    .ifEqual(
                                    PropExpr("component.properties.properties.readFromSource"),
                                    StringExpr("soql"),
                                )
                                    .then(
                                        TextArea("SOQL query to query Salesforce Object", 10, placeholder="SELECT Name FROM Account").bindProperty("component.properties.properties.soql")
                                )
                            ) \
                            .addElement(
                                Condition()
                                    .ifEqual(
                                    PropExpr("component.properties.properties.readFromSource"),
                                    StringExpr("sfobj"),
                                )
                                    .then(
                                        TextBox("Query Salesforce Object").bindPlaceholder("Account").bindProperty("component.properties.properties.sfobj")
                                )
                            )
    return SpecBox(stack, "LOCATION")