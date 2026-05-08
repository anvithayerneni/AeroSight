"""
AeroSight Airflow Analytics & Reporting DAG: analytics_pipeline
Orchestrates executive reporting generation and periodic ML model refresh.
"""

from datetime import datetime, timedelta

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
    "owner": "aerosight_analytics",
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

def generate_reports():
    from reports.generator import ReportGenerator
    gen = ReportGenerator()
    gen.generate_all_reports()

def retrain_models():
    from ml.train import train_all_models
    train_all_models()

dag = DAG(
    "analytics_pipeline",
    default_args=default_args,
    description="Analytics Reporting & ML Retraining Orchestration",
    schedule_interval="@weekly",
    catchup=False,
    tags=["aerosight", "reporting", "ml"],
)

with dag:
    task_reports = PythonOperator(
        task_id="generate_executive_excel_reports",
        python_callable=generate_reports,
    )

    task_ml = PythonOperator(
        task_id="retrain_delay_and_anomaly_models",
        python_callable=retrain_models,
    )

    task_reports >> task_ml
