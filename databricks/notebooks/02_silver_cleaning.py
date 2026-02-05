# Databricks notebook source
# COMMAND ----------
# DBTITLE 1,AeroSight - Silver Cleaning & Standardization
# MAGIC %md
# MAGIC # AeroSight: 02 - Silver Cleaning Notebook
# MAGIC Reads Bronze Delta table, executes schema enforcement, derives operational KPI flags,
# MAGIC performs window turnaround time calculations, and writes to Delta Silver table partitioned by carrier.

# COMMAND ----------
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql.types import DoubleType, IntegerType

BRONZE_DATA_PATH = spark.conf.get("aerosight.bronze.path", "/mnt/aerosight/bronze")
SILVER_DATA_PATH = spark.conf.get("aerosight.silver.path", "/mnt/aerosight/silver")

# COMMAND ----------
# DBTITLE 1,Read Bronze Delta Table
df_bronze = spark.read.format("delta").load(f"{BRONZE_DATA_PATH}/flights")

# COMMAND ----------
# DBTITLE 1,Standardize and Enrich Records
df_clean = (
    df_bronze
    .filter(F.col("flight_id").isNotNull() & F.col("flight_date").isNotNull())
    .withColumn("flight_date", F.to_date(F.col("flight_date"), "yyyy-MM-dd"))
    .withColumn("flight_year", F.year(F.col("flight_date")))
    .withColumn("flight_month", F.month(F.col("flight_date")))
    .withColumn("flight_day_of_week", F.dayofweek(F.col("flight_date")))
    .withColumn("dep_delay", F.coalesce(F.col("dep_delay").cast(DoubleType()), F.lit(0.0)))
    .withColumn("arr_delay", F.coalesce(F.col("arr_delay").cast(DoubleType()), F.lit(0.0)))
    .withColumn("taxi_out", F.coalesce(F.col("taxi_out").cast(DoubleType()), F.lit(0.0)))
    .withColumn("taxi_in", F.coalesce(F.col("taxi_in").cast(DoubleType()), F.lit(0.0)))
    .withColumn("distance", F.col("distance").cast(IntegerType()))
    .withColumn("air_time", F.coalesce(F.col("air_time").cast(DoubleType()), F.lit(0.0)))
    .withColumn("is_delayed_15", F.when(F.col("arr_delay") >= 15.0, 1).otherwise(0))
    .withColumn("is_delayed_45", F.when(F.col("arr_delay") >= 45.0, 1).otherwise(0))
    .withColumn("is_severe_delay", F.when(F.col("arr_delay") >= 120.0, 1).otherwise(0))
    .withColumn("dep_hour", (F.col("crs_dep_time") / 100).cast(IntegerType()))
    .withColumn("arr_hour", (F.col("crs_arr_time") / 100).cast(IntegerType()))
    .withColumn("route_code", F.concat_ws("-", F.col("origin_airport"), F.col("dest_airport")))
)

# COMMAND ----------
# DBTITLE 1,Window Function Turnaround Calculation
tail_window = Window.partitionBy("tail_number", "flight_date").orderBy("crs_dep_time")
df_silver = (
    df_clean
    .withColumn("prev_dest_airport", F.lag("dest_airport").over(tail_window))
    .withColumn("prev_arr_time", F.lag("arr_time").over(tail_window))
    .withColumn("is_connected_flight", F.when(F.col("prev_dest_airport") == F.col("origin_airport"), 1).otherwise(0))
)

# COMMAND ----------
# DBTITLE 1,Write to Silver Delta Table
(
    df_silver.write
    .format("delta")
    .mode("overwrite")
    .partitionBy("carrier_code")
    .option("overwriteSchema", "true")
    .save(f"{SILVER_DATA_PATH}/flights")
)

display(df_silver.limit(10))
