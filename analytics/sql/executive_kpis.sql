-- ============================================================================
-- AeroSight SQL Analytics: Executive Operational KPI Summary
-- Demonstrates: Comprehensive Business Metamart, FAA/BTS Metric Computations
-- ============================================================================

WITH core_aggregates AS (
    SELECT 
        COUNT(flight_id) AS total_flights,
        SUM(CASE WHEN cancelled = 0 THEN 1 ELSE 0 END) AS operated_flights,
        SUM(cancelled) AS cancelled_flights,
        SUM(diverted) AS diverted_flights,
        SUM(CASE WHEN is_delayed_15 = 1 THEN 1 ELSE 0 END) AS delayed_flights_count,
        SUM(CASE WHEN is_delayed_45 = 1 THEN 1 ELSE 0 END) AS major_delayed_flights_count,
        SUM(CASE WHEN is_severe_delay = 1 THEN 1 ELSE 0 END) AS severe_delayed_flights_count,
        ROUND(AVG(CASE WHEN cancelled = 0 THEN dep_delay END), 2) AS system_avg_dep_delay_min,
        ROUND(AVG(CASE WHEN cancelled = 0 THEN arr_delay END), 2) AS system_avg_arr_delay_min,
        ROUND(AVG(CASE WHEN cancelled = 0 THEN taxi_out END), 2) AS system_avg_taxi_out_min,
        ROUND(AVG(CASE WHEN cancelled = 0 THEN taxi_in END), 2) AS system_avg_taxi_in_min,
        SUM(CASE WHEN cancelled = 0 THEN distance END) AS total_flown_miles
    FROM fact_flights
),
baggage_aggregates AS (
    SELECT 
        SUM(total_checked_bags) AS total_bags_checked,
        SUM(delayed_bags) AS total_delayed_bags,
        ROUND(AVG(avg_carousel_wait_min), 1) AS avg_baggage_wait_min
    FROM fact_baggage
)
SELECT 
    c.total_flights,
    c.operated_flights,
    c.cancelled_flights,
    c.diverted_flights,
    ROUND((c.operated_flights::DOUBLE / c.total_flights) * 100, 2) AS completion_rate_pct,
    ROUND((c.cancelled_flights::DOUBLE / c.total_flights) * 100, 2) AS cancellation_rate_pct,
    ROUND(((c.total_flights - c.delayed_flights_count)::DOUBLE / c.total_flights) * 100, 2) AS on_time_arrival_otp15_pct,
    c.delayed_flights_count,
    ROUND((c.delayed_flights_count::DOUBLE / c.total_flights) * 100, 2) AS delay_rate_pct,
    c.major_delayed_flights_count,
    c.severe_delayed_flights_count,
    c.system_avg_dep_delay_min,
    c.system_avg_arr_delay_min,
    c.system_avg_taxi_out_min,
    c.system_avg_taxi_in_min,
    c.total_flown_miles,
    b.total_bags_checked,
    b.total_delayed_bags,
    ROUND((b.total_delayed_bags::DOUBLE / NULLIF(b.total_bags_checked, 0)) * 100, 2) AS baggage_mishandle_rate_pct,
    b.avg_baggage_wait_min
FROM core_aggregates c
CROSS JOIN baggage_aggregates b;
