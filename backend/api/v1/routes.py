"""
AeroSight Route Network API Endpoints
"""

from fastapi import APIRouter, Query
from warehouse.db import get_db

router = APIRouter(prefix="/routes", tags=["Routes"])

@router.get("", summary="Get Route Network Performance Directory")
def get_routes(limit: int = Query(50, ge=1, le=200)):
    db = get_db()
    query = f"""
    SELECT 
        r.route_key,
        r.origin_airport AS origin,
        r.dest_airport AS dest,
        r.distance_miles,
        r.distance_category,
        COUNT(f.flight_id) AS flight_count,
        ROUND(AVG(CASE WHEN f.cancelled = 0 THEN f.arr_delay END), 1) AS avg_arr_delay,
        ROUND(AVG(CASE WHEN f.cancelled = 0 THEN f.dep_delay END), 1) AS avg_dep_delay,
        ROUND((SUM(CASE WHEN f.cancelled = 0 AND f.arr_delay < 15 THEN 1 ELSE 0 END)::DOUBLE / NULLIF(COUNT(f.flight_id), 0)) * 100, 1) AS otp15_pct,
        ROUND((SUM(f.cancelled)::DOUBLE / NULLIF(COUNT(f.flight_id), 0)) * 100, 1) AS cancellation_rate_pct
    FROM dim_route r
    LEFT JOIN fact_flights f ON r.route_key = f.route_key
    GROUP BY r.route_key, r.origin_airport, r.dest_airport, r.distance_miles, r.distance_category
    HAVING COUNT(f.flight_id) > 0
    ORDER BY flight_count DESC
    LIMIT {limit};
    """
    return db.execute_query(query)

@router.get("/top-delayed", summary="Get Top Delayed Route Corridors")
def get_top_delayed_routes(limit: int = Query(15, ge=1, le=50)):
    db = get_db()
    query = f"""
    SELECT 
        r.route_key,
        r.origin_airport AS origin,
        r.dest_airport AS dest,
        r.distance_miles,
        COUNT(f.flight_id) AS flight_count,
        ROUND(AVG(f.arr_delay), 1) AS avg_arr_delay,
        ROUND(AVG(f.dep_delay), 1) AS avg_dep_delay,
        ROUND((SUM(CASE WHEN f.arr_delay >= 15 THEN 1 ELSE 0 END)::DOUBLE / COUNT(f.flight_id)) * 100, 1) AS delayed_flight_pct
    FROM dim_route r
    JOIN fact_flights f ON r.route_key = f.route_key
    WHERE f.cancelled = 0
    GROUP BY r.route_key, r.origin_airport, r.dest_airport, r.distance_miles
    HAVING COUNT(f.flight_id) >= 15
    ORDER BY avg_arr_delay DESC
    LIMIT {limit};
    """
    return db.execute_query(query)
