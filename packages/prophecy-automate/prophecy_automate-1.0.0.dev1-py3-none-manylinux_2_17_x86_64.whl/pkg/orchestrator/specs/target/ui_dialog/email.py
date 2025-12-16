from typing import Dict, Any, List, Optional

from pyspark.sql import SparkSession
from pyspark.sql import DataFrame

# Try to import UI dependencies, but don't fail if they're not available
# These are only needed for UI generation, not for runtime execution
try:
    from prophecy.cb.server.base.ComponentBuilderBase import *
    from prophecy.cb.ui.uispec import *
except ImportError:
    pass  # UI dependencies not available, dialog() function won't work but config_transform will


def config_transform(
    process_id: str,
    connection: Dict[str, Any],
    to: List[str],
    subject: str,
    body: str,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None,
    include_data: bool = True,
    file_format: str = "csv",
    file_name: str = "data.csv",
) -> Dict[str, Any]:
   
    smtp_url = connection.get("smtpUrl")
    smtp_port = connection.get("smtpPort")
    smtp_username = connection.get("smtpUsername")
    smtp_password = connection.get("smtpPassword")
    
    # Validate required fields
    missing_fields = []
    if not smtp_url:
        missing_fields.append("smtpUrl")
    if not smtp_port:
        missing_fields.append("smtpPort")
    if not smtp_username:
        missing_fields.append("smtpUsername")
    if not smtp_password:
        missing_fields.append("smtpPassword")
    
    if missing_fields:
        raise ValueError(
            f"Missing required fields in connection: {', '.join(missing_fields)}"
        )
    
    return {
        "gemName": "Email",
        "processId": process_id,
        "config": {
            "to": to,
            "cc": cc or [],
            "bcc": bcc or [],
            "subject": subject,
            "body": body,
            "includeData": include_data,
            "fileFormat": file_format,
            "fileName": file_name,
            "connection": {
                "kind": "smtp",
                "properties": {
                    "smtpUrl": smtp_url,
                    "smtpPort": smtp_port,
                    "smtpUsername": smtp_username,
                    "smtpPassword": {
                        "kind": "plain",
                        "properties": {
                            "scope": "project",
                            "value": smtp_password
                        }
                    }
                }
            }
        }
    }


def dialog():
        # --- Controls we know exist ---
        connection = (
            ConnectionDropdown("smtp", "SMTP Connection")
                .bindProperty("connection")
                .bindPlaceholder("SMTP Connection")
                .bindConnectionKind("smtp")
        )

        # ---------- Step 1: Connection ----------
        step1_connection = Step().addElement(
            StackLayout(direction="vertical", gap="1rem")
                .addElement(TitleElement("Connection"))
                .addElement(connection)
        )

        # ---------- Step 2: Recipients (compact; per-field 'Use column') ----------
        # To
        # To (checkbox right-aligned)
        to_row = (
            StackLayout(direction="vertical", gap="0.5rem")
                .addElement(
                    StackLayout(direction="horizontal", gap="0.75rem", alignY="center", align="space-between", width="100%")
                        .addElement(TitleElement("To"))
                        .addElement(Checkbox("Use column").bindProperty("toFromColumn"))
                )
                .addElement(
                    Condition()
                        .ifEqual(PropExpr("component.properties.toFromColumn"), BooleanExpr(True))
                        .then(
                            SchemaColumnsDropdown("")
                                .bindSchema("component.ports.inputs[0].schema")
                                .bindProperty("toColumn")
                                .showErrorsFor("toColumn")
                        )
                        .otherwise(
                            SelectBox("", mode="multiple").bindProperty("to").withCreatable(True)
                        )
                )
        )

        # Optional Cc/Bcc toggle to save space
        cc_bcc_toggle = Checkbox("Add Cc/Bcc").bindProperty("showCcBcc")

        # Cc
        cc_block = (
            StackLayout(direction="vertical", gap="0.5rem")
                .addElement(
                    StackLayout(direction="horizontal", gap="0.75rem", alignY="center", align="space-between", width="100%")
                        .addElement(NativeText("Cc"))
                        .addElement(Checkbox("Use column").bindProperty("ccFromColumn"))
                )
                .addElement(
                    Condition()
                        .ifEqual(PropExpr("component.properties.ccFromColumn"), BooleanExpr(True))
                        .then(
                            SchemaColumnsDropdown("")
                                .bindSchema("component.ports.inputs[0].schema")
                                .bindProperty("ccColumn")
                        )
                        .otherwise(
                            SelectBox("", mode="multiple").bindProperty("cc").withCreatable(True)
                        )
                )
        )

        # Bcc
        bcc_block = (
            StackLayout(direction="vertical", gap="0.5rem")
                .addElement(
                    StackLayout(direction="horizontal", gap="0.75rem", alignY="center", align="space-between", width="100%")
                        .addElement(NativeText("Bcc"))
                        .addElement(Checkbox("Use column").bindProperty("bccFromColumn"))
                )
                .addElement(
                    Condition()
                        .ifEqual(PropExpr("component.properties.bccFromColumn"), BooleanExpr(True))
                        .then(
                            SchemaColumnsDropdown("")
                                .bindSchema("component.ports.inputs[0].schema")
                                .bindProperty("bccColumn")
                        )
                        .otherwise(
                            SelectBox("", mode="multiple").bindProperty("bcc").withCreatable(True)
                        )
                )
        )

        step2_recipients = Step().addElement(
            StackLayout(direction="vertical", gap="1rem")
                .addElement(to_row)
                .addElement(cc_bcc_toggle)
                .addElement(
                    Condition()
                        .ifEqual(PropExpr("component.properties.showCcBcc"), BooleanExpr(True))
                        .then(
                            ColumnsLayout(gap="1rem")
                                .addColumn(cc_block, "1fr")
                                .addColumn(bcc_block, "1fr")
                        )
                )
        )

        # ---------- Step 3: Subject & Body (per-field 'Use column') ----------
        subject_block = (
            StackLayout(direction="vertical", gap="0.5rem")
                .addElement(
                    StackLayout(direction="horizontal", gap="0.75rem", alignY="center", align="space-between", width="100%")
                        .addElement(TitleElement("Subject"))
                        .addElement(Checkbox("Use column").bindProperty("subjectFromColumn"))
                )
                .addElement(
                    Condition()
                        .ifEqual(PropExpr("component.properties.subjectFromColumn"), BooleanExpr(True))
                        .then(
                            SchemaColumnsDropdown("")
                                .bindSchema("component.ports.inputs[0].schema")
                                .bindProperty("subjectColumn")
                                .showErrorsFor("subjectColumn")
                        )
                        .otherwise(
                            TextBox("").bindProperty("subject").bindPlaceholder("Pipeline Success")
                        )
                )
        )
        body_block = (
            StackLayout(direction="vertical", gap="0.5rem")
                .addElement(
                    StackLayout(direction="horizontal", gap="0.75rem", alignY="center", align="space-between", width="100%")
                        .addElement(TitleElement("Body"))
                        .addElement(Checkbox("Use column").bindProperty("bodyFromColumn"))
                )
                .addElement(
                    StackLayout(direction="horizontal", gap="0.75rem", alignY="center")
                        .addElement(Checkbox("Use Custom HTML").bindProperty("bodyType"))
                )
                .addElement(
                    Condition()
                        .ifEqual(PropExpr("component.properties.bodyFromColumn"), BooleanExpr(True))
                        .then(
                            SchemaColumnsDropdown("")
                                .bindSchema("component.ports.inputs[0].schema")
                                .bindProperty("bodyColumn")
                                .showErrorsFor("bodyColumn")
                        )
                        .otherwise(
                            Condition()
                                .ifEqual(PropExpr("component.properties.bodyType"), BooleanExpr(True))
                                .then(
                                    TextArea("", 10).bindProperty("body").bindPlaceholder("Paste your HTML content here...")
                                )
                                .otherwise(
                                    TextArea("", 10).bindProperty("body").bindPlaceholder("Upstream pipeline run was successful")
                                )
                        )
                )
        )


        step3_subject_body = Step().addElement(
            StackLayout(direction="vertical", gap="1rem")
                .addElement(subject_block)
                .addElement(body_block)
        )

        # ---------- Step 4: Attachments (Table-based only) ----------


        table_based_ui = (
            StackLayout(direction="vertical", gap="0.75rem")
                .addElement(
                    StackLayout(direction="horizontal", gap="0.75rem", alignY="center")
                        .addElement(Checkbox("Attach input data as ").bindProperty("includeData"))
                        .addElement(SelectBox("").bindProperty("fileFormat").withStyle({"width": "20%"}).withDefault("xlsx")
                            .addOption("XLSX", "xlsx")
                            .addOption("CSV", "csv"))
                        .addElement(NativeText(" "))
                        .addElement(NativeText("named"))
                        .addElement(TextBox("").bindProperty("fileName").bindPlaceholder("File Name"))
                )
        )


        step4_attachments = Step().addElement(
            StackLayout(direction="vertical", gap="1rem")
                .addElement(TitleElement("Attachments"))
                .addElement(table_based_ui)
                .addElement(
                    AlertBox(
                        variant="info",
                        _children=[
                            Markdown(
                                "**Port Usage Information**\n\n"
                                "• **Single Port:** The same dataframe is used for both email recipients and attachment data\n\n"
                                "• **Multiple Ports:** First port contains recipient information, second port contains data to attach"
                            )
                        ]
                    )
                )
        )

        # ---------- 2-column shell: Ports | Steps (StepContainer is LIFO) ----------
        return Dialog("Email").addElement(
            ColumnsLayout(gap="1rem", height="100%")
                .addColumn(Ports(minInputPorts=1, allowInputAddOrDelete=True), "content")
                .addColumn(
                    StepContainer()
                        # Add in REVERSE so UI displays in natural order (1→4)
                        .addElement(step4_attachments)
                        .addElement(step3_subject_body)
                        .addElement(step2_recipients)
                        .addElement(step1_connection),
                    "60fr",
                    overflow="auto"
                )
        )

def applyPython(self, spark: SparkSession, in0: DataFrame):
    prophecy.write.email(
        data=in0,
        to = self.props.to,
        subject = self.props.subject,
        body = self.props.body,
        cc = self.props.cc if hasattr(self.props, 'cc') else None,
        bcc = self.props.bcc if hasattr(self.props, 'bcc') else None,
        file_format = self.props.fileFormat,
        file_name = self.props.fileName,
        connection_name = self.props.connection.id
    )
