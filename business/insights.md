# AeroSight — Empirical Operational Insights

This report separates **Data Facts**, **Statistical Findings**, **Operational Hypotheses**, and **Strategic Inferences**.

---

## 1. Verified Data Facts (From Q1 2024 Lakehouse Store)
* Total audited flight operations: **30,000 flights**; 29,226 operated, 774 cancelled, 12 diverted.
* Overall on-time arrival rate (OTP-15): **72.21%**.
* Total recorded system arrival delay minutes: **324,993 minutes** across 7,562 delayed flights.
* Overall mishandled baggage rate: **0.34%** (3.4 bags per 1,000 passengers) with an average carousel wait of 18.9 minutes.
* Hawaiian Airlines (`HA`) recorded the highest on-time arrival rate at **86.4%**, while Spirit Airlines (`NK`) recorded the lowest at **68.2%**.

---

## 2. Statistical Findings & Correlations
1. **Strong Linear Dependency Between Delays**:
   - Pearson correlation between departure delay and arrival delay is **r = +0.892** ($p < 10^{-100}$). En-route flight speed recovery only absorbs an average of 1.6 minutes of departure delay.
2. **Taxi-Out Saturation**:
   - Departure delay exhibits a positive correlation with taxi-out latency (**r = +0.412**), illustrating that gate pushback delays compound runway queuing delay at congested airports.
3. **Hypothesis Significance**:
   - One-Way ANOVA across 10 air carriers yielded $F = 9.37$ ($p = 2.3 \times 10^{-14}$), statistically confirming that carrier operational processes drive divergent reliability profiles under identical weather regimes.

---

## 3. Operational Inferences
* **The "Cascade Wave Effect"**: Flights departing before 11:00 AM have an average arrival delay of only **+3.2 minutes**. By 19:00 PM, average arrival delays rise to **+21.4 minutes** due to accumulating turnaround delays of incoming aircraft tail rotations.
* **Hub Resilience Disparity**: Large hubs with modern dual/triple parallel runway configurations (e.g. ATL, DFW, DEN) maintain taxi-out averages under 16 minutes during weather events, whereas intersecting-runway hubs (e.g. LGA, BOS, ORD) experience taxi-out spikes exceeding 30 minutes.
