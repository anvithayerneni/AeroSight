# Snowflake Enterprise Data Warehouse Architecture

AeroSight implements an enterprise-ready **Star-Schema Dimensional Model** engineered to run natively in Snowflake or locally via embedded DuckDB/PostgreSQL.

---

## 1. Dimensional Star Schema Architecture

```text
               +-------------------+
               |     DIM_DATE      |
               +-------------------+
                         |
                         v
+----------------+ +--------------+ +-----------------+
|  DIM_AIRLINE   | | FACT_FLIGHTS | |   DIM_AIRPORT   |
+----------------+ +--------------+ +-----------------+
       |                 |                   |
       |                 v                   |
       |           +-------------+           |
       +---------> | FACT_DELAYS | <---------+
                   +-------------+
                         ^
                         |
               +-------------------+
               |     DIM_ROUTE     |
               +-------------------+
```

---

## 2. Snowflake Deployment Instructions (Optional Cloud Step)

1. **Create Virtual Warehouse & Schemas**:
   ```sql
   !source 01_setup_database_warehouse.sql
   ```
2. **Deploy Dimension Tables**:
   ```sql
   !source 02_create_dimensions.sql
   ```
3. **Deploy Clustered Fact Tables**:
   ```sql
   !source 03_create_facts.sql
   ```
4. **Ingest Gold Parquet Lakehouse Data**:
   ```sql
   !source 04_load_gold_to_snowflake.sql
   ```

---

## 3. Power BI & Enterprise BI Integration

When connecting enterprise BI tools (Power BI, Tableau, ThoughtSpot) to AeroSight:
* **Local / Free Tier**: Connect Power BI / Superset to DuckDB or PostgreSQL.
* **Snowflake Cloud**: Connect Power BI DirectQuery or Import Mode using Snowflake Partner Connect to `AEROSIGHT_DB.GOLD.FACT_FLIGHTS`.
