from typing import Dict, Any

from pyspark.sql import SparkSession
from pyspark.sql import DataFrame


def config_transform(
    process_id: str,
    connection: Dict[str, Any],
    project_name: str,
    datasource_name: str,
) -> Dict[str, Any]:
    
    server_url = connection.get("serverUrl")
    token_name = connection.get("tokenName")
    token_value = connection.get("tokenValue")
    site_name = connection.get("siteName")
    
    # Validate required fields
    missing_fields = []
    if not server_url:
        missing_fields.append("serverUrl")
    if not token_name:
        missing_fields.append("tokenName")
    if not token_value:
        missing_fields.append("tokenValue")
    if not site_name:
        missing_fields.append("siteName")
    
    if missing_fields:
        raise ValueError(
            f"Missing required fields in connection: {', '.join(missing_fields)}"
        )
    
    return {
        "gemName": "TableauWrite",
        "processId": process_id,
        "config": {
            "projectName": project_name,
            "dataSource": datasource_name,
            "connection": {
                "kind": "tableau",
                "properties": {
                    "serverUrl": server_url,
                    "tokenName": token_name,
                    "tokenValue": {
                        "kind": "plain",
                        "properties": {
                            "scope": "project",
                            "value": token_value
                        }
                    },
                    "siteName": site_name
                }
            }
        }
    }


def dialog():
    # Import UI dependencies only when generating UI
    import prophecy.cb.ui.uispec as uispec
    
    connection = uispec.ConnectionDropdown("tableau", "Tableau Connection").bindProperty("connection").bindPlaceholder("Tableau Token").bindConnectionKind("tableau")

    return uispec.Dialog("Tableau").addElement(
        uispec.ColumnsLayout(gap="1rem", height="100%")
        .addColumn(uispec.Ports(allowCustomOutputSchema=False), "content")
        .addColumn(
            uispec.StackLayout(height="100%")
            .addElement(connection)
            .addElement(uispec.TextBox("Project name").bindProperty("projectName"))
            .addElement(uispec.TextBox("Data source").bindProperty("dataSource")),
            "5fr"
        )
    )

def applyPython(self, spark: SparkSession, in0: DataFrame):
    prophecy.write.tableau(
        data=in0,
        project_name = self.props.properties.projectName,
        datasource_name = self.props.properties.dataSource,
        connection_name = self.props.connector.id,
    )
