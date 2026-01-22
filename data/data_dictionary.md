# AeroSight Data Dictionary & Medallion Schema Specification

## 1. Overview
AeroSight standardizes civil aviation operational datasets across a three-tier **Medallion Data Lake Architecture** (Bronze, Silver, Gold) and loads dimensional models into a **Snowflake / PostgreSQL / DuckDB** star schema.

---

## 2. Medallion Layer Schema

### Bronze Layer (`data/bronze/`)
* **Format**: Parquet / Delta Lake
* **Description**: Raw ingested records from source CSVs and Kafka event envelopes with audit metadata.

| Column | Type | Description |
| :--- | :--- | :--- |
| `_ingestion_id` | String (UUID) | Unique ingestion batch/stream identifier |
| `_ingestion_timestamp` | Timestamp | Timestamp when data was appended to data lake |
| `_source_file` | String | Source filename or Kafka topic partition offset |
| `flight_id` | String | Operational flight identifier (e.g., `FL-2024-000101`) |
| `flight_date` | String | Raw date string (`YYYY-MM-DD`) |
| `carrier_code` | String | 2-letter IATA airline code (e.g., `DL`, `AA`, `UA`) |
| `flight_number` | Integer | Flight number |
| `tail_number` | String | Aircraft tail registration code |
| `origin_airport` | String | 3-letter IATA origin airport code |
| `dest_airport` | String | 3-letter IATA destination airport code |
| `crs_dep_time` | Integer | Scheduled departure time (`HHMM`) |
| `dep_time` | Float / Int | Actual departure time (`HHMM`) |
| `dep_delay` | Float | Departure delay in minutes (negative = early) |
| `taxi_out` | Float | Taxi-out duration in minutes |
| `wheels_off` | Float / Int | Wheels-off timestamp (`HHMM`) |
| `wheels_on` | Float / Int | Wheels-on timestamp (`HHMM`) |
| `taxi_in` | Float | Taxi-in duration in minutes |
| `crs_arr_time` | Integer | Scheduled arrival time (`HHMM`) |
| `arr_time` | Float / Int | Actual arrival time (`HHMM`) |
| `arr_delay` | Float | Arrival delay in minutes (negative = early) |
| `cancelled` | Integer | Binary flag (1 = Cancelled, 0 = Operated) |
| `cancellation_code`| String | BTS cancellation reason: `A` (Carrier), `B` (Weather), `C` (NAS), `D` (Security) |
| `diverted` | Integer | Binary flag (1 = Diverted, 0 = Normal) |
| `crs_elapsed_time`| Integer | Scheduled elapsed duration in minutes |
| `actual_elapsed_time`| Float | Actual total elapsed duration in minutes |
| `air_time` | Float | Airborne flight time in minutes |
| `distance` | Integer | Great-circle nautical miles |
| `carrier_delay` | Float | Delay minutes attributed to air carrier |
| `weather_delay` | Float | Delay minutes attributed to extreme weather |
| `nas_delay` | Float | Delay minutes attributed to National Airspace System |
| `security_delay` | Float | Delay minutes attributed to TSA / security |
| `late_aircraft_delay`| Float | Delay minutes attributed to late arriving previous flight |
| `origin_temp_f` | Float | Ambient surface temperature at origin (°F) |
| `origin_wind_mph` | Float | Surface wind speed at origin (mph) |
| `origin_visibility_miles` | Float | Surface visibility distance at origin (miles) |
| `origin_weather_condition` | String | METAR weather condition (`Clear`, `Rain`, `Snow`, `Fog`, `Thunderstorm`) |
| `dest_temp_f` | Float | Ambient surface temperature at destination (°F) |
| `dest_wind_mph` | Float | Surface wind speed at destination (mph) |
| `dest_visibility_miles` | Float | Surface visibility distance at destination (miles) |
| `dest_weather_condition` | String | METAR weather condition at destination |

---

### Silver Layer (`data/silver/`)
* **Format**: Parquet / Delta Lake partitioned by `year` and `month`
* **Description**: Cleaned, validated, typed, and deduplicated records.
* **Transformations applied**:
  1. Standardized ISO timestamps (`scheduled_dep_ts`, `actual_dep_ts`, `scheduled_arr_ts`, `actual_arr_ts`).
  2. Data quality quarantine for corrupted records.
  3. Standardized delay categorization (`is_delayed_15`, `is_delayed_45`, `is_severe_delay`).
  4. Derived operational duration metrics (`turnaround_time`, `speed_mph`, `delay_variance`).
  5. Airport and airline dimension key lookups.

---

### Gold Layer (`data/gold/`) & Star-Schema Warehouse

#### Fact Tables
1. **`FACT_FLIGHTS`**: Granular flight operations fact table (grain: one row per flight).
2. **`FACT_DELAYS`**: Delay breakdown fact table (grain: one row per delayed flight with cause minutes).
3. **`FACT_BAGGAGE`**: Operational baggage performance tracking.

#### Dimension Tables
1. **`DIM_DATE`**: Date dimension with calendar attributes, quarter, day of week, holiday flags.
2. **`DIM_AIRPORT`**: Airport reference with IATA, ICAO, geographic coordinates, hub tier, elevation, timezones.
3. **`DIM_AIRLINE`**: Airline reference with callsigns, fleet size, base hub.
4. **`DIM_ROUTE`**: Origin-Destination pair dimension with distance band, direction, airspace corridor.
5. **`DIM_AIRCRAFT`**: Aircraft tail registry, manufacturer, model, capacity, engine class.
6. **`DIM_WEATHER`**: Weather condition classification and severity tier.
