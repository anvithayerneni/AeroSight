# AeroSight ✈️

> A real-time airline operations intelligence platform & flight delay prediction engine.

[![CI](https://github.com/anvithayerneni/AeroSight/actions/workflows/ci.yml/badge.svg)](https://github.com/anvithayerneni/AeroSight/actions/workflows/ci.yml)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Online-success?style=flat-square)](https://pmid-griffin-powerful-triumph.trycloudflare.com)
[![Swagger Docs](https://img.shields.io/badge/API%20Docs-Swagger-blue?style=flat-square)](https://pmid-griffin-powerful-triumph.trycloudflare.com/docs)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)

**AeroSight** processes real flight data from the US Bureau of Transportation Statistics (BTS) through a data lakehouse pipeline, loads it into an analytical warehouse, trains machine learning models to predict flight delays in real time, and serves an interactive operations dashboard.

🔗 **Live App**: [https://pmid-griffin-powerful-triumph.trycloudflare.com](https://pmid-griffin-powerful-triumph.trycloudflare.com)  
📖 **API Docs**: [https://pmid-griffin-powerful-triumph.trycloudflare.com/docs](https://pmid-griffin-powerful-triumph.trycloudflare.com/docs)

---

## Key Features

- **Lakehouse Data Pipeline**: PySpark medallion architecture (Bronze $\rightarrow$ Silver $\rightarrow$ Gold) processing flight telemetry, turnaround intervals, and airport weather.
- **OLAP Data Warehouse**: Star schema modeled in DuckDB with dimension and fact tables for sub-millisecond analytical queries.
- **Flight Delay ML Engine**: Real-time delay classification and regression models (Random Forest + Gradient Boosting) trained on BTS flight records.
- **Operations Dashboard**: React 18 + TypeScript frontend with live flight tracking, interactive delay simulator, and analytics charts.
- **Streaming Telemetry**: Kafka replay producer & Server-Sent Events (SSE) streaming live flight status updates.
- **Automated Reporting**: Excel workbooks generated with openpyxl including formatted charts and metrics.

---

## Tech Stack

| Layer | Technologies |
|---|---|
| **Data Processing** | PySpark, Delta Lake, Apache Kafka, DuckDB, Pandas |
| **Machine Learning** | scikit-learn, NumPy, SciPy (ANOVA, Welch's t-test) |
| **Backend & API** | FastAPI, Pydantic, Uvicorn, SSE |
| **Frontend UI** | React 18, TypeScript, Tailwind CSS, Recharts, Vite |
| **DevOps & Tooling** | Docker, GitHub Actions, Pytest, Ruff |

---

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend development)
- Java 17 (for PySpark)

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/anvithayerneni/AeroSight.git
cd AeroSight

# 2. Setup Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Run the full platform locally
./scripts/run_all_local.sh
```

Visit **http://localhost:8000** for the dashboard and **http://localhost:8000/docs** for the API documentation.

---

## Running Individual Components

```bash
# Run data pipeline (PySpark)
python spark/bronze_ingestion.py
python spark/silver_transformation.py
python spark/gold_aggregations.py

# Train ML models
python ml/train.py

# Run tests
pytest -v

# Generate Excel reports
python reports/generate_excel_report.py
```

---

## Project Structure

```text
aerosight/
├── analytics/        # Statistical tests (ANOVA, t-test) & SQL queries
├── backend/          # FastAPI REST endpoints & SSE streaming
├── data/             # Raw BTS flight samples & DuckDB warehouse
├── frontend/         # React 18 + TypeScript dashboard (Vite + Tailwind)
├── kafka/            # Flight event replay producer
├── ml/               # Model training & inference pipeline
├── reports/          # Excel workbook generator (openpyxl)
├── spark/            # Medallion lakehouse PySpark jobs
├── tests/            # Automated pytest suite (unit & integration)
└── docker-compose.yml
```

---

## Dataset

This project uses flight on-time performance data from the **US Bureau of Transportation Statistics (BTS)**. A 30,000-record sample is included in `data/sample/flights_sample.csv` for immediate local execution.

---

## License

Distributed under the MIT License. See `LICENSE` for details.
