"""
AeroSight ML Feature Store Builder
Generates enriched feature sets from Silver & Gold layers for training
Delay Prediction, Anomaly Detection, and Traffic Forecasting models.
"""

import os
import math
import pandas as pd
import numpy as np
from spark.session import get_spark_session, stop_spark_session
from pyspark.sql import functions as F

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SILVER_DIR = os.path.join(BASE_DIR, "data", "silver")
GOLD_DIR = os.path.join(BASE_DIR, "data", "gold")

def run_feature_store_pipeline():
    print("Starting ML Feature Store Pipeline...")
    spark = get_spark_session("AeroSight-FeatureStore")

    try:
        silver_flights_path = os.path.join(SILVER_DIR, "flights")
        df_flights = spark.read.parquet(silver_flights_path)
        
        # Filter for operated flights (cancellations handled separately in cancellation model)
        df_operated = df_flights.filter(F.col("cancelled") == 0)

        # 1. Carrier historical delay profile
        carrier_profile = (
            df_operated.groupBy("carrier_code")
            .agg(
                F.round(F.avg("is_delayed_15"), 4).alias("carrier_historical_delay_rate"),
                F.round(F.avg("arr_delay"), 2).alias("carrier_avg_arr_delay")
            )
        )

        # 2. Origin airport congestion profile
        origin_profile = (
            df_operated.groupBy("origin_airport", "dep_hour")
            .agg(
                F.count("flight_id").alias("origin_hourly_flight_volume"),
                F.round(F.avg("dep_delay"), 2).alias("origin_hourly_avg_dep_delay"),
                F.round(F.avg("taxi_out"), 2).alias("origin_hourly_avg_taxi_out")
            )
        )

        # 3. Route historical profile
        route_profile = (
            df_operated.groupBy("origin_airport", "dest_airport")
            .agg(
                F.round(F.avg("arr_delay"), 2).alias("route_avg_arr_delay"),
                F.round(F.avg("is_delayed_15"), 4).alias("route_delay_rate")
            )
        )

        # 4. Join and calculate cyclical and normalized features
        df_features = (
            df_operated
            .join(F.broadcast(carrier_profile), on="carrier_code", how="left")
            .join(F.broadcast(origin_profile), on=["origin_airport", "dep_hour"], how="left")
            .join(F.broadcast(route_profile), on=["origin_airport", "dest_airport"], how="left")
            .withColumn("dep_hour_sin", F.round(F.sin(F.col("dep_hour") * (2.0 * math.pi / 24.0)), 4))
            .withColumn("dep_hour_cos", F.round(F.cos(F.col("dep_hour") * (2.0 * math.pi / 24.0)), 4))
            .withColumn("day_of_week_sin", F.round(F.sin(F.col("flight_day_of_week") * (2.0 * math.pi / 7.0)), 4))
            .withColumn("day_of_week_cos", F.round(F.cos(F.col("flight_day_of_week") * (2.0 * math.pi / 7.0)), 4))
            .withColumn("month_sin", F.round(F.sin(F.col("flight_month") * (2.0 * math.pi / 12.0)), 4))
            .withColumn("month_cos", F.round(F.cos(F.col("flight_month") * (2.0 * math.pi / 12.0)), 4))
            .withColumn("is_weekend", F.when(F.col("flight_day_of_week").isin([1, 7]), 1).otherwise(0))
            .withColumn("is_rush_hour", F.when(F.col("dep_hour").isin([7, 8, 9, 16, 17, 18, 19]), 1).otherwise(0))
            .withColumn("is_severe_weather",
                F.when(F.col("origin_weather_condition").isin(["Thunderstorm", "Snow", "Fog"]) | (F.col("origin_wind_mph") > 20), 1)
                .otherwise(0)
            )
        )

        output_path = os.path.join(GOLD_DIR, "ml_features")
        df_features.write.mode("overwrite").parquet(output_path)
        print(f"✅ ML Feature Store successfully generated with {df_features.count():,} rows at {output_path}")

    finally:
        stop_spark_session(spark)

if __name__ == "__main__":
    run_feature_store_pipeline()
