#!/usr/bin/env bash
# ============================================================================
# Run AeroSight PySpark Pipeline
# ============================================================================
set -e
export PYTHONPATH=.
if [ -d "/opt/homebrew/opt/openjdk@17" ]; then
    export JAVA_HOME="/opt/homebrew/opt/openjdk@17"
fi

echo "Running Bronze Ingestion..."
python3 spark/bronze_ingestion.py

echo "Running Silver Transformations..."
python3 spark/silver_transformation.py

echo "Running Gold Aggregations..."
python3 spark/gold_aggregations.py

echo "Updating Feature Store..."
python3 spark/feature_store.py

echo "Reloading Warehouse..."
python3 warehouse/loader.py

echo "✅ PySpark Lakehouse Pipeline completed successfully!"
