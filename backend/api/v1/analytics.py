"""
AeroSight Analytics & Advanced SQL API Endpoints
"""


from fastapi import APIRouter, HTTPException

from analytics.kpi_engine import KPIEngine
from analytics.statistics import StatisticalEngine
from backend.schemas import SQLQueryRequest
from warehouse.db import get_db

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/kpis", summary="Get Executive Operations KPI Scorecard")
def get_executive_kpis():
    kpi_engine = KPIEngine()
    return kpi_engine.get_executive_summary()

@router.get("/delays", summary="Get Root-Cause Delay Breakdown")
def get_delay_breakdown():
    kpi_engine = KPIEngine()
    return kpi_engine.get_delay_root_cause_breakdown()

@router.get("/trends", summary="Get Daily Time-Series Operational Trends")
def get_trends():
    kpi_engine = KPIEngine()
    return kpi_engine.get_daily_trends()

@router.get("/statistics", summary="Get Delay Distributions & Hypothesis Testing")
def get_statistical_analysis():
    stats_engine = StatisticalEngine()
    return {
        "descriptive_statistics": stats_engine.compute_delay_descriptive_stats(),
        "correlations": stats_engine.compute_correlation_matrix(),
        "outliers": stats_engine.detect_delay_outliers(),
        "hypothesis_tests": stats_engine.run_hypothesis_tests()
    }

@router.post("/query", summary="Run Safe Read-Only SQL Query on Warehouse")
def execute_custom_sql(req: SQLQueryRequest):
    query = req.query.strip()
    # Guard against destructive queries in read-only SQL studio
    disallowed = ["DROP", "DELETE", "TRUNCATE", "UPDATE", "INSERT", "ALTER", "CREATE"]
    first_word = query.split()[0].upper()
    if first_word in disallowed:
        raise HTTPException(status_code=400, detail="Only SELECT queries are permitted in Analytics SQL Studio.")
    
    db = get_db()
    try:
        results = db.execute_query(query)
        return {
            "query": query,
            "row_count": len(results),
            "rows": results
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
