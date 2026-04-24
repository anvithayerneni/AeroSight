# AeroSight — Business Requirements Document (BRD)

## 1. Executive Context & Problem Statement
Commercial airline network operations face significant volatility due to weather disruptions, airport runway and gate congestion, cascade aircraft routing delays, and maintenance turnaround bottlenecks. Operational disruptions cost the global aviation industry over $30B annually in direct fuel, crew overtime, passenger re-accommodation, and FAA slot penalties.

**AeroSight** was commissioned to establish an integrated **Operations Intelligence & Data Platform** that:
1. Unifies batch historical reporting with real-time operational event streaming.
2. Implements a multi-tier Medallion Lakehouse (Bronze, Silver, Gold) with schema governance.
3. Quantifies delay root causes using statistical hypothesis testing and Machine Learning.
4. Delivers actionable operational intelligence via sub-second API telemetry and executive Excel scorecards.

---

## 2. Stakeholder Personas & Core Objectives

| Stakeholder Persona | Operational Responsibility | Primary Platform Requirements |
| :--- | :--- | :--- |
| **VP of Flight Operations** | Network on-time punctuality (A14/D0) & completion rate | Executive dashboard, daily OTP-15 trends, carrier benchmarking |
| **Director of Network Planning** | Route profitability, turnaround buffers, schedule block padding | Route corridor bottleneck rankings, delay variance analysis |
| **Airport Station Managers** | Gate turnaround, ramp taxi-out latency, ground staffing | Origin airport taxi-out congestion metrics, baggage wait time metrics |
| **Chief Operations Officer (COO)** | Board-level reporting, regulatory DOT compliance, cost minimization | Downloadable audit-ready Excel reports, automated SLA governance |
| **Operations Data / ML Engineers**| Predictive alerting, automated pipeline retraining | Fast REST inference APIs, Kafka event ingestion, PySpark lakehouse |

---

## 3. Functional Requirements

1. **Data Ingestion & Lakehouse Pipeline**:
   - Ingest raw FAA / US DOT Bureau of Transportation Statistics (BTS) On-Time Performance feeds.
   - Enforce Bronze/Silver/Gold data lakehouse structure with audit columns (`_ingestion_id`, `_timestamp`).
   - Standardize time formats, detect duplicates, and quarantine corrupted records (Quality Gate >= 95%).
2. **Streaming Event Hub**:
   - Replay operational flight events via Kafka topics (`flights`, `flight_status`, `airport_events`, `weather_events`).
   - Support accelerated simulation speeds (1x, 10x, 50x) with zero-cost fallback for local developer laptops.
3. **Advanced SQL & Dimensional Data Warehouse**:
   - Star Schema dimensional model with fact tables (`FACT_FLIGHTS`, `FACT_DELAYS`, `FACT_BAGGAGE`) and dimension tables (`DIM_DATE`, `DIM_AIRPORT`, `DIM_AIRLINE`, `DIM_ROUTE`, `DIM_AIRCRAFT`).
   - Advanced SQL window functions for turnaround tracking, route ranking, and rolling averages.
4. **Predictive Intelligence & Anomaly Detection**:
   - Machine Learning models for flight delay probability classification and duration regression.
   - Unsupervised Isolation Forest to detect abnormal turnaround times and taxi bottlenecks.
   - 14-day network demand forecasting with confidence intervals.
5. **Interactive Operations Portal & Executive Reporting**:
   - High performance React + TypeScript web interface with real-time flight search, radar telemetry, and ML tool.
   - Automated openpyxl generation of executive Excel workbooks with native charts and formula summaries.
