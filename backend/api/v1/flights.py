"""
AeroSight Flights API Endpoints
"""


from fastapi import APIRouter, HTTPException, Query

from warehouse.db import get_db

router = APIRouter(prefix="/flights", tags=["Flights"])

@router.get("", summary="Get Paginated Flight Operations Records")
def get_flights(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    carrier: str | None = None,
    origin: str | None = None,
    dest: str | None = None,
    delayed_only: bool = False,
    date: str | None = None
):
    db = get_db()
    where_clauses = ["1=1"]
    params = []

    if carrier:
        where_clauses.append("carrier_key = ?")
        params.append(carrier.upper())
    if origin:
        where_clauses.append("origin_airport_key = ?")
        params.append(origin.upper())
    if dest:
        where_clauses.append("dest_airport_key = ?")
        params.append(dest.upper())
    if delayed_only:
        where_clauses.append("is_delayed_15 = 1")
    if date:
        where_clauses.append("flight_date = ?")
        params.append(date)

    where_sql = " AND ".join(where_clauses)
    
    count_query = f"SELECT COUNT(*) as total FROM fact_flights WHERE {where_sql}"
    total_count = db.execute_query(count_query, params)[0]["total"]

    query = f"""
    SELECT 
        flight_id,
        CAST(flight_date AS VARCHAR) AS flight_date,
        carrier_key,
        flight_number,
        aircraft_key,
        origin_airport_key,
        dest_airport_key,
        route_key,
        crs_dep_time,
        dep_time,
        dep_delay,
        taxi_out,
        crs_arr_time,
        arr_time,
        arr_delay,
        cancelled,
        cancellation_code,
        diverted,
        distance,
        is_delayed_15,
        origin_temp_f,
        origin_weather_condition
    FROM fact_flights
    WHERE {where_sql}
    ORDER BY flight_date DESC, crs_dep_time DESC
    LIMIT ? OFFSET ?
    """
    flights = db.execute_query(query, params + [limit, offset])

    return {
        "total_count": total_count,
        "limit": limit,
        "offset": offset,
        "flights": flights
    }

@router.get("/{flight_id}", summary="Get Detailed Single Flight Profile")
def get_flight_by_id(flight_id: str):
    db = get_db()
    query = "SELECT * FROM fact_flights WHERE flight_id = ?"
    rows = db.execute_query(query, [flight_id])
    if not rows:
        raise HTTPException(status_code=404, detail=f"Flight {flight_id} not found")
    
    flight = rows[0]
    # Check if delay details exist
    delay_query = "SELECT * FROM fact_delays WHERE flight_id = ?"
    delay_rows = db.execute_query(delay_query, [flight_id])
    flight["delay_breakdown"] = delay_rows[0] if delay_rows else None

    return flight
