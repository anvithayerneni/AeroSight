"""
AeroSight PySpark Bronze Ingestion Job
Ingests raw CSV data files, appends pipeline audit metadata, and writes raw Parquet/Delta to the Bronze layer.
"""

import os
import uuid
from datetime import datetime
from pyspark.sql import functions as F
from spark.session import get_spark_session, stop_spark_session

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
BRONZE_DIR = os.path.join(BASE_DIR, "data", "bronze")

def run_bronze_ingestion():
    batch_id = str(uuid.uuid4())
    ingestion_ts = datetime.utcnow()
    print(f"[{ingestion_ts.isoformat()}] Starting Bronze Layer Ingestion (Batch ID: {batch_id})...")

    spark = get_spark_session("AeroSight-BronzeIngestion")
    
    try:
        # Ingest Flights
        raw_flights_path = os.path.join(RAW_DIR, "flights_sample.csv")
        if os.path.exists(raw_flights_path):
            print(f"Ingesting raw flights from {raw_flights_path}...")
            df_flights = spark.read.option("header", "true").option("inferSchema", "true").csv(raw_flights_path)
            
            # Add Bronze audit metadata columns
            df_bronze_flights = (
                df_flights
                .withColumn("_ingestion_id", F.lit(batch_id))
                .withColumn("_ingestion_timestamp", F.lit(ingestion_ts))
                .withColumn("_source_file", F.lit("flights_sample.csv"))
            )
            
            bronze_flights_out = os.path.join(BRONZE_DIR, "flights")
            df_bronze_flights.write.mode("overwrite").parquet(bronze_flights_out)
            print(f"✅ Saved Bronze Flights ({df_bronze_flights.count():,} rows) to {bronze_flights_out}")

        # Ingest Airports
        raw_airports_path = os.path.join(RAW_DIR, "airports.csv")
        if os.path.exists(raw_airports_path):
            df_airports = spark.read.option("header", "true").option("inferSchema", "true").csv(raw_airports_path)
            df_bronze_airports = (
                df_airports
                .withColumn("_ingestion_id", F.lit(batch_id))
                .withColumn("_ingestion_timestamp", F.lit(ingestion_ts))
                .withColumn("_source_file", F.lit("airports.csv"))
            )
            df_bronze_airports.write.mode("overwrite").parquet(os.path.join(BRONZE_DIR, "airports"))
            print(f"✅ Saved Bronze Airports to {os.path.join(BRONZE_DIR, 'airports')}")

        # Ingest Airlines
        raw_airlines_path = os.path.join(RAW_DIR, "airlines.csv")
        if os.path.exists(raw_airlines_path):
            df_airlines = spark.read.option("header", "true").option("inferSchema", "true").csv(raw_airlines_path)
            df_bronze_airlines = (
                df_airlines
                .withColumn("_ingestion_id", F.lit(batch_id))
                .withColumn("_ingestion_timestamp", F.lit(ingestion_ts))
                .withColumn("_source_file", F.lit("airlines.csv"))
            )
            df_bronze_airlines.write.mode("overwrite").parquet(os.path.join(BRONZE_DIR, "airlines"))
            print(f"✅ Saved Bronze Airlines to {os.path.join(BRONZE_DIR, 'airlines')}")

        # Ingest Aircraft Fleet
        raw_aircraft_path = os.path.join(RAW_DIR, "aircraft.csv")
        if os.path.exists(raw_aircraft_path):
            df_aircraft = spark.read.option("header", "true").option("inferSchema", "true").csv(raw_aircraft_path)
            df_bronze_aircraft = (
                df_aircraft
                .withColumn("_ingestion_id", F.lit(batch_id))
                .withColumn("_ingestion_timestamp", F.lit(ingestion_ts))
                .withColumn("_source_file", F.lit("aircraft.csv"))
            )
            df_bronze_aircraft.write.mode("overwrite").parquet(os.path.join(BRONZE_DIR, "aircraft"))
            print(f"✅ Saved Bronze Aircraft to {os.path.join(BRONZE_DIR, 'aircraft')}")

        # Ingest Baggage Events
        raw_baggage_path = os.path.join(RAW_DIR, "baggage_events.csv")
        if os.path.exists(raw_baggage_path):
            df_baggage = spark.read.option("header", "true").option("inferSchema", "true").csv(raw_baggage_path)
            df_bronze_baggage = (
                df_baggage
                .withColumn("_ingestion_id", F.lit(batch_id))
                .withColumn("_ingestion_timestamp", F.lit(ingestion_ts))
                .withColumn("_source_file", F.lit("baggage_events.csv"))
            )
            df_bronze_baggage.write.mode("overwrite").parquet(os.path.join(BRONZE_DIR, "baggage"))
            print(f"✅ Saved Bronze Baggage Events to {os.path.join(BRONZE_DIR, 'baggage')}")

        print("Bronze Ingestion completed successfully.")
    finally:
        stop_spark_session(spark)

if __name__ == "__main__":
    run_bronze_ingestion()
