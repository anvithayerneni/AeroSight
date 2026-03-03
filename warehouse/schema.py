"""
AeroSight Star-Schema Dimensional Data Warehouse DDL
Defines ANSI SQL, PostgreSQL, and DuckDB compliant Fact & Dimension schemas.
"""

# DDL for Dimensions
DDL_DIM_DATE = """
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY,
    flight_date DATE NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    is_weekend INTEGER NOT NULL
);
"""

DDL_DIM_AIRPORT = """
CREATE TABLE IF NOT EXISTS dim_airport (
    airport_key VARCHAR(10) PRIMARY KEY,
    iata VARCHAR(3) NOT NULL,
    icao VARCHAR(4),
    name VARCHAR(150) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(10) NOT NULL,
    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL,
    elev INTEGER,
    tz VARCHAR(50),
    hub VARCHAR(30),
    terminals INTEGER,
    gates INTEGER
);
"""

DDL_DIM_AIRLINE = """
CREATE TABLE IF NOT EXISTS dim_airline (
    airline_key VARCHAR(10) PRIMARY KEY,
    carrier_code VARCHAR(3) NOT NULL,
    airline_name VARCHAR(100) NOT NULL,
    callsign VARCHAR(50),
    country VARCHAR(50),
    fleet_size INTEGER,
    primary_hub VARCHAR(10)
);
"""

DDL_DIM_ROUTE = """
CREATE TABLE IF NOT EXISTS dim_route (
    route_key VARCHAR(20) PRIMARY KEY,
    origin_airport VARCHAR(10) NOT NULL,
    dest_airport VARCHAR(10) NOT NULL,
    distance_miles INTEGER NOT NULL,
    avg_scheduled_elapsed_min DOUBLE PRECISION,
    historical_flight_count INTEGER,
    distance_category VARCHAR(50)
);
"""

DDL_DIM_AIRCRAFT = """
CREATE TABLE IF NOT EXISTS dim_aircraft (
    aircraft_key VARCHAR(20) PRIMARY KEY,
    tail_number VARCHAR(20) NOT NULL,
    carrier_code VARCHAR(10),
    model VARCHAR(100),
    manufacturer VARCHAR(100),
    seat_capacity INTEGER,
    cruise_speed_knots INTEGER,
    year_manufactured INTEGER
);
"""

# DDL for Facts
DDL_FACT_FLIGHTS = """
CREATE TABLE IF NOT EXISTS fact_flights (
    flight_id VARCHAR(50) PRIMARY KEY,
    date_key INTEGER,
    flight_date DATE NOT NULL,
    carrier_key VARCHAR(10) NOT NULL,
    flight_number INTEGER NOT NULL,
    aircraft_key VARCHAR(20),
    origin_airport_key VARCHAR(10) NOT NULL,
    dest_airport_key VARCHAR(10) NOT NULL,
    route_key VARCHAR(20) NOT NULL,
    crs_dep_time INTEGER NOT NULL,
    dep_time INTEGER,
    dep_delay DOUBLE PRECISION,
    taxi_out DOUBLE PRECISION,
    wheels_off INTEGER,
    wheels_on INTEGER,
    taxi_in DOUBLE PRECISION,
    crs_arr_time INTEGER NOT NULL,
    arr_time INTEGER,
    arr_delay DOUBLE PRECISION,
    cancelled INTEGER NOT NULL DEFAULT 0,
    cancellation_code VARCHAR(5),
    diverted INTEGER NOT NULL DEFAULT 0,
    crs_elapsed_time INTEGER,
    actual_elapsed_time DOUBLE PRECISION,
    air_time DOUBLE PRECISION,
    distance INTEGER NOT NULL,
    is_delayed_15 INTEGER NOT NULL DEFAULT 0,
    is_delayed_45 INTEGER NOT NULL DEFAULT 0,
    is_severe_delay INTEGER NOT NULL DEFAULT 0,
    origin_temp_f DOUBLE PRECISION,
    origin_wind_mph DOUBLE PRECISION,
    origin_visibility_miles DOUBLE PRECISION,
    origin_weather_condition VARCHAR(50),
    dest_temp_f DOUBLE PRECISION,
    dest_wind_mph DOUBLE PRECISION,
    dest_visibility_miles DOUBLE PRECISION,
    dest_weather_condition VARCHAR(50)
);
"""

DDL_FACT_DELAYS = """
CREATE TABLE IF NOT EXISTS fact_delays (
    flight_id VARCHAR(50) PRIMARY KEY,
    date_key INTEGER,
    carrier_key VARCHAR(10) NOT NULL,
    origin_airport_key VARCHAR(10) NOT NULL,
    dest_airport_key VARCHAR(10) NOT NULL,
    dep_delay DOUBLE PRECISION NOT NULL,
    arr_delay DOUBLE PRECISION NOT NULL,
    carrier_delay DOUBLE PRECISION DEFAULT 0.0,
    weather_delay DOUBLE PRECISION DEFAULT 0.0,
    nas_delay DOUBLE PRECISION DEFAULT 0.0,
    security_delay DOUBLE PRECISION DEFAULT 0.0,
    late_aircraft_delay DOUBLE PRECISION DEFAULT 0.0,
    primary_delay_cause VARCHAR(50) NOT NULL
);
"""

DDL_FACT_BAGGAGE = """
CREATE TABLE IF NOT EXISTS fact_baggage (
    event_id VARCHAR(50) PRIMARY KEY,
    flight_id VARCHAR(50) NOT NULL,
    carrier_code VARCHAR(10) NOT NULL,
    origin_airport VARCHAR(10) NOT NULL,
    dest_airport VARCHAR(10) NOT NULL,
    total_checked_bags INTEGER NOT NULL,
    loaded_bags INTEGER NOT NULL,
    delayed_bags INTEGER NOT NULL,
    mishandled_bag_rate_pct DOUBLE PRECISION NOT NULL,
    avg_carousel_wait_min DOUBLE PRECISION NOT NULL,
    timestamp TIMESTAMP NOT NULL
);
"""

ALL_DDL = [
    DDL_DIM_DATE,
    DDL_DIM_AIRPORT,
    DDL_DIM_AIRLINE,
    DDL_DIM_ROUTE,
    DDL_DIM_AIRCRAFT,
    DDL_FACT_FLIGHTS,
    DDL_FACT_DELAYS,
    DDL_FACT_BAGGAGE,
]
