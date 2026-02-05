"""
AeroSight Apache Spark Session Factory
Configures a lightweight, Apple Silicon M3 memory-optimized PySpark session.
"""

import os
import sys
from pyspark.sql import SparkSession

# Ensure JAVA_HOME points to Java 17 LTS if installed in Homebrew
if "JAVA_HOME" not in os.environ:
    brew_jdk = "/opt/homebrew/opt/openjdk@17"
    if os.path.exists(brew_jdk):
        os.environ["JAVA_HOME"] = brew_jdk

def get_spark_session(app_name: str = "AeroSight-DataPlatform", enable_delta: bool = False) -> SparkSession:
    """
    Creates and returns a memory-conscious SparkSession configured for local Apple Silicon.
    - driver memory: 2GB
    - shuffle partitions: 4 (prevents partition explosion on local machines)
    - dynamic partition pruning & AQE enabled
    """
    builder = (
        SparkSession.builder
        .appName(app_name)
        .master("local[2]")
        .config("spark.driver.memory", "2g")
        .config("spark.executor.memory", "2g")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.default.parallelism", "4")
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
        .config("spark.ui.enabled", "false") # Disable UI to save ports and memory
        .config("spark.sql.execution.arrow.pyspark.enabled", "true")
    )

    if enable_delta:
        builder = (
            builder
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
            .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        )

    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    return spark

def stop_spark_session(spark: SparkSession):
    """Safely stops and cleans up the active Spark session."""
    if spark:
        try:
            spark.stop()
        except Exception:
            pass
