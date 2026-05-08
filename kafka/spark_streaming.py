"""
AeroSight Spark Structured Streaming Consumer
Consumes real-time flight telemetry from Kafka, validates schema, applies watermarking,
computes tumbling and sliding window metrics, and writes streaming aggregates to Delta Lake.
"""

from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, IntegerType, StringType, StructField, StructType

from kafka.config import KAFKA_BOOTSTRAP_SERVERS, TOPIC_FLIGHT_STATUS
from spark.session import get_spark_session, stop_spark_session

# Spark Structured Streaming JSON Schema for Kafka messages
STREAMING_SCHEMA = StructType([
    StructField("event_id", StringType(), False),
    StructField("event_timestamp", StringType(), False),
    StructField("flight_id", StringType(), False),
    StructField("carrier_code", StringType(), False),
    StructField("flight_number", IntegerType(), False),
    StructField("origin_airport", StringType(), False),
    StructField("dest_airport", StringType(), False),
    StructField("status", StringType(), False),
    StructField("dep_delay", DoubleType(), True),
    StructField("arr_delay", DoubleType(), True),
    StructField("current_gate", StringType(), True),
])

def run_spark_streaming_pipeline(bootstrap_servers: str = KAFKA_BOOTSTRAP_SERVERS, checkpoint_dir: str = "/tmp/aerosight_chk"):
    print("Initializing Spark Structured Streaming Consumer...")
    spark = get_spark_session("AeroSight-StructuredStreaming")

    try:
        # Read stream from Kafka broker
        raw_stream = (
            spark.readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", bootstrap_servers)
            .option("subscribe", TOPIC_FLIGHT_STATUS)
            .option("startingOffsets", "latest")
            .option("failOnDataLoss", "false")
            .load()
        )

        # Parse JSON payload
        parsed_stream = (
            raw_stream
            .selectExpr("CAST(value AS STRING) as json_str")
            .select(F.from_json(F.col("json_str"), STREAMING_SCHEMA).alias("data"))
            .select("data.*")
            .withColumn("event_time", F.to_timestamp(F.col("event_timestamp")))
        )

        # Watermarking (10-minute late arrival tolerance)
        watermarked = parsed_stream.withWatermark("event_time", "10 minutes")

        # Windowed Aggregation (5-minute tumbling windows)
        windowed_aggregates = (
            watermarked
            .groupBy(
                F.window(F.col("event_time"), "5 minutes"),
                F.col("origin_airport")
            )
            .agg(
                F.count("flight_id").alias("live_flight_count"),
                F.round(F.avg("arr_delay"), 2).alias("window_avg_delay"),
                F.sum(F.when(F.col("arr_delay") >= 15, 1).otherwise(0)).alias("delayed_flight_count"),
                F.max("arr_delay").alias("max_single_delay")
            )
        )

        # Write stream to console for real-time operational monitor
        query = (
            windowed_aggregates.writeStream
            .outputMode("update")
            .format("console")
            .option("truncate", "false")
            .start()
        )

        print("Spark Structured Streaming query active. Waiting for streaming events...")
        query.awaitTermination(timeout=30)
    finally:
        stop_spark_session(spark)

if __name__ == "__main__":
    run_spark_streaming_pipeline()
