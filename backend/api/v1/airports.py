"""
AeroSight Airports API Endpoints
"""

from fastapi import APIRouter, HTTPException

from warehouse.db import get_db

router = APIRouter(prefix="/airports", tags=["Airports"])

@router.get("", summary="Get Airport Directory with Congestion Metrics")
def get_airports():
    db = get_db()
    query = """
    SELECT 
        ap.airport_key AS iata,
        ap.icao,
        ap.name,
        ap.city,
        ap.state,
        ap.lat,
        ap.lon,
        ap.hub,
        ap.gates,
        COUNT(f.flight_id) AS total_departures,
        ROUND(AVG(CASE WHEN f.cancelled = 0 THEN f.dep_delay END), 1) AS avg_dep_delay_min,
        ROUND(AVG(CASE WHEN f.cancelled = 0 THEN f.taxi_out END), 1) AS avg_taxi_out_min,
        ROUND((SUM(CASE WHEN f.cancelled = 0 AND f.dep_delay >= 15 THEN 1 ELSE 0 END)::DOUBLE / NULLIF(COUNT(f.flight_id), 0)) * 100, 1) AS delayed_dep_pct,
        ROUND((SUM(f.cancelled)::DOUBLE / NULLIF(COUNT(f.flight_id), 0)) * 100, 1) AS cancellation_rate_pct
    FROM dim_airport ap
    LEFT JOIN fact_flights f ON ap.airport_key = f.origin_airport_key
    GROUP BY ap.airport_key, ap.icao, ap.name, ap.city, ap.state, ap.lat, ap.lon, ap.hub, ap.gates
    ORDER BY total_departures DESC;
    """
    return db.execute_query(query)

@router.get("/{airport_code}", summary="Get Single Airport Operational Profile")
def get_airport_by_code(airport_code: str):
    db = get_db()
    query = "SELECT * FROM dim_airport WHERE airport_key = ?"
    rows = db.execute_query(query, [airport_code.upper()])
    if not rows:
        raise HTTPException(status_code=404, detail=f"Airport {airport_code} not found")
    
    airport = rows[0]
    # Inbound / Outbound counts
    stats_query = """
    SELECT 
        COUNT(flight_id) AS total_flights,
        ROUND(AVG(CASE WHEN cancelled = 0 THEN dep_delay END), 1) AS avg_dep_delay,
        ROUND(AVG(CASE WHEN cancelled = 0 THEN taxi_out END), 1) AS avg_taxi_out,
        ROUND((SUM(CASE WHEN cancelled = 0 AND dep_delay <= 0 THEN 1 ELSE 0 END)::DOUBLE / COUNT(flight_id)) * 100, 1) AS otp_dep_pct
    FROM fact_flights WHERE origin_airport_key = ?
    """
    stats = db.execute_query(stats_query, [airport_code.upper()])[0]
    airport["operational_stats"] = stats
    return airport
