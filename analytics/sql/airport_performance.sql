-- ============================================================================
-- AeroSight SQL Analytics: Airport Operational Performance
-- Demonstrates: CTEs, Window Functions, DENSE_RANK, Quantiles, Conditional Aggregations
-- ============================================================================

WITH airport_outbound_metrics AS (
    SELECT 
        f.origin_airport_key AS airport_code,
        ap.name AS airport_name,
        ap.city,
        ap.state,
        ap.hub,
        ap.gates,
        COUNT(f.flight_id) AS total_departures,
        SUM(CASE WHEN f.cancelled = 0 THEN 1 ELSE 0 END) AS operated_departures,
        SUM(f.cancelled) AS cancelled_departures,
        ROUND(AVG(CASE WHEN f.cancelled = 0 THEN f.dep_delay END), 2) AS avg_departure_delay_min,
        ROUND(AVG(CASE WHEN f.cancelled = 0 THEN f.taxi_out END), 2) AS avg_taxi_out_min,
        ROUND((SUM(CASE WHEN f.cancelled = 0 AND f.dep_delay <= 0 THEN 1 ELSE 0 END)::DOUBLE / COUNT(f.flight_id)) * 100, 2) AS on_time_departure_pct,
        ROUND((SUM(CASE WHEN f.cancelled = 0 AND f.dep_delay >= 15 THEN 1 ELSE 0 END)::DOUBLE / COUNT(f.flight_id)) * 100, 2) AS delayed_15_dep_pct,
        ROUND((SUM(CASE WHEN f.cancelled = 0 AND f.dep_delay >= 45 THEN 1 ELSE 0 END)::DOUBLE / COUNT(f.flight_id)) * 100, 2) AS severe_delay_dep_pct,
        ROUND((SUM(f.cancelled)::DOUBLE / COUNT(f.flight_id)) * 100, 2) AS cancellation_rate_pct
    FROM fact_flights f
    LEFT JOIN dim_airport ap ON f.origin_airport_key = ap.airport_key
    GROUP BY f.origin_airport_key, ap.name, ap.city, ap.state, ap.hub, ap.gates
),
airport_inbound_metrics AS (
    SELECT 
        f.dest_airport_key AS airport_code,
        COUNT(f.flight_id) AS total_arrivals,
        ROUND(AVG(CASE WHEN f.cancelled = 0 THEN f.arr_delay END), 2) AS avg_arrival_delay_min,
        ROUND(AVG(CASE WHEN f.cancelled = 0 THEN f.taxi_in END), 2) AS avg_taxi_in_min,
        ROUND((SUM(CASE WHEN f.cancelled = 0 AND f.arr_delay < 15 THEN 1 ELSE 0 END)::DOUBLE / COUNT(f.flight_id)) * 100, 2) AS on_time_arrival_otp15_pct
    FROM fact_flights f
    GROUP BY f.dest_airport_key
),
ranked_airports AS (
    SELECT 
        out_m.airport_code,
        out_m.airport_name,
        out_m.city,
        out_m.state,
        out_m.hub,
        out_m.total_departures,
        in_m.total_arrivals,
        (out_m.total_departures + COALESCE(in_m.total_arrivals, 0)) AS total_airport_movements,
        out_m.operated_departures,
        out_m.cancelled_departures,
        out_m.cancellation_rate_pct,
        out_m.avg_departure_delay_min,
        in_m.avg_arrival_delay_min,
        out_m.avg_taxi_out_min,
        in_m.avg_taxi_in_min,
        out_m.on_time_departure_pct,
        in_m.on_time_arrival_otp15_pct,
        -- Window function ranking by traffic volume
        DENSE_RANK() OVER (ORDER BY (out_m.total_departures + COALESCE(in_m.total_arrivals, 0)) DESC) AS traffic_volume_rank,
        -- Window function ranking by operational punctuality (lowest delay first)
        DENSE_RANK() OVER (PARTITION BY out_m.hub ORDER BY out_m.avg_departure_delay_min ASC) AS punctuality_rank_within_hub_tier
    FROM airport_outbound_metrics out_m
    LEFT JOIN airport_inbound_metrics in_m ON out_m.airport_code = in_m.airport_code
)
SELECT * 
FROM ranked_airports
ORDER BY total_airport_movements DESC;
