# AeroSight — Executive Summary

## Operational Audit & Lakehouse Intelligence Report
**Reporting Period**: Q1 2024 (January 1 – March 31, 2024)  
**Total Monitored Flights**: 30,000 Verified Operations  
**Audited Carriers**: 10 Major US Air Carriers  
**Audited Hub Airports**: 31 Large & Medium Commercial Hubs  

---

## 1. Top-Line Executive Key Findings

```text
+-----------------------+-----------------------+-----------------------+
|  COMPLETION RATE      |  ON-TIME ARRIVAL      |  AVG SYSTEM DELAY     |
|       97.42%          |      72.21% (OTP-15)  |      +11.12 Minutes   |
|   (29,226 Operated)   |   (7,562 Delayed >15m)|   (Std Dev: 29.8 min) |
+-----------------------+-----------------------+-----------------------+
```

1. **Overall Network Health**:
   - The commercial flight network achieved a **97.42% completion rate** (774 cancellations out of 30,000 scheduled operations).
   - **72.21% of flights arrived on-time** within the DOT standard (arrival delay < 15 minutes).
   - The median delay across all completed flights was **+0.3 minutes**, with delays heavily right-skewed (90th percentile: **+48.6 minutes**; 99th percentile: **+128.6 minutes**).

2. **Root Cause Attribution of Delay Minutes**:
   - **Late Arriving Aircraft Cascade**: Accounts for **38.4%** of all delay minutes, primarily impacting evening departure banks after 17:00.
   - **Air Carrier Controllable Operations**: Accounts for **29.1%** of delay minutes (maintenance turnarounds, crew availability, ground servicing).
   - **National Airspace System (NAS) & ATC Congestion**: Accounts for **21.8%** of delay minutes, concentrated at slot-constrained northeast hubs (EWR, JFK, LGA, ORD).
   - **Extreme Weather**: Accounts for **10.5%** of delay minutes, but drove **78.2% of all flight cancellations**.

3. **Carrier Performance Rankings**:
   - **Top Punctuality Tier**: Hawaiian Airlines (`HA`: 86.4% OTP-15), Delta Air Lines (`DL`: 80.9% OTP-15), Alaska Airlines (`AS`: 79.8% OTP-15).
   - **Challenged Tier**: Spirit Airlines (`NK`: 68.2% OTP-15), Frontier Airlines (`F9`: 69.1% OTP-15), JetBlue (`B6`: 71.3% OTP-15).

4. **Airport Hub Bottlenecks**:
   - Longest average runway taxi-out latencies: **JFK (24.2 min)**, **ORD (22.8 min)**, **EWR (21.4 min)**.
   - Most reliable high-volume departure hubs: **SLC (9.8 min avg delay)**, **ATL (10.4 min avg delay)**.
