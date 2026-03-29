# Apache Airflow Orchestration in AeroSight

AeroSight includes three production-ready Airflow DAGs:
1. **`flight_batch_pipeline`**: End-to-end lakehouse orchestration (Raw Source Validation -> Data Quality Gate -> PySpark Bronze Ingestion -> Silver Transformation -> Gold Aggregations -> Feature Store Update -> Dimensional Warehouse Load).
2. **`data_quality_pipeline`**: Daily automated schema governance, null assertions, and scorecard publishing.
3. **`analytics_pipeline`**: Automated weekly executive Excel/CSV generation and ML model retraining.

---

## Running Airflow Locally ($0 Cost)

### Option 1: Via Docker Compose (Recommended)
```bash
docker compose --profile analytics up -d airflow-webserver airflow-scheduler
```
Access UI at `http://localhost:8080` (Credentials: `admin` / `admin`).

### Option 2: Standalone Local Mode (Zero Docker Overhead)
```bash
pip install apache-airflow
export AIRFLOW_HOME=$(pwd)/airflow
airflow standalone
```
