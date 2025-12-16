from prophecy.cb.server.base.ComponentBuilderBase import *
from prophecy.cb.ui.uispec import *

def dialog() -> Dialog:
    # please edit the json generated to account for
    return Dialog("Model").addElement(
        ColumnsLayout(gap="1rem", height="100%")
        .addColumn(Ports(), "content")
        .addColumn(
            ScrollBox().addElement(
                StackLayout(height="100%", gap="48px")
                .addElement(
                    StackLayout(gap="12px")
                    .addElement(TitleElement("Choose which pipeline to run").setLevel("lg").setWeight("500"))
                    .addElement(
                        PipelineSelector("Pipeline").bindProperty("pipelineName")
                    )
                )
                .addElement(
                    StackLayout(gap="12px", width="442px")
                    .addElement(TitleElement("Trigger only if").setLevel("lg").setWeight("500"))
                    .addElement(
                        SelectBox("Trigger").bindProperty("triggerCondition")
                        .addOption("Always run", "Always")
                        .addOption("All pipelines run successfully", "AllSuccess")
                        .addOption("All pipelines failed", "AllFailed")
                        .addOption("Any pipeline succeeded", "AnySuccess")
                        .addOption("Any pipeline failed", "AnyFailed")
                        .withDefault("Always")
                        .withHint('Trigger conditions are evaluated based on the status column. A value of "success" is treated as successful run; any other value is treated as failure.')
                    )
                )
                .addElement(
                    StackLayout(gap="12px")
                    .addElement(TitleElement("Advanced Options").setLevel("lg").setWeight("500"))
                    .addElement(
                        StackLayout(direction=("horizontal"), gap=("1rem"), alignY="center")
                        .addElement(
                            Checkbox("Maximum number of pipeline triggers: ").bindProperty("enableMaxTriggers")
                        )
                        .addElement(
                            StackLayout(width="80px")
                            .addElement(
                                Condition()
                                .ifEqual(PropExpr("component.properties.enableMaxTriggers"), BooleanExpr(True))
                                .then(
                                    NumberBox("").bindProperty("maxTriggers").withMin(0).withMax(10000)
                                )
                                .otherwise(
                                    NumberBox("", disabledView=True).bindProperty("maxTriggers").withMin(0).withMax(10000)
                                )
                            )
                        )
                    )
                )
                .addElement(
                    StackLayout(gap="12px")
                    .addElement(TitleElement("Set pipeline parameters").setLevel("lg").setWeight("500"))
                    .addElement(
                        PipelineParameters("Parameters").bindPipelineId("${component.properties.pipelineName}").bindProperty("parameters")
                    )
                )
            )
        )
    )