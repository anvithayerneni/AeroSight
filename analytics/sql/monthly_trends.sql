-- ============================================================================
-- AeroSight SQL Analytics: Monthly Time-Series Trends & Rolling Metrics
-- Demonstrates: LAG / LEAD, Rolling Moving Averages, MoM Volume & OTP Changes
-- ============================================================================

WITH daily_metrics AS (
    SELECT 
        f.flight_date,
        d.year,
        d.month,
        d.month_name,
        d.day_name,
        d.is_weekend,
        COUNT(f.flight_id) AS flight_volume,
        SUM(CASE WHEN f.cancelled = 0 THEN 1 ELSE 0 END) AS completed_volume,
        SUM(f.cancelled) AS cancellations,
        ROUND(AVG(CASE WHEN f.cancelled = 0 THEN f.arr_delay END), 2) AS daily_avg_arr_delay,
        ROUND((SUM(CASE WHEN f.cancelled = 0 AND f.arr_delay < 15 THEN 1 ELSE 0 END)::DOUBLE / COUNT(f.flight_id)) * 100, 2) AS daily_otp15_pct
    FROM fact_flights f
    LEFT JOIN dim_date d ON f.date_key = d.date_key
    GROUP BY f.flight_date, d.year, d.month, d.month_name, d.day_name, d.is_weekend
),
windowed_trends AS (
    SELECT 
        flight_date,
        year,
        month,
        month_name,
        day_name,
        is_weekend,
        flight_volume,
        completed_volume,
        cancellations,
        daily_avg_arr_delay,
        daily_otp15_pct,
        -- 7-Day Rolling Moving Average of Flights & Delay
        ROUND(AVG(flight_volume) OVER (ORDER BY flight_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 1) AS rolling_7day_flight_volume,
        ROUND(AVG(daily_avg_arr_delay) OVER (ORDER BY flight_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 2) AS rolling_7day_avg_delay,
        -- Prior Day Comparison
        LAG(daily_otp15_pct, 1) OVER (ORDER BY flight_date) AS prev_day_otp15_pct,
        ROUND(daily_otp15_pct - LAG(daily_otp15_pct, 1) OVER (ORDER BY flight_date), 2) AS day_over_day_otp_delta
    FROM daily_metrics
)
SELECT * 
FROM windowed_trends
ORDER BY flight_date ASC;
