from prophecy.cb.server.base.ComponentBuilderBase import *
from prophecy.cb.ui.uispec import *

def dialog() -> Dialog:
    return Dialog("Directory").addElement(
        ColumnsLayout(gap="1rem", height="100%")
        .addColumn(Ports(), "content")
        .addColumn(
            StackLayout(height="100%")
            .addElement(
                SelectBox("Connection Type")
                .bindProperty("integration")
                .addOption("Databricks Volumes", "databricks")
                .addOption("S3", "s3")
                .addOption("OneDrive", "onedrive")
                .addOption("Sftp", "sftp")
                .addOption("Sharepoint", "sharepoint")
                .addOption("Smartsheet", "smartsheet")
            )
            .addElement(
                (
                    Condition()
                    .ifEqual(PropExpr("component.properties.integration"), StringExpr("databricks"))
                ).then(
                    ConnectionDropdown("databricks", "Databricks Connection")
                        .bindProperty("connector")
                        .bindPlaceholder("Databricks Connection")
                        .bindConnectionKind("databricks")
                ).otherwise(
                    (
                        Condition()
                        .ifEqual(PropExpr("component.properties.integration"), StringExpr("s3"))
                    ).then(
                        ConnectionDropdown("s3", "S3 Connection")
                            .bindProperty("connector")
                            .bindPlaceholder("S3 Connection")
                            .bindConnectionKind("s3")
                    ).otherwise(
                        (
                            Condition()
                            .ifEqual(PropExpr("component.properties.integration"), StringExpr("onedrive"))
                        ).then(
                            ConnectionDropdown("onedrive", "OneDrive Connection")
                                .bindProperty("connector")
                                .bindPlaceholder("OneDrive Connection")
                                .bindConnectionKind("onedrive")
                        ).otherwise(
                            (
                                Condition()
                                .ifEqual(PropExpr("component.properties.integration"), StringExpr("sftp"))
                            ).then(
                                ConnectionDropdown("sftp", "SFTP Connection")
                                    .bindProperty("connector")
                                    .bindPlaceholder("SFTP Connection")
                                    .bindConnectionKind("sftp")
                            ).otherwise(
                                (
                                    Condition()
                                    .ifEqual(PropExpr("component.properties.integration"), StringExpr("sharepoint"))
                                ).then(
                                    ConnectionDropdown("sharepoint", "Sharepoint Connection")
                                        .bindProperty("connector")
                                        .bindPlaceholder("Sharepoint Connection")
                                        .bindConnectionKind("sharepoint")
                                ).otherwise(
                                    ConnectionDropdown("smartsheet", "Smartsheet Connection")
                                        .bindProperty("connector")
                                        .bindPlaceholder("Smartsheet Connection")
                                        .bindConnectionKind("smartsheet")
                                )
                            )
                        )
                    )
                )
            )
            .addElement(
                TextBox("Path")
                .bindPlaceholder("/path/to/directory/*.csv")
                .bindProperty("path")
            )
            .addElement(
                Checkbox("Enable to include files/directories inside subfolders")
                .bindProperty("recursive")
            )
            .addElement(
                TextBox("File Pattern")
                .bindPlaceholder("*.csv")
                .bindProperty("pattern")
            )
            .addElement(
                Checkbox("Include sheet name as column in output for xlsx files")
                .bindProperty("addSheetNameColumn")
            )
            .addElement(
                Condition().ifEqual(PropExpr("component.properties.addSheetNameColumn"), BooleanExpr(True)).then(
                    TextBox("Password").bindPlaceholder("password(if any) for xlsx files").bindProperty("password")
                )
            )
            .addElement(
                AlertBox(
                    variant="info",
                    _children=[
                        Markdown(
                            "This gem returns all folders and files in the selected path."
                            "For each folder or file, the output includes the following:"
                            "name, path, size_in_bytes, creation_time, modification_time, parent_directory, file_type, sheet_name(for xlsx files, only if checkbox is ticked)"
                        )
                    ]
                )
            )
        )
    )