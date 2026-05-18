# Databricks Deployment & Compatibility Guide

AeroSight pipelines are architected with pure **PySpark and Delta Lake API compatibility**, enabling seamless execution across:
1. **Local Development (0-Cost)**: Memory-conscious PySpark on macOS / Apple Silicon using local file storage.
2. **Databricks Unified Analytics Platform**: Zero-code-change execution on Databricks Multi-node clusters or Single-node compute.

---

## 1. Databricks Workspace Setup

### Storage Mount Configuration
Configure your cloud object storage (Azure ADLS Gen2, AWS S3, or Google Cloud Storage) using Databricks Secrets:

```python
# Azure ADLS Gen2 Example
spark.conf.set(
    "fs.azure.account.key.<storage-account-name>.dfs.core.windows.net",
    dbutils.secrets.get(scope="aerosight-scope", key="storage-key")
)

# Set base lakehouse paths
spark.conf.set("aerosight.raw.path", "abfss://raw@<storage-account-name>.dfs.core.windows.net")
spark.conf.set("aerosight.bronze.path", "abfss://bronze@<storage-account-name>.dfs.core.windows.net")
spark.conf.set("aerosight.silver.path", "abfss://silver@<storage-account-name>.dfs.core.windows.net")
spark.conf.set("aerosight.gold.path", "abfss://gold@<storage-account-name>.dfs.core.windows.net")
```

---

## 2. Notebook Execution Order

Execute the following notebooks in sequence or orchestrate them via **Databricks Workflows (Multi-Task Jobs)**:

1. [`01_bronze_ingestion.py`](notebooks/01_bronze_ingestion.py): Ingests raw flight operational telemetry into Bronze Delta tables with audit envelopes.
2. [`02_silver_cleaning.py`](notebooks/02_silver_cleaning.py): Cleans, validates, deduplicates, and calculates windowed turnaround times.
3. [`03_gold_aggregations.py`](notebooks/03_gold_aggregations.py): Builds Star-Schema Fact & Dimension Delta tables and KPI summaries.
4. [`04_feature_store.py`](notebooks/04_feature_store.py): Computes cyclical temporal encodings and registers curated ML features.

---

## 3. Unity Catalog Integration (Optional)

To register tables into **Unity Catalog**, replace the output paths with 3-level namespace identifiers:

```sql
CREATE TABLE main.aerosight_silver.flights
USING DELTA
LOCATION 'abfss://silver@<storage-account-name>.dfs.core.windows.net/flights';
```
