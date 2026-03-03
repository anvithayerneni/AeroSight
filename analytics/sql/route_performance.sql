-- ============================================================================
-- AeroSight SQL Analytics: Route Corridor Performance & Bottleneck Analysis
-- Demonstrates: CTEs, Window Functions, DENSE_RANK, Quantiles, Distance Segmentation
-- ============================================================================

WITH route_metrics AS (
    SELECT 
        f.route_key,
        f.origin_airport_key AS origin,
        f.dest_airport_key AS dest,
        r.distance_miles,
        r.distance_category,
        COUNT(f.flight_id) AS total_flights,
        SUM(f.cancelled) AS cancelled_flights,
        ROUND((SUM(f.cancelled)::DOUBLE / COUNT(f.flight_id)) * 100, 2) AS cancellation_rate_pct,
        ROUND(AVG(CASE WHEN f.cancelled = 0 THEN f.arr_delay END), 2) AS avg_arr_delay,
        ROUND(AVG(CASE WHEN f.cancelled = 0 THEN f.dep_delay END), 2) AS avg_dep_delay,
        ROUND((SUM(CASE WHEN f.cancelled = 0 AND f.arr_delay < 15 THEN 1 ELSE 0 END)::DOUBLE / COUNT(f.flight_id)) * 100, 2) AS on_time_arrival_pct,
        ROUND(AVG(CASE WHEN f.cancelled = 0 THEN f.actual_elapsed_time END), 1) AS avg_actual_elapsed_min,
        ROUND(AVG(CASE WHEN f.cancelled = 0 THEN f.air_time END), 1) AS avg_air_time_min
    FROM fact_flights f
    LEFT JOIN dim_route r ON f.route_key = r.route_key
    GROUP BY f.route_key, f.origin_airport_key, f.dest_airport_key, r.distance_miles, r.distance_category
    HAVING COUNT(f.flight_id) >= 10
)
SELECT 
    route_key,
    origin,
    dest,
    distance_miles,
    distance_category,
    total_flights,
    cancelled_flights,
    cancellation_rate_pct,
    avg_arr_delay,
    avg_dep_delay,
    on_time_arrival_pct,
    avg_actual_elapsed_min,
    avg_air_time_min,
    -- Top delayed routes nationwide
    DENSE_RANK() OVER (ORDER BY avg_arr_delay DESC) AS nationwide_delay_rank,
    -- Top delayed routes from specific origin
    DENSE_RANK() OVER (PARTITION BY origin ORDER BY avg_arr_delay DESC) AS origin_delay_rank
FROM route_metrics
ORDER BY total_flights DESC, avg_arr_delay DESC;
