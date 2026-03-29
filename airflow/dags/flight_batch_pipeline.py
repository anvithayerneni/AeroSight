"""
AeroSight Airflow Batch Pipeline DAG: flight_batch_pipeline
Orchestrates raw extraction -> PySpark Bronze -> Silver -> Gold -> Quality Gate -> Warehouse Load.
"""

from datetime import datetime, timedelta
import os
import sys

# Airflow DAG definition
try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator
    from airflow.operators.bash import BashOperator
    from airflow.utils.task_group import TaskGroup
except ImportError:
    class DAG:
        def __init__(self, *args, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass
    class PythonOperator:
        def __init__(self, *args, **kwargs): pass
        def __rshift__(self, other): return other
        def __rrshift__(self, other): return self
    class BashOperator:
        def __init__(self, *args, **kwargs): pass
        def __rshift__(self, other): return other
    class TaskGroup:
        def __init__(self, *args, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass

default_args = {
    "owner": "aerosight_data_engineering",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

def task_verify_raw_data():
    raw_path = "data/raw/flights_sample.csv"
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"Raw source dataset missing at {raw_path}")
    print(f"Verified raw source dataset at {raw_path}")

def task_run_bronze():
    from spark.bronze_ingestion import run_bronze_ingestion
    run_bronze_ingestion()

def task_run_silver():
    from spark.silver_transformation import run_silver_transformation
    run_silver_transformation()

def task_run_gold():
    from spark.gold_aggregations import run_gold_aggregations
    run_gold_aggregations()

def task_run_feature_store():
    from spark.feature_store import run_feature_store_pipeline
    run_feature_store_pipeline()

def task_run_data_quality():
    import pandas as pd
    from data_quality.validator import DataQualityValidator
    df = pd.read_csv("data/raw/flights_sample.csv")
    validator = DataQualityValidator(df)
    res = validator.run_all_checks()
    if res["quality_score"] < 95.0:
        raise ValueError(f"Data Quality Gate Failed! Score: {res['quality_score']}%")
    print(f"Data Quality Gate Passed. Score: {res['quality_score']}%")

def task_load_warehouse():
    from warehouse.loader import load_gold_to_warehouse
    load_gold_to_warehouse()

dag = DAG(
    "flight_batch_pipeline",
    default_args=default_args,
    description="End-to-End AeroSight PySpark Lakehouse Batch Pipeline",
    schedule_interval="@daily",
    catchup=False,
    tags=["aerosight", "pyspark", "medallion", "warehouse"],
)

with dag:
    verify_raw = PythonOperator(
        task_id="verify_raw_data_sources",
        python_callable=task_verify_raw_data,
    )

    quality_check = PythonOperator(
        task_id="data_quality_gate",
        python_callable=task_run_data_quality,
    )

    bronze_job = PythonOperator(
        task_id="pyspark_bronze_ingestion",
        python_callable=task_run_bronze,
    )

    silver_job = PythonOperator(
        task_id="pyspark_silver_transformation",
        python_callable=task_run_silver,
    )

    gold_job = PythonOperator(
        task_id="pyspark_gold_aggregations",
        python_callable=task_run_gold,
    )

    features_job = PythonOperator(
        task_id="pyspark_feature_store_update",
        python_callable=task_run_feature_store,
    )

    load_wh = PythonOperator(
        task_id="load_dimensional_warehouse",
        python_callable=task_load_warehouse,
    )

    # Task Pipeline Dependencies
    verify_raw >> quality_check >> bronze_job >> silver_job >> gold_job >> [features_job, load_wh]
