"""
AeroSight Business KPI Engine
Computes granular operational, airport, airline, and route KPIs from the Data Warehouse.
"""

from typing import Dict, Any, List, Optional
from warehouse.db import get_db

class KPIEngine:
    def __init__(self, db_manager=None):
        self.db = db_manager or get_db()

    def get_executive_summary(self) -> Dict[str, Any]:
        """Returns top-level executive KPI scorecard."""
        query = """
        SELECT 
            COUNT(flight_id) AS total_flights,
            SUM(CASE WHEN cancelled = 0 THEN 1 ELSE 0 END) AS operated_flights,
            SUM(cancelled) AS cancelled_flights,
            SUM(diverted) AS diverted_flights,
            SUM(CASE WHEN is_delayed_15 = 1 THEN 1 ELSE 0 END) AS delayed_flights,
            ROUND(AVG(CASE WHEN cancelled = 0 THEN dep_delay END), 2) AS avg_dep_delay,
            ROUND(AVG(CASE WHEN cancelled = 0 THEN arr_delay END), 2) AS avg_arr_delay,
            ROUND((SUM(CASE WHEN cancelled = 0 AND dep_delay <= 0 THEN 1 ELSE 0 END)::DOUBLE / COUNT(flight_id)) * 100, 2) AS on_time_departure_pct,
            ROUND((SUM(CASE WHEN cancelled = 0 AND arr_delay < 15 THEN 1 ELSE 0 END)::DOUBLE / COUNT(flight_id)) * 100, 2) AS on_time_arrival_otp15_pct,
            ROUND((SUM(CASE WHEN cancelled = 0 THEN 1 ELSE 0 END)::DOUBLE / COUNT(flight_id)) * 100, 2) AS completion_rate_pct,
            ROUND((SUM(cancelled)::DOUBLE / COUNT(flight_id)) * 100, 2) AS cancellation_rate_pct,
            SUM(CASE WHEN cancelled = 0 THEN distance END) AS total_distance_flown_miles
        FROM fact_flights;
        """
        rows = self.db.execute_query(query)
        res = rows[0] if rows else {}

        # Baggage KPIs
        baggage_query = """
        SELECT 
            SUM(total_checked_bags) AS total_checked_bags,
            SUM(delayed_bags) AS delayed_bags,
            ROUND(AVG(avg_carousel_wait_min), 1) AS avg_carousel_wait_min
        FROM fact_baggage;
        """
        bag_rows = self.db.execute_query(baggage_query)
        if bag_rows and bag_rows[0]["total_checked_bags"]:
            b = bag_rows[0]
            res["total_bags_checked"] = b["total_checked_bags"]
            res["mishandled_bag_rate_pct"] = round((b["delayed_bags"] / b["total_checked_bags"]) * 100, 2) if b["total_checked_bags"] else 0.0
            res["avg_baggage_wait_min"] = b["avg_carousel_wait_min"]
        else:
            res["total_bags_checked"] = 0
            res["mishandled_bag_rate_pct"] = 0.0
            res["avg_baggage_wait_min"] = 0.0

        return res

    def get_carrier_leaderboard(self) -> List[Dict[str, Any]]:
        """Returns carrier reliability and punctuality rankings."""
        query = """
        SELECT 
            f.carrier_key AS carrier_code,
            a.airline_name,
            a.fleet_size,
            a.primary_hub,
            COUNT(f.flight_id) AS total_flights,
            ROUND(AVG(CASE WHEN f.cancelled = 0 THEN f.arr_delay END), 2) AS avg_arr_delay,
            ROUND(AVG(CASE WHEN f.cancelled = 0 THEN f.dep_delay END), 2) AS avg_dep_delay,
            ROUND((SUM(CASE WHEN f.cancelled = 0 AND f.arr_delay < 15 THEN 1 ELSE 0 END)::DOUBLE / COUNT(f.flight_id)) * 100, 2) AS otp15_pct,
            ROUND((SUM(CASE WHEN f.cancelled = 0 THEN 1 ELSE 0 END)::DOUBLE / COUNT(f.flight_id)) * 100, 2) AS completion_rate_pct,
            DENSE_RANK() OVER (ORDER BY (SUM(CASE WHEN f.cancelled = 0 AND f.arr_delay < 15 THEN 1 ELSE 0 END)::DOUBLE / COUNT(f.flight_id)) DESC) AS rank
        FROM fact_flights f
        LEFT JOIN dim_airline a ON f.carrier_key = a.carrier_code
        GROUP BY f.carrier_key, a.airline_name, a.fleet_size, a.primary_hub
        ORDER BY total_flights DESC;
        """
        return self.db.execute_query(query)

    def get_airport_congestion_ranking(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Returns airport traffic, delay, and taxi-out congestion metrics."""
        query = f"""
        SELECT 
            f.origin_airport_key AS iata,
            ap.name AS airport_name,
            ap.city,
            ap.state,
            ap.lat,
            ap.lon,
            ap.hub,
            COUNT(f.flight_id) AS total_departures,
            ROUND(AVG(CASE WHEN f.cancelled = 0 THEN f.taxi_out END), 1) AS avg_taxi_out_min,
            ROUND(AVG(CASE WHEN f.cancelled = 0 THEN f.dep_delay END), 1) AS avg_dep_delay_min,
            ROUND((SUM(CASE WHEN f.cancelled = 0 AND f.dep_delay >= 15 THEN 1 ELSE 0 END)::DOUBLE / COUNT(f.flight_id)) * 100, 2) AS delayed_dep_pct,
            ROUND((SUM(f.cancelled)::DOUBLE / COUNT(f.flight_id)) * 100, 2) AS cancellation_rate_pct
        FROM fact_flights f
        LEFT JOIN dim_airport ap ON f.origin_airport_key = ap.iata
        GROUP BY f.origin_airport_key, ap.name, ap.city, ap.state, ap.lat, ap.lon, ap.hub
        ORDER BY total_departures DESC
        LIMIT {limit};
        """
        return self.db.execute_query(query)

    def get_delay_root_cause_breakdown(self) -> List[Dict[str, Any]]:
        """Returns aggregated delay minutes by primary root cause."""
        query = """
        SELECT 
            primary_delay_cause,
            COUNT(flight_id) AS delayed_flights,
            ROUND(SUM(arr_delay), 1) AS total_delay_minutes,
            ROUND(AVG(arr_delay), 2) AS avg_delay_duration_min,
            ROUND(SUM(carrier_delay), 1) AS carrier_minutes,
            ROUND(SUM(weather_delay), 1) AS weather_minutes,
            ROUND(SUM(nas_delay), 1) AS nas_minutes,
            ROUND(SUM(late_aircraft_delay), 1) AS late_aircraft_minutes
        FROM fact_delays
        GROUP BY primary_delay_cause
        ORDER BY total_delay_minutes DESC;
        """
        return self.db.execute_query(query)

    def get_daily_trends(self) -> List[Dict[str, Any]]:
        """Returns daily time-series flight volumes and delay trends."""
        query = """
        SELECT 
            flight_date,
            COUNT(flight_id) AS flight_volume,
            SUM(CASE WHEN cancelled = 0 THEN 1 ELSE 0 END) AS operated_volume,
            SUM(cancelled) AS cancellations,
            ROUND(AVG(CASE WHEN cancelled = 0 THEN arr_delay END), 2) AS avg_arr_delay,
            ROUND((SUM(CASE WHEN cancelled = 0 AND arr_delay < 15 THEN 1 ELSE 0 END)::DOUBLE / COUNT(flight_id)) * 100, 2) AS otp15_pct
        FROM fact_flights
        GROUP BY flight_date
        ORDER BY flight_date ASC;
        """
        return self.db.execute_query(query)
