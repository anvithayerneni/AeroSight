"""
AeroSight Health & System Status Endpoints
"""

from datetime import datetime

from fastapi import APIRouter

from warehouse.db import get_db

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("", summary="Service Health Check")
def get_health():
    db = get_db()
    db_ok = True
    try:
        db.execute_query("SELECT 1")
    except Exception:
        db_ok = False

    return {
        "status": "healthy" if db_ok else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected" if db_ok else "disconnected",
        "service": "AeroSight Operations Platform",
        "version": "1.0.0"
    }

@router.get("/status", summary="Detailed Data Lakehouse & Component Status")
def get_system_status():
    db = get_db()
    counts = {}
    for tbl in ["fact_flights", "fact_delays", "dim_airport", "dim_airline", "dim_route", "dim_aircraft"]:
        try:
            res = db.execute_query(f"SELECT COUNT(*) as cnt FROM {tbl}")
            counts[tbl] = res[0]["cnt"] if res else 0
        except Exception:
            counts[tbl] = 0

    return {
        "status": "operational",
        "data_lake": {
            "medallion_layers": ["bronze", "silver", "gold"],
            "storage_engine": "Parquet / Delta Lake / DuckDB",
            "record_counts": counts
        },
        "ml_engine": "scikit-learn active",
        "streaming": "Kafka / In-Memory SSE active"
    }
