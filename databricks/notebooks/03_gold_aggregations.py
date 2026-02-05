# Databricks notebook source
# COMMAND ----------
# DBTITLE 1,AeroSight - Gold Dimensional Aggregations
# MAGIC %md
# MAGIC # AeroSight: 03 - Gold Aggregations & Dimensional Modeling Notebook
# MAGIC Generates Star-Schema Fact & Dimension Delta tables and business rollups with ranking window functions.

# COMMAND ----------
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql.types import IntegerType

SILVER_DATA_PATH = spark.conf.get("aerosight.silver.path", "/mnt/aerosight/silver")
GOLD_DATA_PATH = spark.conf.get("aerosight.gold.path", "/mnt/aerosight/gold")

# COMMAND ----------
# DBTITLE 1,Load Silver Delta
df_flights = spark.read.format("delta").load(f"{SILVER_DATA_PATH}/flights")

# COMMAND ----------
# DBTITLE 1,Build FACT_FLIGHTS Delta Table
df_fact_flights = (
    df_flights
    .withColumn("date_key", F.date_format("flight_date", "yyyyMMdd").cast(IntegerType()))
    .withColumn("origin_airport_key", F.col("origin_airport"))
    .withColumn("dest_airport_key", F.col("dest_airport"))
    .withColumn("carrier_key", F.col("carrier_code"))
    .withColumn("route_key", F.concat_ws("-", F.col("origin_airport"), F.col("dest_airport")))
    .withColumn("aircraft_key", F.col("tail_number"))
)

df_fact_flights.write.format("delta").mode("overwrite").save(f"{GOLD_DATA_PATH}/fact_flights")

# COMMAND ----------
# DBTITLE 1,Build Daily Carrier KPIs Rollup
df_carrier_kpis = (
    df_flights.groupBy("flight_date", "carrier_code")
    .agg(
        F.count("flight_id").alias("total_flights"),
        F.sum(F.when(F.col("cancelled") == 0, 1).otherwise(0)).alias("completed_flights"),
        F.round(F.avg(F.when(F.col("cancelled") == 0, F.col("arr_delay"))), 2).alias("avg_arr_delay"),
        F.round((F.sum(F.when((F.col("cancelled") == 0) & (F.col("arr_delay") < 15), 1).otherwise(0)) / F.count("flight_id")) * 100, 2).alias("on_time_arrival_pct_otp15")
    )
    .orderBy("flight_date", "carrier_code")
)

df_carrier_kpis.write.format("delta").mode("overwrite").save(f"{GOLD_DATA_PATH}/daily_carrier_kpis")
display(df_carrier_kpis.limit(10))
