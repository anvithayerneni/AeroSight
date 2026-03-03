-- ============================================================================
-- AeroSight SQL Analytics: Airline Carrier Performance & Reliability
-- Demonstrates: CTEs, Window Ranking, Conditional Aggregation, Cause Breakdown
-- ============================================================================

WITH carrier_base_stats AS (
    SELECT 
        f.carrier_key AS carrier_code,
        a.airline_name,
        a.fleet_size,
        a.primary_hub,
        COUNT(f.flight_id) AS total_flights,
        SUM(CASE WHEN f.cancelled = 0 THEN 1 ELSE 0 END) AS operated_flights,
        SUM(f.cancelled) AS cancelled_flights,
        SUM(f.diverted) AS diverted_flights,
        ROUND(AVG(CASE WHEN f.cancelled = 0 THEN f.dep_delay END), 2) AS avg_dep_delay,
        ROUND(AVG(CASE WHEN f.cancelled = 0 THEN f.arr_delay END), 2) AS avg_arr_delay,
        ROUND((SUM(CASE WHEN f.cancelled = 0 AND f.dep_delay <= 0 THEN 1 ELSE 0 END)::DOUBLE / COUNT(f.flight_id)) * 100, 2) AS on_time_departure_pct,
        ROUND((SUM(CASE WHEN f.cancelled = 0 AND f.arr_delay < 15 THEN 1 ELSE 0 END)::DOUBLE / COUNT(f.flight_id)) * 100, 2) AS on_time_arrival_otp15_pct,
        ROUND((SUM(CASE WHEN f.cancelled = 0 THEN 1 ELSE 0 END)::DOUBLE / COUNT(f.flight_id)) * 100, 2) AS completion_rate_pct
    FROM fact_flights f
    LEFT JOIN dim_airline a ON f.carrier_key = a.airline_key
    GROUP BY f.carrier_key, a.airline_name, a.fleet_size, a.primary_hub
),
carrier_delay_causes AS (
    SELECT 
        carrier_key AS carrier_code,
        COUNT(flight_id) AS delayed_flight_count,
        ROUND(SUM(carrier_delay), 1) AS total_carrier_delay_min,
        ROUND(SUM(weather_delay), 1) AS total_weather_delay_min,
        ROUND(SUM(nas_delay), 1) AS total_nas_delay_min,
        ROUND(SUM(late_aircraft_delay), 1) AS total_late_aircraft_delay_min,
        ROUND(SUM(security_delay), 1) AS total_security_delay_min,
        ROUND(AVG(arr_delay), 2) AS avg_delay_when_delayed_min
    FROM fact_delays
    GROUP BY carrier_key
)
SELECT 
    b.carrier_code,
    b.airline_name,
    b.fleet_size,
    b.primary_hub,
    b.total_flights,
    b.operated_flights,
    b.cancelled_flights,
    b.completion_rate_pct,
    b.on_time_departure_pct,
    b.on_time_arrival_otp15_pct,
    b.avg_dep_delay,
    b.avg_arr_delay,
    d.delayed_flight_count,
    ROUND((d.delayed_flight_count::DOUBLE / b.total_flights) * 100, 2) AS delayed_flight_ratio_pct,
    d.total_carrier_delay_min,
    d.total_weather_delay_min,
    d.total_nas_delay_min,
    d.total_late_aircraft_delay_min,
    -- Carrier Reliability Rank (highest OTP-15 first)
    DENSE_RANK() OVER (ORDER BY b.on_time_arrival_otp15_pct DESC) AS reliability_rank
FROM carrier_base_stats b
LEFT JOIN carrier_delay_causes d ON b.carrier_code = d.carrier_code
ORDER BY b.total_flights DESC;
