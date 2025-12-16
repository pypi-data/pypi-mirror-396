from prophecy.cb.server.base.ComponentBuilderBase import *
from prophecy.cb.ui.uispec import *

def dialog() -> Dialog:
    return Dialog("Model").addElement(
        ColumnsLayout(gap="1rem", height="100%")
        .addColumn(Ports(allowInputAddOrDelete = True, allowOutputAddOrDelete = True), "content")
        .addColumn(
            ScrollBox().addElement(
            StackLayout(height="100%")
            .addElement(StoredProcedureSelectBox("Procedure").bindProperty("storedProcedureIdentifier"))
            .addElement(StoredProcedureArgumentTable("Arguments").bindProperty("parameters").bindStoredProcedureIdentifier("storedProcedureIdentifier"))
            .addElement(
                StackLayout(height="40%")
                .addElement(TitleElement("Pass Through Columns"))
                .addElement(BasicTable(titleVar= "", columns = [
                                                    Column(
                                                          "Column",
                                                          "alias",
                                                          TextBox("").bindPlaceholder("Column.."), width="30%"
                                                    ),
                                                    Column(
                                                          "Expression",
                                                          "expression.expression",
                                                            ExpressionBox(ignoreTitle = True, language = "sql")
                                                              .withSchemaSuggestions()
                                                              .withGroupBuilder(GroupBuilderType.EXPRESSION)
                                                              .withUnsupportedExpressionBuilderTypes([
                                                                ExpressionBuilderType.VALUE_EXPRESSION,
                                                                ExpressionBuilderType.INCREMENTAL_EXPRESSION,
                                                                ExpressionBuilderType.FUNCTION_EXPRESSION,
                                                                ExpressionBuilderType.CASE_EXPRESSION,
                                                                ExpressionBuilderType.CONFIG_EXPRESSION,
                                                                ExpressionBuilderType.SQL_FUNCTION,
                                                                ExpressionBuilderType.MACRO_FUNCTION,
                                                                ExpressionBuilderType.CUSTOM_EXPRESSION,
                                                                ExpressionBuilderType.JINJA_CONCAT_EXPRESSION,
                                                                ExpressionBuilderType.CAST_AS_EXPRESSION,
                                                                ExpressionBuilderType.COPILOT_EXPRESSION])
                                                        )
                                                ],  targetColumnKey="alias").bindProperty("passThroughColumns"))     
            )),
            "5fr"
      )
    )