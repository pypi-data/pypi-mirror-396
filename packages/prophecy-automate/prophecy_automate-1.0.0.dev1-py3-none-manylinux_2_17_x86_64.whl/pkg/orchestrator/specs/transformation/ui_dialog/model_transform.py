from prophecy.cb.server.base.ComponentBuilderBase import *
from prophecy.cb.ui.uispec import *

def dialog() -> Dialog:
    # please edit the json generated to account for
    return Dialog("Model").addElement(
        ColumnsLayout(gap="1rem", height="100%")
        .addColumn(Ports(), "content")
        .addColumn(
            StackLayout(height="100%")
            .addElement(ConfigText("Model Name").bindProperty("properties.modelName"))
            .addElement(Checkbox("Run Seeds").bindProperty("properties.runSeeds")),
            "5fr"
        )
    )