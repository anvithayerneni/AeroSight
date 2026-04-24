# AeroSight Business KPI Dictionary

This dictionary establishes strict governance and mathematical definitions for all operational, financial, and regulatory metrics across the AeroSight platform.

---

## Metric Classification Legend
* 🟢 **Observed KPI**: Direct measurements recorded in raw operational / BTS feeds.
* 🟡 **Derived KPI**: Calculated via deterministic mathematical or SQL aggregation.
* 🔵 **Estimated KPI**: Modeled using statistical inference, heuristics, or machine learning.
* 🔴 **Unavailable KPI**: Not contained in standard public BTS data; omitted to preserve integrity.

---

## 1. Flight Operations KPIs

| Metric Name | Type | Formula / Definition | Operational Business Use Case |
| :--- | :--- | :--- | :--- |
| **Total Scheduled Flights** | 🟢 Observed | `COUNT(flight_id)` | Baseline operational volume |
| **Completed Flights** | 🟢 Observed | `SUM(CASE WHEN cancelled = 0 THEN 1 ELSE 0 END)` | Volume of flights safely flown |
| **Cancelled Flights** | 🟢 Observed | `SUM(cancelled)` | Volume of unoperated flights |
| **Diverted Flights** | 🟢 Observed | `SUM(diverted)` | Flights diverted to alternate airport |
| **Completion Rate (%)** | 🟡 Derived | `(Completed Flights / Total Flights) * 100` | Operational schedule integrity |
| **Cancellation Rate (%)** | 🟡 Derived | `(Cancelled Flights / Total Flights) * 100` | Schedule disruption rate |
| **On-Time Departure (D0)** | 🟡 Derived | `SUM(CASE WHEN dep_delay <= 0 THEN 1 ELSE 0 END) / Total Flights * 100` | Ramp punctuality |
| **On-Time Arrival (OTP-15 / A14)** | 🟡 Derived | `SUM(CASE WHEN arr_delay < 15 THEN 1 ELSE 0 END) / Total Flights * 100` | Official US DOT Punctuality Benchmark |
| **Average Departure Delay** | 🟡 Derived | `AVG(dep_delay)` on operated flights | Average gate departure deviation |
| **Average Arrival Delay** | 🟡 Derived | `AVG(arr_delay)` on operated flights | Average runway arrival deviation |
| **Delay Skewness & IQR** | 🟡 Derived | `P75(arr_delay) - P25(arr_delay)` | Outlier resistance measurement |
| **Predicted Delay Risk** | 🔵 Estimated | ML Random Forest Class Probability (`is_delayed_15`) | Proactive passenger/crew alerting |
| **Direct Disruption Cost ($)**| 🔵 Estimated | `$74.24/min * Total Delay Minutes` (FAA APMT formula) | Operational cost quantification |
| **Ticket Revenue ($)** | 🔴 Unavailable | *N/A (Not published in public BTS OTP data)* | Excluded from reporting |
| **Passenger Load Factor** | 🔴 Unavailable | *N/A (Requires Form 41 T-100 Segment data)* | Excluded from reporting |

---

## 2. Airport & Station KPIs

| Metric Name | Type | Formula / Definition | Operational Business Use Case |
| :--- | :--- | :--- | :--- |
| **Airport Movement Volume** | 🟡 Derived | `Departures + Arrivals` | Total station movement volume |
| **Average Taxi-Out Time** | 🟢 Observed | `AVG(taxi_out)` in minutes | Ramp and runway queue latency |
| **Average Taxi-In Time** | 🟢 Observed | `AVG(taxi_in)` in minutes | Gate arrival ramp congestion |
| **Hub Punctuality Rank** | 🟡 Derived | `DENSE_RANK() OVER (PARTITION BY hub ORDER BY avg_dep_delay)` | Peer station benchmarking |
| **Aircraft Turnaround Time** | 🟡 Derived | `crs_dep_time(flight_N) - arr_time(flight_N-1)` for same tail | Ground gate handling efficiency |

---

## 3. Customer & Baggage Operations KPIs

| Metric Name | Type | Formula / Definition | Operational Business Use Case |
| :--- | :--- | :--- | :--- |
| **Total Checked Bags** | 🟢 Observed | `SUM(total_checked_bags)` | Station baggage throughput |
| **Mishandled Bag Rate (%)** | 🟡 Derived | `(Delayed Bags / Total Bags) * 100` | DOT 14 CFR Part 234 Compliance |
| **Avg Carousel Wait Time** | 🟡 Derived | `AVG(avg_carousel_wait_min)` in minutes | Passenger baggage claim experience |
