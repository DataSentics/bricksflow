# Databricks notebook source
# MAGIC %md
# MAGIC <img src="https://github.com/richardcerny/bricksflow/raw/rc-bricksflow2.1/docs/img/databricks_icon.png?raw=true" width=100/>
# MAGIC # Bricksflow example 3.
# MAGIC
# MAGIC ## Bricksflow Development flow - DEMO
# MAGIC There is a standard process of developing pipelines using Bricksflow. The aim is to use SW Engineering practices while still working in interactively in Databricks notebooks. Follow schema bellow while using Bricksflow.
# MAGIC
# MAGIC If you want to get more info about the process check Bricksflow User training video - [Link](https://web.microsoftstream.com/video/e8e3ed9b-7944-4ea2-b314-8f0694853fcf)
# MAGIC <img src="https://github.com/richardcerny/bricksflow/raw/rc-bricksflow2.1/docs/img/development-flow.png?raw=true" width=1200/>
# MAGIC

# COMMAND ----------

# MAGIC %md ## Common console commands you would use:
# MAGIC - `console dbx:deploy --env=dev` to upload notebooks & configs from local to Databricks
# MAGIC - `console dbx:workspace:export --env=dev` to download notebooks from Databricks to local
# MAGIC
# MAGIC Tip: By executing `console` you get list of available commands that you can use

# COMMAND ----------

# MAGIC %run ../../../app/install_master_package

# COMMAND ----------

from pyspark.sql import functions as f
from datetime import datetime
from logging import Logger
from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame
from datalakebundle.notebook.decorators import dataFrameLoader, transformation, dataFrameSaver
from datalakebundle.table.TableManager import TableManager

# COMMAND ----------


@dataFrameLoader(display=False)
def read_table_bronze_covid_tbl_template_1_mask_usage(spark: SparkSession, table_manager: TableManager):
    return spark.read.table(table_manager.getName("bronze_covid.tbl_template_1_mask_usage"))


# COMMAND ----------


@transformation(read_table_bronze_covid_tbl_template_1_mask_usage, display=False)
def add_execution_datetime(df: DataFrame):
    return df.withColumn("EXECUTE_DATETIME", f.lit(datetime.now()))


# COMMAND ----------


@transformation("%myparameter.myvalue%", add_execution_datetime, display=True)
def add_parameter_from_config(config_yaml_parameter, df: DataFrame):
    print(config_yaml_parameter)
    return df.withColumn("CONFIG_YAML_PARAMETER", f.lit(config_yaml_parameter))


# COMMAND ----------


@dataFrameSaver(add_parameter_from_config)
def save_table_silver_covid_tbl_template_3_mask_usage(df: DataFrame, logger: Logger, table_manager: TableManager):
    output_table_name = table_manager.getName("silver_covid.tbl_template_3_mask_usage")
    if table_manager.exists("silver_covid.tbl_template_3_mask_usage"):
        logger.info(f"Table {output_table_name} exists. Appending...")
    else:
        table_manager.create("silver_covid.tbl_template_3_mask_usage")

    logger.info(f"Saving data to table: {output_table_name}")
    (
        df.select(
            "COUNTYFP",
            "NEVER",
            "RARELY",
            "SOMETIMES",
            "FREQUENTLY",
            "ALWAYS",
            "EXECUTE_DATETIME",
            "CONFIG_YAML_PARAMETER",
        )
        .write.option("partitionOverwriteMode", "dynamic")
        .insertInto(output_table_name)
    )