# Databricks notebook source
# COMMAND ----------
# DBTITLE 1,AeroSight - Bronze Medallion Ingestion
# MAGIC %md
# MAGIC # AeroSight: 01 - Bronze Ingestion Notebook
# MAGIC Ingests raw flight operational CSVs from ADLS / S3 / DBFS into Delta Lake Bronze tables with audit metadata.

# COMMAND ----------
import uuid
from datetime import datetime
from pyspark.sql import functions as F

# Configuration: Set storage path (works with DBFS, S3 s3a://, or Azure ADLS abfss://)
RAW_DATA_PATH = spark.conf.get("aerosight.raw.path", "/mnt/aerosight/raw")
BRONZE_DATA_PATH = spark.conf.get("aerosight.bronze.path", "/mnt/aerosight/bronze")

batch_id = str(uuid.uuid4())
ingestion_ts = datetime.utcnow()
print(f"Starting Bronze Ingestion. Batch ID: {batch_id}")

# COMMAND ----------
# DBTITLE 1,Ingest Raw Flights to Bronze Delta Table
df_raw_flights = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv(f"{RAW_DATA_PATH}/flights_sample.csv")
)

df_bronze_flights = (
    df_raw_flights
    .withColumn("_ingestion_id", F.lit(batch_id))
    .withColumn("_ingestion_timestamp", F.lit(ingestion_ts))
    .withColumn("_source_file", F.lit("flights_sample.csv"))
)

# Write to Delta Lake Bronze table
(
    df_bronze_flights.write
    .format("delta")
    .mode("append")
    .option("mergeSchema", "true")
    .save(f"{BRONZE_DATA_PATH}/flights")
)

display(df_bronze_flights.limit(10))
