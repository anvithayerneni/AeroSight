.PHONY: help setup data spark warehouse ml reports test run docker-core docker-streaming docker-full clean

help:
	@echo "AeroSight — Airline Operations Intelligence & Data Platform"
	@echo "------------------------------------------------------------"
	@echo "make setup          Install Python & Frontend dependencies"
	@echo "make data           Generate/Refresh sample aviation dataset"
	@echo "make spark          Execute PySpark Bronze -> Silver -> Gold pipeline"
	@echo "make warehouse      Load Gold tables into Star-Schema DuckDB"
	@echo "make ml             Train Machine Learning models (Delay, Anomaly, Forecast)"
	@echo "make reports        Generate Excel business reports with openpyxl"
	@echo "make test           Run all unit, integration, and API tests via pytest"
	@echo "make verify         Run comprehensive end-to-end verification script"
	@echo "make run            Start FastAPI server (http://localhost:8000)"
	@echo "make docker-core    Start Core stack (FastAPI + Postgres + React) in Docker"
	@echo "make docker-full    Start Full stack (Kafka, Airflow, Spark, Backend, Frontend)"

setup:
	pip install -r requirements.txt
	cd frontend && npm install && npm run build

data:
	python3 data/generate_dataset.py

spark:
	export PYTHONPATH=. && python3 spark/bronze_ingestion.py && python3 spark/silver_transformation.py && python3 spark/gold_aggregations.py && python3 spark/feature_store.py

warehouse:
	export PYTHONPATH=. && python3 warehouse/loader.py

ml:
	export PYTHONPATH=. && python3 ml/train.py

reports:
	export PYTHONPATH=. && python3 reports/generator.py

test:
	export PYTHONPATH=. && pytest -v

verify:
	export PYTHONPATH=. && python3 scripts/verify_system.py

run:
	uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

docker-core:
	docker compose --profile core up --build -d

docker-streaming:
	docker compose --profile streaming up -d

docker-full:
	docker compose --profile full up --build -d

clean:
	rm -rf .pytest_cache spark-warehouse derby.log
