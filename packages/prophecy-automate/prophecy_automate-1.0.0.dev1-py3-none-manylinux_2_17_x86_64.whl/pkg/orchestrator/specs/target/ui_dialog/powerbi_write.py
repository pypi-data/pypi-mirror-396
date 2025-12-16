from prophecy.cb.server.base.ComponentBuilderBase import *
from prophecy.cb.ui.uispec import *

def dialog() -> Dialog:
    connection = ConnectionDropdown("powerbi", "PowerBI Connection").bindProperty("connection").bindPlaceholder("PowerBI Token").bindConnectionKind("powerbi")

    return Dialog("PowerBI").addElement(
        ColumnsLayout(gap="1rem", height="100%")
        .addColumn(Ports(allowCustomOutputSchema=False,allowInputAddOrDelete=True), "content")
        .addColumn(
            StackLayout(height="100%")
            .addElement(connection)
            .addElement(TextBox("Workspace Name").bindPlaceholder("MyWorkspace").bindProperty("workspaceName"))
            .addElement(
                RadioGroup("Create New or Use Existing Dataset")
                    .addOption("Dataset Name", "datasetName",
                                description=(
                                    "Select this option to create a brand-new dataset using the name you enter. If a dataset with that name already exists, Power BI will still create a new dataset with the same display name but assign it a unique internal ID. Once you’ve written to this dataset and its tables have been created, subsequent writes can only update or overwrite those existing tables—you cannot add new tables to the dataset under this option."))
                    .addOption("Dataset ID", "datasetID",
                                description="Select this option to update an existing dataset—simply enter its dataset ID. All subsequent write operations will connect to that dataset and will only update or overwrite the tables you’ve already created there; no new tables can be added under this option."
                                )
                    .setOptionType("button")
                    .setVariant("medium")
                    .setButtonStyle("solid")
                    .bindProperty("datasetType")
            )
            .addElement(
                Condition()
                    .ifEqual(PropExpr("component.properties.datasetType"), StringExpr("datasetName"))
                    .then(
                        TextBox("Dataset Name").bindPlaceholder("Finance").bindProperty("datasetName")
                    )
                    .otherwise(
                        TextBox("Dataset ID").bindPlaceholder("224679f8-6a7a-4457-a328-96184775fe65").bindProperty("datasetID")                                    
                    )                
                )
            .addElement(TitleElement(title="Table Write Configuration"))
            .addElement(
                Condition()
                    .ifEqual(PropExpr("component.properties.datasetType"), StringExpr("datasetName"))
                    .then(
                        StackLayout(height=("100%"))
                                .addElement(BasicTable(
                                    "Dataset Tables",
                                    height="200px",
                                    columns=[
                                        Column("Input Alias", "inputAlias", width="50%"),
                                        Column("Table Name", "tableName", TextBox("").bindPlaceholder("table_name"), width="50%")
                                    ],
                                delete=False,
                                appendNewRow=False,
                                ).bindProperty("datasetTables")
                            )
                    )
                    .otherwise(
                        StackLayout(height=("100%"))
                                .addElement(BasicTable(
                                    "Dataset Tables",
                                    height="200px",
                                    columns=[
                                        Column("Input Alias", "inputAlias", width="25%"),
                                        Column("Table Name", "tableName", TextBox("").bindPlaceholder("table_name"), width="25%"),
                                        Column("Write Mode", "writeMode",
                                            (SelectBox("")
                                                .addOption("Overwrite", "overwrite")
                                                .addOption("Append", "append")
                                                ), width="25%"
                                            ),
                                        Column("Overwrite Schema", "overwriteSchema", 
                                               (SelectBox("")
                                                .addOption("Yes", "Yes")
                                                .addOption("No", "No")
                                                ), width="25%")
                                    ],
                                delete=False,
                                appendNewRow=False,
                                ).bindProperty("datasetTables")
                            )                                 
                    )  
            ),            
            "5fr"
        )
    )