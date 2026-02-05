"""
AeroSight PySpark Silver Transformation Job
Reads raw Bronze data, applies schema standardization, data cleaning,
enrichment, window-based turnaround calculations, and writes to the Silver layer.
"""

import os
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql.types import DoubleType, IntegerType, StringType, DateType, TimestampType
from spark.session import get_spark_session, stop_spark_session

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRONZE_DIR = os.path.join(BASE_DIR, "data", "bronze")
SILVER_DIR = os.path.join(BASE_DIR, "data", "silver")

def run_silver_transformation():
    print("Starting Silver Layer Transformation Job...")
    spark = get_spark_session("AeroSight-SilverTransformation")

    try:
        bronze_flights_path = os.path.join(BRONZE_DIR, "flights")
        if not os.path.exists(bronze_flights_path):
            raise FileNotFoundError(f"Bronze flights directory not found at {bronze_flights_path}")

        df = spark.read.parquet(bronze_flights_path)
        print(f"Read {df.count():,} rows from Bronze flights.")

        # 1. Standardize types and handle nulls
        df_clean = (
            df
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
            .withColumn("carrier_delay", F.coalesce(F.col("carrier_delay").cast(DoubleType()), F.lit(0.0)))
            .withColumn("weather_delay", F.coalesce(F.col("weather_delay").cast(DoubleType()), F.lit(0.0)))
            .withColumn("nas_delay", F.coalesce(F.col("nas_delay").cast(DoubleType()), F.lit(0.0)))
            .withColumn("security_delay", F.coalesce(F.col("security_delay").cast(DoubleType()), F.lit(0.0)))
            .withColumn("late_aircraft_delay", F.coalesce(F.col("late_aircraft_delay").cast(DoubleType()), F.lit(0.0)))
        )

        # 2. Derive delay classification flags
        df_enriched = (
            df_clean
            .withColumn("is_delayed_15", F.when(F.col("arr_delay") >= 15.0, 1).otherwise(0))
            .withColumn("is_delayed_45", F.when(F.col("arr_delay") >= 45.0, 1).otherwise(0))
            .withColumn("is_severe_delay", F.when(F.col("arr_delay") >= 120.0, 1).otherwise(0))
            .withColumn("dep_hour", (F.col("crs_dep_time") / 100).cast(IntegerType()))
            .withColumn("arr_hour", (F.col("crs_arr_time") / 100).cast(IntegerType()))
            .withColumn("route_code", F.concat_ws("-", F.col("origin_airport"), F.col("dest_airport")))
            .withColumn("dep_delay_group",
                F.when(F.col("dep_delay") < 0, "Early (< 0m)")
                .when((F.col("dep_delay") >= 0) & (F.col("dep_delay") < 15), "On-Time (0-14m)")
                .when((F.col("dep_delay") >= 15) & (F.col("dep_delay") < 45), "Moderate (15-44m)")
                .when((F.col("dep_delay") >= 45) & (F.col("dep_delay") < 120), "Heavy (45-119m)")
                .otherwise("Severe (120m+)")
            )
            .withColumn("speed_mph",
                F.when(F.col("air_time") > 0, F.round((F.col("distance") * 1.15078) / (F.col("air_time") / 60.0), 1))
                .otherwise(F.lit(0.0))
            )
        )

        # 3. Window Function: Aircraft turnaround time estimation
        tail_window = Window.partitionBy("tail_number", "flight_date").orderBy("crs_dep_time")
        df_silver = (
            df_enriched
            .withColumn("prev_dest_airport", F.lag("dest_airport").over(tail_window))
            .withColumn("prev_arr_time", F.lag("arr_time").over(tail_window))
            .withColumn("is_connected_flight", F.when(F.col("prev_dest_airport") == F.col("origin_airport"), 1).otherwise(0))
        )

        # 4. Save to Silver Layer
        silver_flights_out = os.path.join(SILVER_DIR, "flights")
        df_silver.write.mode("overwrite").partitionBy("carrier_code").parquet(silver_flights_out)
        print(f"✅ Saved Silver Flights ({df_silver.count():,} rows) to {silver_flights_out}")

        # Also copy reference dimensions from Bronze to Silver
        for entity in ["airports", "airlines", "aircraft", "baggage"]:
            b_path = os.path.join(BRONZE_DIR, entity)
            if os.path.exists(b_path):
                spark.read.parquet(b_path).write.mode("overwrite").parquet(os.path.join(SILVER_DIR, entity))
                print(f"✅ Saved Silver {entity.capitalize()}")

        print("Silver Layer transformations completed successfully.")
    finally:
        stop_spark_session(spark)

if __name__ == "__main__":
    run_silver_transformation()
