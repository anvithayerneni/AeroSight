-- ============================================================================
-- AeroSight SQL Analytics: Root Cause Delay Breakdown & Weather Correlation
-- Demonstrates: Conditional Aggregation, Cause Attribution, Weather Segmentations
-- ============================================================================

WITH delay_cause_totals AS (
    SELECT 
        primary_delay_cause,
        COUNT(flight_id) AS flight_count,
        ROUND(SUM(dep_delay), 1) AS total_dep_delay_min,
        ROUND(SUM(arr_delay), 1) AS total_arr_delay_min,
        ROUND(AVG(arr_delay), 2) AS avg_delay_duration_min,
        ROUND(SUM(carrier_delay), 1) AS total_carrier_min,
        ROUND(SUM(weather_delay), 1) AS total_weather_min,
        ROUND(SUM(nas_delay), 1) AS total_nas_min,
        ROUND(SUM(late_aircraft_delay), 1) AS total_late_aircraft_min
    FROM fact_delays
    GROUP BY primary_delay_cause
),
overall_delay AS (
    SELECT SUM(arr_delay) AS system_total_delay_min FROM fact_delays
)
SELECT 
    d.primary_delay_cause,
    d.flight_count,
    d.total_arr_delay_min,
    d.avg_delay_duration_min,
    ROUND((d.total_arr_delay_min / o.system_total_delay_min) * 100, 2) AS pct_of_total_system_delay,
    d.total_carrier_min,
    d.total_weather_min,
    d.total_nas_min,
    d.total_late_aircraft_min
FROM delay_cause_totals d
CROSS JOIN overall_delay o
ORDER BY d.total_arr_delay_min DESC;
