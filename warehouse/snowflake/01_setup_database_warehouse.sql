-- ============================================================================
-- AeroSight Snowflake Warehouse Setup
-- 01_setup_database_warehouse.sql
-- ============================================================================

-- 1. Create Dedicated Analytical Warehouse
CREATE WAREHOUSE IF NOT EXISTS AEROSIGHT_WH
    WITH WAREHOUSE_SIZE = 'X-SMALL'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Virtual warehouse for AeroSight flight operations analytics';

-- 2. Create Database and Schemas
CREATE DATABASE IF NOT EXISTS AEROSIGHT_DB;

USE DATABASE AEROSIGHT_DB;

-- Create Bronze, Silver, and Gold Medallion Schemas
CREATE SCHEMA IF NOT EXISTS BRONZE COMMENT = 'Raw ingestion layer';
CREATE SCHEMA IF NOT EXISTS SILVER COMMENT = 'Cleaned and standardized operational data';
CREATE SCHEMA IF NOT EXISTS GOLD COMMENT = 'Dimensional Star Schema and Business KPI datamarts';

-- Set Search Path to Gold Schema
USE SCHEMA GOLD;
