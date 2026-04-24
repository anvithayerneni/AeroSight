# AeroSight — Core Stakeholder Questions & Analytical Investigations

This document maps strategic airline business questions to empirical data metrics, analytical methods, and operational decisions.

---

### Question 1: Which airports contribute most to operational delay propagation across our network?
* **Metric**: Outbound Average Departure Delay (`avg_dep_delay`), Taxi-Out Latency (`taxi_out`), and Inbound vs Outbound Delay Ratio.
* **Methodology**: SQL CTEs, window ranking across hub tiers (`DENSE_RANK() OVER (PARTITION BY hub ORDER BY avg_dep_delay ASC)`).
* **Finding**: New York area hubs (JFK, EWR, LGA) and Chicago O'Hare (ORD) exhibit the highest departure delays (+16.8 to +19.4 min) and taxi-out times (>21 min).
* **Operational Decision**: Increase schedule block buffer times on flights originating from JFK/ORD/EWR during evening peak banks (16:00–20:00).

---

### Question 2: Does adverse surface weather statistically explain flight delays, or are carrier controllable factors dominant?
* **Metric**: Arrival Delay Minutes categorized by BTS root cause codes (`CarrierDelay`, `WeatherDelay`, `NASDelay`, `LateAircraftDelay`).
* **Methodology**: Welch's Two-Sample independent t-test comparing adverse weather conditions against fair weather; ANOVA across delay causes.
* **Finding**: Welch's t-test confirms adverse weather significantly elevates delays ($t = 7.93, p < 10^{-14}$), yet controllable carrier factors and late aircraft cascades represent over **67.5% of total system delay minutes**.
* **Operational Decision**: Station managers cannot rely solely on weather exemptions; focus ground crew efficiency on rapid turnaround recovery.

---

### Question 3: Are flight cancellations statistically dependent on weather or airline carrier dispatch policies?
* **Metric**: Cancellation binary flag and BTS cancellation codes (`A` Carrier, `B` Weather, `C` NAS, `D` Security).
* **Methodology**: Pearson's Chi-Square Test of Independence on contingency tables.
* **Finding**: Chi-Square statistic ($\chi^2 = 2301.4, p < 10^{-50}$) confirms severe winter storms and convective weather drive over 78% of cancellations.
* **Operational Decision**: Deploy automated preemptive flight cancellations 12 hours before severe storm systems to preserve fleet positioning and prevent stranded aircraft.

---

### Question 4: How predictable are arrival delays prior to departure, and what features provide the highest predictive signal?
* **Metric**: Binary classification ROC-AUC, F1-Score, Brier Score, and Gini Feature Importance.
* **Methodology**: Random Forest Classifier with cyclical trigonometric temporal encodings (`dep_hour_sin/cos`, `day_of_week_sin/cos`) and origin congestion indices.
* **Finding**: Origin airport hourly congestion index, historical carrier reliability rate, and departure hour cyclical encodings account for **62.4% of total predictive feature importance**.
* **Operational Decision**: Embed real-time ML inference into the dispatch console to flag flights with >60% delay risk at the time of flight release.
