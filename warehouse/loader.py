"""
AeroSight Gold to Data Warehouse Loader
Loads curated Gold Parquet tables into DuckDB / PostgreSQL Star Schema tables.
"""

import glob
import os

import duckdb

from warehouse.db import DEFAULT_DUCKDB_PATH
from warehouse.schema import ALL_DDL

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLD_DIR = os.path.join(BASE_DIR, "data", "gold")

def load_gold_to_warehouse(db_path: str = DEFAULT_DUCKDB_PATH):
    print(f"Loading Gold tables into warehouse ({db_path})...")
    conn = duckdb.connect(db_path)

    try:
        # 1. Execute DDL for all Star Schema tables
        for ddl in ALL_DDL:
            conn.execute(ddl)

        # 2. Map and load Gold Parquet tables into Star Schema
        table_mappings = [
            ("dim_date", os.path.join(GOLD_DIR, "dim_date", "*.parquet")),
            ("dim_airport", os.path.join(GOLD_DIR, "dim_airport", "*.parquet")),
            ("dim_airline", os.path.join(GOLD_DIR, "dim_airline", "*.parquet")),
            ("dim_route", os.path.join(GOLD_DIR, "dim_route", "*.parquet")),
            ("dim_aircraft", os.path.join(GOLD_DIR, "dim_aircraft", "*.parquet")),
            ("fact_flights", os.path.join(GOLD_DIR, "fact_flights", "*.parquet")),
            ("fact_delays", os.path.join(GOLD_DIR, "fact_delays", "*.parquet")),
        ]

        for table_name, parquet_pattern in table_mappings:
            matching_files = glob.glob(parquet_pattern)
            if matching_files:
                print(f"Loading {len(matching_files)} parquet file(s) into table: {table_name}...")
                conn.execute(f"DELETE FROM {table_name}")
                if table_name == "dim_aircraft":
                    conn.execute(f"""
                        INSERT INTO dim_aircraft BY NAME
                        SELECT * EXCLUDE (rn) FROM (
                            SELECT *, ROW_NUMBER() OVER (PARTITION BY aircraft_key ORDER BY year_manufactured DESC) AS rn
                            FROM read_parquet('{parquet_pattern}')
                        ) WHERE rn = 1
                    """)
                else:
                    conn.execute(f"INSERT INTO {table_name} BY NAME SELECT * FROM read_parquet('{parquet_pattern}')")
                count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                print(f"✅ {table_name}: {count:,} records loaded.")
            else:
                print(f"⚠️ No parquet files found matching {parquet_pattern}")

        # Load Baggage if available from raw/sample or bronze
        raw_baggage_csv = os.path.join(BASE_DIR, "data", "raw", "baggage_events.csv")
        if os.path.exists(raw_baggage_csv):
            conn.execute("DELETE FROM fact_baggage")
            conn.execute(f"INSERT INTO fact_baggage SELECT * FROM read_csv_auto('{raw_baggage_csv}')")
            bag_count = conn.execute("SELECT COUNT(*) FROM fact_baggage").fetchone()[0]
            print(f"✅ fact_baggage: {bag_count:,} records loaded.")

        # 3. Create Analytical Views for Fast KPI Queries
        conn.execute("""
        CREATE OR REPLACE VIEW v_carrier_monthly_summary AS
        SELECT 
            f.carrier_key,
            a.airline_name,
            d.year,
            d.month,
            d.month_name,
            COUNT(f.flight_id) AS total_flights,
            SUM(CASE WHEN f.cancelled = 0 THEN 1 ELSE 0 END) AS completed_flights,
            SUM(f.cancelled) AS cancelled_flights,
            ROUND(AVG(CASE WHEN f.cancelled = 0 THEN f.dep_delay END), 2) AS avg_dep_delay,
            ROUND(AVG(CASE WHEN f.cancelled = 0 THEN f.arr_delay END), 2) AS avg_arr_delay,
            ROUND((SUM(CASE WHEN f.cancelled = 0 AND f.arr_delay < 15 THEN 1 ELSE 0 END)::DOUBLE / COUNT(f.flight_id)) * 100, 2) AS on_time_arrival_pct
        FROM fact_flights f
        LEFT JOIN dim_airline a ON f.carrier_key = a.carrier_code
        LEFT JOIN dim_date d ON f.date_key = d.date_key
        GROUP BY f.carrier_key, a.airline_name, d.year, d.month, d.month_name
        ORDER BY d.year, d.month, total_flights DESC;
        """)

        conn.execute("""
        CREATE OR REPLACE VIEW v_airport_congestion_summary AS
        SELECT 
            f.origin_airport_key AS airport_code,
            ap.name AS airport_name,
            ap.city,
            ap.state,
            ap.hub,
            COUNT(f.flight_id) AS total_departures,
            ROUND(AVG(f.taxi_out), 1) AS avg_taxi_out_min,
            ROUND(AVG(f.dep_delay), 1) AS avg_dep_delay_min,
            ROUND((SUM(CASE WHEN f.dep_delay >= 15 THEN 1 ELSE 0 END)::DOUBLE / COUNT(f.flight_id)) * 100, 2) AS delayed_dep_pct,
            ROUND((SUM(f.cancelled)::DOUBLE / COUNT(f.flight_id)) * 100, 2) AS cancellation_rate_pct
        FROM fact_flights f
        LEFT JOIN dim_airport ap ON f.origin_airport_key = ap.iata
        GROUP BY f.origin_airport_key, ap.name, ap.city, ap.state, ap.hub
        ORDER BY total_departures DESC;
        """)

        print("✅ Data Warehouse loading and analytical views completed successfully.")
    finally:
        conn.close()

if __name__ == "__main__":
    load_gold_to_warehouse()
