#!/usr/bin/env bash
# ============================================================================
# AeroSight — End-to-End Local Bootstrap Script
# ============================================================================
set -e

echo "🚀 [1/6] Setting up environment..."
export PYTHONPATH=.
if [ -d "/opt/homebrew/opt/openjdk@17" ]; then
    export JAVA_HOME="/opt/homebrew/opt/openjdk@17"
fi

echo "📊 [2/6] Generating Sample Aviation Dataset (30,000 BTS-compliant records)..."
python3 data/generate_dataset.py

echo "⚡ [3/6] Running PySpark Medallion Lakehouse Pipeline..."
python3 spark/bronze_ingestion.py
python3 spark/silver_transformation.py
python3 spark/gold_aggregations.py
python3 spark/feature_store.py

echo "🏛️ [4/6] Loading Star-Schema Data Warehouse (DuckDB)..."
python3 warehouse/loader.py

echo "🤖 [5/6] Training Machine Learning Models (Delay, Anomaly, Forecast)..."
python3 ml/train.py

echo "📑 [6/6] Generating Styled Business Excel & CSV Reports..."
python3 reports/generator.py

echo "✅ AeroSight Pipeline Ready! Starting FastAPI Backend on http://localhost:8000 (Open /docs for Swagger UI)..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
