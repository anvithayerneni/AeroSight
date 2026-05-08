"""
AeroSight Airflow Data Quality DAG: data_quality_pipeline
Audits dataset validity, range constraints, null thresholds, and generates scorecards.
"""

from datetime import datetime, timedelta

import pandas as pd

try:
    from airflow.operators.python import PythonOperator

    from airflow import DAG
except ImportError:
    class DAG:
        def __init__(self, *args, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass
    class PythonOperator:
        def __init__(self, *args, **kwargs): pass
        def __rshift__(self, other): return other
        def __rrshift__(self, other): return self

default_args = {
    "owner": "aerosight_governance",
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=3),
}

def audit_bronze_quality():
    from data_quality.reporter import DataQualityReporter
    from data_quality.validator import DataQualityValidator
    df = pd.read_csv("data/raw/flights_sample.csv")
    v = DataQualityValidator(df, dataset_name="bronze_flights")
    res = v.run_all_checks()
    r = DataQualityReporter(res)
    print(r.generate_console_summary())
    r.save_report("reports/output/bronze_quality_report.md")
    r.save_report("reports/output/bronze_quality_report.json")

def audit_warehouse_integrity():
    from warehouse.db import get_db
    db = get_db()
    res = db.execute_query("""
        SELECT 
            COUNT(*) AS total_fact_records,
            SUM(CASE WHEN origin_airport_key IS NULL THEN 1 ELSE 0 END) AS missing_origin_keys,
            SUM(CASE WHEN carrier_key IS NULL THEN 1 ELSE 0 END) AS missing_carrier_keys
        FROM fact_flights
    """)
    print("Warehouse Referential Integrity Check:", res)

dag = DAG(
    "data_quality_pipeline",
    default_args=default_args,
    description="Automated Data Quality & Schema Governance Audit",
    schedule_interval="@daily",
    catchup=False,
    tags=["aerosight", "quality", "governance"],
)

with dag:
    audit_bronze = PythonOperator(
        task_id="audit_bronze_layer_quality",
        python_callable=audit_bronze_quality,
    )

    audit_wh = PythonOperator(
        task_id="audit_warehouse_integrity",
        python_callable=audit_warehouse_integrity,
    )

    audit_bronze >> audit_wh
