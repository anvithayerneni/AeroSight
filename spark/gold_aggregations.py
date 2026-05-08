"""
AeroSight PySpark Gold Aggregations & Dimensional Lakehouse Job
Transforms Silver data into Dimensional Star Schema Fact & Dimension tables,
executes advanced analytical Window functions, and outputs curated business aggregates to Gold.
"""

import os

from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType
from pyspark.sql.window import Window

from spark.session import get_spark_session, stop_spark_session

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SILVER_DIR = os.path.join(BASE_DIR, "data", "silver")
GOLD_DIR = os.path.join(BASE_DIR, "data", "gold")

def run_gold_aggregations():
    print("Starting Gold Layer Aggregations Job...")
    spark = get_spark_session("AeroSight-GoldAggregations")

    try:
        silver_flights_path = os.path.join(SILVER_DIR, "flights")
        silver_airports_path = os.path.join(SILVER_DIR, "airports")
        silver_airlines_path = os.path.join(SILVER_DIR, "airlines")
        silver_aircraft_path = os.path.join(SILVER_DIR, "aircraft")
        silver_baggage_path = os.path.join(SILVER_DIR, "baggage")

        df_flights = spark.read.parquet(silver_flights_path)
        df_airports = spark.read.parquet(silver_airports_path) if os.path.exists(silver_airports_path) else None
        df_airlines = spark.read.parquet(silver_airlines_path) if os.path.exists(silver_airlines_path) else None
        df_aircraft = spark.read.parquet(silver_aircraft_path) if os.path.exists(silver_aircraft_path) else None
        df_baggage = spark.read.parquet(silver_baggage_path) if os.path.exists(silver_baggage_path) else None

        os.makedirs(GOLD_DIR, exist_ok=True)

        # -------------------------------------------------------------
        # 1. DIM_DATE
        # -------------------------------------------------------------
        print("Generating DIM_DATE...")
        df_dates = (
            df_flights.select("flight_date").distinct()
            .withColumn("date_key", F.date_format("flight_date", "yyyyMMdd").cast(IntegerType()))
            .withColumn("year", F.year("flight_date"))
            .withColumn("quarter", F.quarter("flight_date"))
            .withColumn("month", F.month("flight_date"))
            .withColumn("month_name", F.date_format("flight_date", "MMMM"))
            .withColumn("day_of_month", F.dayofmonth("flight_date"))
            .withColumn("day_of_week", F.dayofweek("flight_date"))
            .withColumn("day_name", F.date_format("flight_date", "EEEE"))
            .withColumn("is_weekend", F.when(F.col("day_of_week").isin([1, 7]), 1).otherwise(0))
            .orderBy("flight_date")
        )
        df_dates.write.mode("overwrite").parquet(os.path.join(GOLD_DIR, "dim_date"))

        # -------------------------------------------------------------
        # 2. DIM_AIRPORT
        # -------------------------------------------------------------
        if df_airports:
            print("Generating DIM_AIRPORT...")
            df_dim_airport = (
                df_airports
                .withColumn("airport_key", F.col("iata"))
                .select("airport_key", "iata", "icao", "name", "city", "state", "lat", "lon", "elev", "tz", "hub", "terminals", "gates")
            )
            df_dim_airport.write.mode("overwrite").parquet(os.path.join(GOLD_DIR, "dim_airport"))

        # -------------------------------------------------------------
        # 3. DIM_AIRLINE
        # -------------------------------------------------------------
        if df_airlines:
            print("Generating DIM_AIRLINE...")
            df_dim_airline = (
                df_airlines
                .withColumn("airline_key", F.col("carrier_code"))
                .select("airline_key", "carrier_code", "airline_name", "callsign", "country", "fleet_size", "primary_hub")
            )
            df_dim_airline.write.mode("overwrite").parquet(os.path.join(GOLD_DIR, "dim_airline"))

        # -------------------------------------------------------------
        # 4. DIM_ROUTE
        # -------------------------------------------------------------
        print("Generating DIM_ROUTE...")
        df_dim_route = (
            df_flights.groupBy("origin_airport", "dest_airport")
            .agg(
                F.first("distance").alias("distance_miles"),
                F.round(F.avg("crs_elapsed_time"), 1).alias("avg_scheduled_elapsed_min"),
                F.count("flight_id").alias("historical_flight_count")
            )
            .withColumn("route_key", F.concat_ws("-", F.col("origin_airport"), F.col("dest_airport")))
            .withColumn("distance_category",
                F.when(F.col("distance_miles") < 500, "Short Haul (<500 mi)")
                .when((F.col("distance_miles") >= 500) & (F.col("distance_miles") < 1500), "Medium Haul (500-1499 mi)")
                .otherwise("Long Haul (1500+ mi)")
            )
        )
        df_dim_route.write.mode("overwrite").parquet(os.path.join(GOLD_DIR, "dim_route"))

        # -------------------------------------------------------------
        # 5. DIM_AIRCRAFT
        # -------------------------------------------------------------
        if df_aircraft:
            print("Generating DIM_AIRCRAFT...")
            df_dim_aircraft = (
                df_aircraft
                .withColumn("aircraft_key", F.col("tail_number"))
                .select("aircraft_key", "tail_number", "carrier_code", "model", "manufacturer", "seat_capacity", "cruise_speed_knots", "year_manufactured")
            )
            df_dim_aircraft.write.mode("overwrite").parquet(os.path.join(GOLD_DIR, "dim_aircraft"))

        # -------------------------------------------------------------
        # 6. FACT_FLIGHTS
        # -------------------------------------------------------------
        print("Generating FACT_FLIGHTS...")
        df_fact_flights = (
            df_flights
            .withColumn("date_key", F.date_format("flight_date", "yyyyMMdd").cast(IntegerType()))
            .withColumn("origin_airport_key", F.col("origin_airport"))
            .withColumn("dest_airport_key", F.col("dest_airport"))
            .withColumn("carrier_key", F.col("carrier_code"))
            .withColumn("route_key", F.concat_ws("-", F.col("origin_airport"), F.col("dest_airport")))
            .withColumn("aircraft_key", F.col("tail_number"))
            .select(
                "flight_id", "date_key", "flight_date", "carrier_key", "flight_number", "aircraft_key",
                "origin_airport_key", "dest_airport_key", "route_key",
                "crs_dep_time", "dep_time", "dep_delay", "taxi_out", "wheels_off",
                "wheels_on", "taxi_in", "crs_arr_time", "arr_time", "arr_delay",
                "cancelled", "cancellation_code", "diverted",
                "crs_elapsed_time", "actual_elapsed_time", "air_time", "distance",
                "is_delayed_15", "is_delayed_45", "is_severe_delay",
                "origin_temp_f", "origin_wind_mph", "origin_visibility_miles", "origin_weather_condition",
                "dest_temp_f", "dest_wind_mph", "dest_visibility_miles", "dest_weather_condition"
            )
        )
        df_fact_flights.write.mode("overwrite").parquet(os.path.join(GOLD_DIR, "fact_flights"))

        # -------------------------------------------------------------
        # 7. FACT_DELAYS
        # -------------------------------------------------------------
        print("Generating FACT_DELAYS...")
        df_fact_delays = (
            df_flights.filter(F.col("arr_delay") >= 15.0)
            .withColumn("date_key", F.date_format("flight_date", "yyyyMMdd").cast(IntegerType()))
            .withColumn("carrier_key", F.col("carrier_code"))
            .withColumn("origin_airport_key", F.col("origin_airport"))
            .withColumn("dest_airport_key", F.col("dest_airport"))
            .withColumn("primary_delay_cause",
                F.when(F.col("weather_delay") >= F.greatest("carrier_delay", "nas_delay", "late_aircraft_delay", "security_delay"), "Weather")
                .when(F.col("carrier_delay") >= F.greatest("weather_delay", "nas_delay", "late_aircraft_delay", "security_delay"), "Carrier")
                .when(F.col("late_aircraft_delay") >= F.greatest("carrier_delay", "weather_delay", "nas_delay", "security_delay"), "Late Aircraft")
                .when(F.col("nas_delay") >= F.greatest("carrier_delay", "weather_delay", "late_aircraft_delay", "security_delay"), "NAS")
                .otherwise("Other")
            )
            .select(
                "flight_id", "date_key", "carrier_key", "origin_airport_key", "dest_airport_key",
                "dep_delay", "arr_delay",
                "carrier_delay", "weather_delay", "nas_delay", "security_delay", "late_aircraft_delay",
                "primary_delay_cause"
            )
        )
        df_fact_delays.write.mode("overwrite").parquet(os.path.join(GOLD_DIR, "fact_delays"))

        # -------------------------------------------------------------
        # 8. DAILY_CARRIER_KPIS (Business Rollup)
        # -------------------------------------------------------------
        print("Generating Gold Rollup: DAILY_CARRIER_KPIS...")
        df_carrier_kpis = (
            df_flights.groupBy("flight_date", "carrier_code")
            .agg(
                F.count("flight_id").alias("total_flights"),
                F.sum(F.when(F.col("cancelled") == 0, 1).otherwise(0)).alias("completed_flights"),
                F.sum("cancelled").alias("cancelled_flights"),
                F.sum("diverted").alias("diverted_flights"),
                F.round(F.avg(F.when(F.col("cancelled") == 0, F.col("dep_delay"))), 2).alias("avg_dep_delay"),
                F.round(F.avg(F.when(F.col("cancelled") == 0, F.col("arr_delay"))), 2).alias("avg_arr_delay"),
                F.round((F.sum(F.when((F.col("cancelled") == 0) & (F.col("dep_delay") <= 0), 1).otherwise(0)) / F.count("flight_id")) * 100, 2).alias("on_time_departure_pct"),
                F.round((F.sum(F.when((F.col("cancelled") == 0) & (F.col("arr_delay") < 15), 1).otherwise(0)) / F.count("flight_id")) * 100, 2).alias("on_time_arrival_pct_otp15"),
                F.round((F.sum(F.when(F.col("cancelled") == 0, 1).otherwise(0)) / F.count("flight_id")) * 100, 2).alias("completion_rate_pct")
            )
            .orderBy("flight_date", "carrier_code")
        )
        df_carrier_kpis.write.mode("overwrite").parquet(os.path.join(GOLD_DIR, "daily_carrier_kpis"))

        # -------------------------------------------------------------
        # 9. ROUTE_PERFORMANCE_METRICS (With Window Ranking)
        # -------------------------------------------------------------
        print("Generating Gold Rollup: ROUTE_PERFORMANCE_METRICS with Window Ranking...")
        route_agg = (
            df_flights.filter(F.col("cancelled") == 0)
            .groupBy("origin_airport", "dest_airport")
            .agg(
                F.count("flight_id").alias("flight_volume"),
                F.round(F.avg("arr_delay"), 2).alias("avg_arr_delay"),
                F.round(F.avg("dep_delay"), 2).alias("avg_dep_delay"),
                F.round((F.sum(F.when(F.col("arr_delay") >= 15, 1).otherwise(0)) / F.count("flight_id")) * 100, 2).alias("delayed_flight_rate_pct")
            )
        )
        
        # Apply Window Ranking per Origin
        origin_window = Window.partitionBy("origin_airport").orderBy(F.asc("avg_arr_delay"))
        df_route_metrics = (
            route_agg
            .withColumn("origin_delay_rank", F.dense_rank().over(origin_window))
            .withColumn("route_code", F.concat_ws("-", F.col("origin_airport"), F.col("dest_airport")))
        )
        df_route_metrics.write.mode("overwrite").parquet(os.path.join(GOLD_DIR, "route_performance_metrics"))

        print("✅ Gold Layer Aggregations successfully generated.")
    finally:
        stop_spark_session(spark)

if __name__ == "__main__":
    run_gold_aggregations()
