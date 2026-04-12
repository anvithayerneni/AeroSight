"""
AeroSight Airlines API Endpoints
"""

from fastapi import APIRouter, HTTPException
from warehouse.db import get_db

router = APIRouter(prefix="/airlines", tags=["Airlines"])

@router.get("", summary="Get Airline Fleet & Operational Performance Leaderboard")
def get_airlines():
    db = get_db()
    query = """
    SELECT 
        a.airline_key AS carrier_code,
        a.airline_name,
        a.callsign,
        a.fleet_size,
        a.primary_hub,
        COUNT(f.flight_id) AS total_flights,
        ROUND(AVG(CASE WHEN f.cancelled = 0 THEN f.arr_delay END), 2) AS avg_arr_delay,
        ROUND(AVG(CASE WHEN f.cancelled = 0 THEN f.dep_delay END), 2) AS avg_dep_delay,
        ROUND((SUM(CASE WHEN f.cancelled = 0 AND f.arr_delay < 15 THEN 1 ELSE 0 END)::DOUBLE / NULLIF(COUNT(f.flight_id), 0)) * 100, 2) AS otp15_pct,
        ROUND((SUM(CASE WHEN f.cancelled = 0 THEN 1 ELSE 0 END)::DOUBLE / NULLIF(COUNT(f.flight_id), 0)) * 100, 2) AS completion_rate_pct
    FROM dim_airline a
    LEFT JOIN fact_flights f ON a.airline_key = f.carrier_key
    GROUP BY a.airline_key, a.airline_name, a.callsign, a.fleet_size, a.primary_hub
    ORDER BY total_flights DESC;
    """
    return db.execute_query(query)

@router.get("/{carrier_code}/stats", summary="Get Specific Carrier Operational Statistics")
def get_carrier_stats(carrier_code: str):
    db = get_db()
    c_code = carrier_code.upper()
    query = "SELECT * FROM dim_airline WHERE airline_key = ?"
    rows = db.execute_query(query, [c_code])
    if not rows:
        raise HTTPException(status_code=404, detail=f"Carrier {c_code} not found")
    
    carrier = rows[0]
    cause_query = """
    SELECT 
        ROUND(SUM(carrier_delay), 1) AS carrier_delay_min,
        ROUND(SUM(weather_delay), 1) AS weather_delay_min,
        ROUND(SUM(nas_delay), 1) AS nas_delay_min,
        ROUND(SUM(late_aircraft_delay), 1) AS late_aircraft_delay_min,
        ROUND(SUM(security_delay), 1) AS security_delay_min
    FROM fact_delays
    WHERE carrier_key = ?
    """
    causes = db.execute_query(cause_query, [c_code])
    carrier["delay_causes"] = causes[0] if causes else {}
    return carrier
