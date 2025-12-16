from prophecy.cb.server.base.ComponentBuilderBase import *
from prophecy.cb.ui.uispec import *

def dialog() -> Dialog:
    # please edit the json generated to account for
    return Dialog("Model").addElement(
            ColumnsLayout(gap="1rem", height="100%")
            .addColumn(Ports(),"content")
            .addColumn(
                StackLayout(height="100%")
                .addElement(
                    SelectBox("Select Read Options")
                    .bindProperty("readOptions")
                    .addOption("Modify SQL Query", "modifySQLQuery")
                    .addOption("Dynamically read data from multiple files", "dynamicReadFiles")
                    .withDefault("modifySQLQuery")
                )
                .addElement(
                    Condition()
                        .ifEqual(PropExpr("component.properties.readOptions"), StringExpr("modifySQLQuery"))
                        .then(
                        StackLayout()
                        .addElement(
                            SelectBox("Table Connection Type")
                            .bindProperty("tableIntegration")
                            .addOption("Oracle", "oracle")
                            .addOption("MSSQL", "mssql")
                            .addOption("Azure Synapse", "synapse")
                        )
                        .addElement(
                            (
                                Condition()
                                .ifEqual(PropExpr("component.properties.tableIntegration"), StringExpr("oracle"))
                            ).then(
                                StackLayout(height="100%")
                                .addElement(
                                    ConnectionDropdown("oracle", "Oracle Connection")
                                        .bindProperty("tableConnector")
                                        .bindPlaceholder("Oracle Connection")
                                        .bindConnectionKind("oracle")                                    
                                )                                                              
                            )
                        )
                        .addElement(
                            (
                                Condition()
                                .ifEqual(PropExpr("component.properties.tableIntegration"), StringExpr("mssql"))
                            ).then(
                                StackLayout(height="100%")
                                .addElement(
                                    ConnectionDropdown("mssql", "MSSQL Connection")
                                        .bindProperty("tableConnector")
                                        .bindPlaceholder("MSSQL Connection")
                                        .bindConnectionKind("mssql")                                    
                                )                                                              
                            )
                        )
                        .addElement(
                            (
                                Condition()
                                .ifEqual(PropExpr("component.properties.tableIntegration"), StringExpr("synapse"))
                            ).then(
                                StackLayout(height="100%")
                                .addElement(
                                    ConnectionDropdown("synapse", "Azure Synapse Connection")
                                        .bindProperty("tableConnector")
                                        .bindPlaceholder("Azure Synapse Connection")
                                        .bindConnectionKind("synapse")                                    
                                )                                                              
                            )
                        )
                        .addElement(
                            NativeText("Input Data Source Template")
                        )
                        .addElement(
                            StepContainer()
                                .addElement(
                                    Step()
                                        .addElement(
                                            StackLayout()
                                            .addElement(TitleElement("Table or Query"))
                                            .addElement(
                                                ExpressionBox(language="sql")
                                                .bindProperty("sqlQuery")
                                                .bindPlaceholder("Enter the SQL query")
                                            )                                            
                                        )
                                )
                        )
                        .addElement(
                            StepContainer()
                                .addElement(
                                    Step()                                   
                                        .addElement(
                                            StackLayout()
                                                .addElement(TitleElement(""))
                                                .addElement(TitleElement("Replace a Specific String"))
                                                .addElement(
                                                    BasicTable(
                                                        "Unique Values",
                                                        height="300px",
                                                        columns=[
                                                            Column(
                                                                "Text To Replace","textToReplace",
                                                                (
                                                                    TextBox("").bindPlaceholder("Enter value present in pivot column")
                                                                ),
                                                            ),
                                                            Column(
                                                                "Replacement Field","textToReplaceField",
                                                                (
                                                                    SchemaColumnsDropdown("").bindSchema("component.ports.inputs[0].schema")
                                                                ),
                                                            )                                                            
                                                        ],
                                                    ).bindProperty("replaceSpecificString")
                                                )                                                
                                        )                                    
                                        .addElement(
                                            StackLayout()
                                                .addElement(TitleElement("Pass fields to the Output"))
                                                .addElement(
                                                    SchemaColumnsDropdown("")
                                                    .withMultipleSelection()
                                                    .bindSchema("component.ports.inputs[0].schema")
                                                    .bindProperty("passFieldsToOutput")
                                                )                                                
                                        )
                                    
                                )
                        )                                                
                    )
                )
                .addElement(
                    Condition().ifEqual(PropExpr("component.properties.readOptions"), StringExpr("dynamicReadFiles"))
                    .then(
                        StackLayout()
                        .addElement(
                            SelectBox("Select File Type*")
                            .bindProperty("fileType")
                            .addOption("Excel", "fileType_XLSX")
                        )
                        .addElement(
                            Condition().ifEqual(PropExpr("component.properties.fileType"), StringExpr("fileType_XLSX"))
                            .then(
                            StepContainer().addElement(
                            Step().addElement(
                                StackLayout()
                                .addElement(
                                    SelectBox("Select output mode*")
                                    .bindProperty("outputMode")
                                    .addOption("Union excel file and sheet data by column name", "unionDatasetByName")
                                    .addOption("Retrieve sheet names", "fetchSheetNames")
                                )
                                .addElement(
                                    SelectBox("File Connection Type*")
                                    .bindProperty("xlsxFileIntegration")
                                    .addOption("Databricks", "databricks")
                                    .addOption("Onedrive", "onedrive")
                                    .addOption("S3", "s3")
                                    .addOption("SFTP", "sftp")
                                    .addOption("Sharepoint", "sharepoint")
                                    .addOption("Smartsheet", "smartsheet")
                                )
                                .addElement(
                                    (
                                        Condition()
                                        .ifEqual(PropExpr("component.properties.xlsxFileIntegration"), StringExpr("databricks"))
                                    ).then(
                                        StackLayout(height="100%")
                                        .addElement(
                                            ConnectionDropdown("databricks", "Databricks Connection")
                                            .bindProperty("fileConnector")
                                            .bindPlaceholder("Databricks Connection")
                                            .bindConnectionKind("databricks")
                                        )
                                    )
                                )
                                .addElement(
                                    (
                                        Condition()
                                        .ifEqual(PropExpr("component.properties.xlsxFileIntegration"), StringExpr("onedrive"))
                                    ).then(
                                        StackLayout(height="100%")
                                        .addElement(
                                            ConnectionDropdown("onedrive", "OneDrive Connection")
                                            .bindProperty("fileConnector")
                                            .bindPlaceholder("OneDrive Connection")
                                            .bindConnectionKind("onedrive")
                                        )
                                    )
                                )
                                .addElement(
                                    (
                                        Condition()
                                        .ifEqual(PropExpr("component.properties.xlsxFileIntegration"), StringExpr("sftp"))
                                    ).then(
                                        StackLayout(height="100%")
                                        .addElement(
                                            ConnectionDropdown("sftp", "SFTP Connection")
                                            .bindProperty("fileConnector")
                                            .bindPlaceholder("SFTP Connection")
                                            .bindConnectionKind("sftp")
                                        )
                                    )
                                )
                                .addElement(
                                    (
                                        Condition()
                                        .ifEqual(PropExpr("component.properties.xlsxFileIntegration"), StringExpr("sharepoint"))
                                    ).then(
                                        StackLayout(height="100%")
                                        .addElement(
                                            ConnectionDropdown("sharepoint", "Sharepoint Connection")
                                            .bindProperty("fileConnector")
                                            .bindPlaceholder("Sharepoint Connection")
                                            .bindConnectionKind("sharepoint")
                                        )
                                    )
                                )
                                .addElement(
                                    (
                                        Condition()
                                        .ifEqual(PropExpr("component.properties.xlsxFileIntegration"), StringExpr("smartsheet"))
                                    ).then(
                                        StackLayout(height="100%")
                                        .addElement(
                                            ConnectionDropdown("smartsheet", "Smartsheet Connection")
                                            .bindProperty("fileConnector")
                                            .bindPlaceholder("Smartsheet Connection")
                                            .bindConnectionKind("smartsheet")
                                        )
                                    )
                                )
                                .addElement(
                                    (
                                        Condition()
                                        .ifEqual(PropExpr("component.properties.xlsxFileIntegration"), StringExpr("s3"))
                                    ).then(
                                        StackLayout(height="100%")
                                        .addElement(
                                            ConnectionDropdown("s3", "S3 Connection")
                                            .bindProperty("fileConnector")
                                            .bindPlaceholder("S3 Connection")
                                            .bindConnectionKind("s3")
                                        )
                                    )
                                )
                                .addElement(
                                    TextBox("File Path Column*").bindPlaceholder("").bindProperty("xlsxFilePathColumn")
                                )
                                .addElement(
                                            TextBox("Password").bindPlaceholder("password(if any) for excel files").bindProperty("password")
                                )
                                .addElement(
                                    Condition().ifEqual(PropExpr("component.properties.outputMode"), StringExpr("unionDatasetByName")).then(
                                            TextBox("Sheet Name Column*").bindPlaceholder("").bindProperty("xlsxSheetColumn")
                                    )
                                )
                                .addElement(
                                    Condition().ifEqual(PropExpr("component.properties.outputMode"), StringExpr("unionDatasetByName")).then(
                                        Checkbox("Header Row", isChecked=True).bindProperty("header")
                                    )
                                )
                                .addElement(
                                    Condition().ifEqual(PropExpr("component.properties.outputMode"), StringExpr("fetchSheetNames")).then(
                                        TextBox("Output Column for Sheet Name").bindPlaceholder("sheet_name").bindProperty("sheetNameColumnName")
                                    )
                                )
                                .addElement(
                                    Condition().ifEqual(PropExpr("component.properties.outputMode"), StringExpr("unionDatasetByName")).then(
                                        TextBox("Output Column for File Path").bindPlaceholder("FilePath").bindProperty("filePathColumnName")
                                    )
                                )
                                .addElement(
                                    Condition().ifEqual(PropExpr("component.properties.outputMode"), StringExpr("unionDatasetByName")).then(
                                        TextBox("Output Column for Sheet Name").bindPlaceholder("SheetName").bindProperty("sheetNameColumnName")
                                    )
                                )
                                .addElement(
                                    Condition().ifEqual(PropExpr("component.properties.outputMode"), StringExpr("unionDatasetByName")).then(
                                        NativeText("Note: Empty sheets and non-excel files will be automatically skipped during processing.")
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )
    )
)