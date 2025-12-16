from prophecy.cb.server.base.ComponentBuilderBase import *
from prophecy.cb.ui.uispec import *
from pyspark.sql import SparkSession
from pyspark.sql import DataFrame

def dialog() -> Dialog:
    placeholders = {
            "scala": """select * from in0""",
            "python": """# Sample Python Code for Notebook

from pyspark.sql import SparkSession

# Initialize Spark Session
spark = SparkSession.builder.appName("WarehouseJob").getOrCreate()

# Read CSV file from HDFS
df = spark.read.option("header", "true").csv("hdfs:/mnt/data/input.csv")

# Define Databricks SQL Warehouse Table Name
table_name = "default.sample_table"

# Write Data to SQL Warehouse as a Delta Table
df.write.format("delta").mode("overwrite").saveAsTable(table_name)""",
            "sql": """select * from in0"""}
    leftColumn = StackLayout(height="100%") \
                .addElement(
                    Ports(allowInputAddOrDelete = True, allowOutputAddOrDelete = True, minInputPorts=0, minOutputPorts=0)
                    .bindProperty("ports")
                )
    rightColumn = StackLayout(height = "100%") \
                            .addElement(
                                CodeBlock("def Script():")
                                    .bindProperty("scriptMethodHeader")
                                    .bindCodeLanguage("python")
                                ) \
                            .addElement(
                                StackItem(grow = 1).addElement(
                                    Editor()
                                    .bindLanguage("python")
                                    .bindProperty("script")
                                )
                            ) \
                            .addElement(
                                CodeBlock("return")
                                    .bindProperty("scriptMethodFooter")
                                    .bindCodeLanguage("python")
                            )
    # please edit the json generated to account for
    return Dialog("Script").addElement(
        ColumnsLayout(gap="1rem", height="100%")
        .addColumn(leftColumn, "content")
        .addColumn(
            rightColumn,
            "2fr"
        )
    )

def applyPython(self, spark: SparkSession, *inDFs: DataFrame) -> DataFrame:
    exec(self.props.script)
    return eval(self.props.scriptMethodFooter.lstrip('return '))
