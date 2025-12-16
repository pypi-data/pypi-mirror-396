from prophecy.cb.ui.uispec import *
from pyspark.sql import SparkSession
from pyspark.sql import DataFrame


def dialog() -> Dialog:
    return Dialog("Model").addElement(
        ColumnsLayout(gap="1rem", height="100%")
        .addColumn(Ports(allowInputAddOrDelete=True), "content")
        .addColumn(
            StackLayout(height="100%")
            .addElement(
                Condition()
                .ifEqual(
                    PropExpr("component.properties.parseAPIResponse"), BooleanExpr(False)
                ).then(
                    TextBox("Target Column Name").bindPlaceholder("api_data").bindProperty("targetColumnName")
                )
            )
            .addElement(TextBox("URL").bindPlaceholder("https://example.com/{{column_name}}").bindProperty("url"))
            .addElement(
                SelectBox("Method").bindProperty("method")
                .addOption("GET", "GET")
                .addOption("POST", "POST")
                .addOption("PUT", "PUT")
                .addOption("DELETE", "DELETE")
                .addOption("PATCH", "PATCH")
                .withDefault("GET")
            )
            .addElement(Checkbox("Parse API response as JSON",
                                 isChecked=False).bindProperty("parseAPIResponse"))
            .addElement(
                StackLayout(direction=("horizontal"), gap=("1rem"), alignY="center")
                .addElement(
                    StackLayout(width="442px").addElement(
                    SelectBox("Authentication").bindProperty("authType")
                        .addOption("Basic Auth", "basic")
                            .addOption("Bearer Token", "bearer")
                            .addOption("None", "none")
                            .withDefault("none")
                    )
                )
                .addElement(
                Condition()
                .ifEqual(PropExpr("component.properties.authType"), StringExpr("basic"))
                .then(
                    SqlSecretSelector("Username & Password").bindProperty("credentials").bindPlaceholder("Enter Username and Password").withSupportedSubKinds(["username_password"])
                )
                .otherwise(
                    Condition()
                    .ifEqual(PropExpr("component.properties.authType"), StringExpr("bearer"))
                    .then(
                        SqlSecretSelector("Bearer Token").bindProperty("credentials").bindPlaceholder("Enter Bearer Token").withSupportedSubKinds(["text", "m2m_oauth"])
                    )
                )
            )
            )
            .addElement(
                NativeText("Params")
            )
            .addElement(
                StackLayout(height="200px")
                .addElement(
                    BasicTable(
                        "Parameters",
                        height="200px",
                        columns=[
                            Column(
                                "Key",
                                "key",
                                (
                                    TextBox("").bindPlaceholder(
                                        "Key"
                                    )
                                ),
                            ),
                            Column(
                                "Value",
                                "value",
                                (
                                    TextBox("").bindPlaceholder(
                                        "Value"
                                    )
                                ),
                            )
                        ],
                    ).bindProperty("params")
                )
            )
            .addElement(TextBox("Body").bindPlaceholder("{{column_name}}").bindProperty("body"))
            .addElement(
                NativeText("Headers")
            )
            .addElement(
                StackLayout(height="200px")
                .addElement(
                    BasicTable(
                        "Headers",
                        height="200px",
                        columns=[
                            Column(
                                "Key",
                                "key",
                                (
                                    TextBox("").bindPlaceholder(
                                        "Key"
                                    )
                                ),
                            ),
                            Column(
                                "Value",
                                "value",
                                (
                                    ConfigText("").bindPlaceholder(
                                        "Value"
                                    )
                                ),
                            )
                        ],
                    ).bindProperty("headers")
                )
            )
            .addElement(
                AlertBox(
                    variant="success",
                    _children=[
                        Markdown(
                            "**How to Use Column Names in Your API Configuration?**\n"
                            "You can dynamically reference column values from your dataset by wrapping the column name in double curly braces `{{ }}`\n\n"
                            "**✅ Example:**\n"
                            "- **URL:** `https://example.com/{{column_name}}`\n"
                            "- → Replaces `{{column_name}}` with the value of the column\n"
                        )
                    ]
                )
            ), "5fr", overflow="auto"
        )
    )


def config_transform(
    process_id: str,
    url: str,
    method: str = "GET",
    body: str = None,
    params: list = None,
    headers: list = None,
    target_column_name: str = "api_data",
    parse_api_response: bool = True,
    auth_type: str = "none",
    credentials: dict = None
) -> dict:
    config = {
        "gemName": "RestAPI",
        "processId": process_id,
        "config": {
            "url": url,
            "method": method.upper(),
            "targetColumnName": target_column_name,
            "parseAPIResponse": parse_api_response,
            "authType": auth_type,
            "params": params or [],
            "headers": headers or [],
        }
    }
    
    if body:
        config["config"]["body"] = body
    
    if credentials and auth_type != "none":
        config["config"]["credentials"] = credentials
    
    return config

def applyPython(self, spark: SparkSession, in0: DataFrame) -> DataFrame:
    out = prophecy.write.rest_api(
        data=in0,
        url = self.props.url,
        method = self.props.method,
        body = self.props.body if hasattr(self.props, 'body') else None,
        params = self.props.params if hasattr(self.props, 'params') else None,
        headers = self.props.headers if hasattr(self.props, 'headers') else None,
        target_column_name = self.props.targetColumnName,
        parse_api_response = self.props.parseAPIResponse,
        auth_type = self.props.authType,
        credentials = self.props.credentials if hasattr(self.props, 'credentials') else None
    )
    return out
