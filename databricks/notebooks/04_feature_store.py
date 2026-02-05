# Databricks notebook source
# COMMAND ----------
# DBTITLE 1,AeroSight - ML Feature Store Generation
# MAGIC %md
# MAGIC # AeroSight: 04 - ML Feature Store Notebook
# MAGIC Computes cyclical temporal encodings, origin airport congestion indices, and carrier historical baseline features for Databricks ML / Feature Store.

# COMMAND ----------
import math
from pyspark.sql import functions as F

SILVER_DATA_PATH = spark.conf.get("aerosight.silver.path", "/mnt/aerosight/silver")
GOLD_DATA_PATH = spark.conf.get("aerosight.gold.path", "/mnt/aerosight/gold")

df_flights = spark.read.format("delta").load(f"{SILVER_DATA_PATH}/flights")
df_operated = df_flights.filter(F.col("cancelled") == 0)

# Carrier historical baseline
carrier_profile = (
    df_operated.groupBy("carrier_code")
    .agg(F.round(F.avg("is_delayed_15"), 4).alias("carrier_historical_delay_rate"))
)

# Origin congestion baseline
origin_profile = (
    df_operated.groupBy("origin_airport", "dep_hour")
    .agg(
        F.count("flight_id").alias("origin_hourly_flight_volume"),
        F.round(F.avg("dep_delay"), 2).alias("origin_hourly_avg_dep_delay")
    )
)

df_features = (
    df_operated
    .join(F.broadcast(carrier_profile), on="carrier_code", how="left")
    .join(F.broadcast(origin_profile), on=["origin_airport", "dep_hour"], how="left")
    .withColumn("dep_hour_sin", F.round(F.sin(F.col("dep_hour") * (2.0 * math.pi / 24.0)), 4))
    .withColumn("dep_hour_cos", F.round(F.cos(F.col("dep_hour") * (2.0 * math.pi / 24.0)), 4))
    .withColumn("day_of_week_sin", F.round(F.sin(F.col("flight_day_of_week") * (2.0 * math.pi / 7.0)), 4))
    .withColumn("day_of_week_cos", F.round(F.cos(F.col("flight_day_of_week") * (2.0 * math.pi / 7.0)), 4))
)

df_features.write.format("delta").mode("overwrite").save(f"{GOLD_DATA_PATH}/ml_features")
display(df_features.limit(10))
