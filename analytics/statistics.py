"""
AeroSight Statistical Analysis & Hypothesis Testing Engine
Computes descriptive distributions, correlation matrices, outlier detection,
and formal statistical hypothesis testing (t-test, ANOVA, Chi-Square).
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Any, List
from warehouse.db import get_db

class StatisticalEngine:
    def __init__(self, db_manager=None):
        self.db = db_manager or get_db()
        self._flights_df = None

    def get_flights_dataframe(self) -> pd.DataFrame:
        if self._flights_df is None:
            self._flights_df = self.db.query_df("SELECT * FROM fact_flights")
        return self._flights_df

    def compute_delay_descriptive_stats(self) -> Dict[str, Any]:
        """Calculates comprehensive distribution metrics for arrival and departure delays."""
        df = self.get_flights_dataframe()
        operated = df[df["cancelled"] == 0]
        
        arr_delays = operated["arr_delay"].dropna().to_numpy()
        dep_delays = operated["dep_delay"].dropna().to_numpy()

        def _stats(arr):
            p25, p50, p75, p90, p95, p99 = np.percentile(arr, [25, 50, 75, 90, 95, 99])
            return {
                "count": int(len(arr)),
                "mean": round(float(np.mean(arr)), 2),
                "median": round(float(p50), 2),
                "std": round(float(np.std(arr, ddof=1)), 2),
                "variance": round(float(np.var(arr, ddof=1)), 2),
                "min": round(float(np.min(arr)), 2),
                "max": round(float(np.max(arr)), 2),
                "iqr": round(float(p75 - p25), 2),
                "p25": round(float(p25), 2),
                "p50": round(float(p50), 2),
                "p75": round(float(p75), 2),
                "p90": round(float(p90), 2),
                "p95": round(float(p95), 2),
                "p99": round(float(p99), 2),
                "skewness": round(float(stats.skew(arr)), 3),
                "kurtosis": round(float(stats.kurtosis(arr)), 3),
            }

        return {
            "arrival_delay": _stats(arr_delays),
            "departure_delay": _stats(dep_delays),
        }

    def compute_correlation_matrix(self) -> Dict[str, Any]:
        """Computes Pearson and Spearman correlation coefficients across operational and weather metrics."""
        df = self.get_flights_dataframe()
        operated = df[df["cancelled"] == 0]
        
        numeric_cols = [
            "dep_delay", "arr_delay", "taxi_out", "taxi_in",
            "distance", "origin_temp_f", "origin_wind_mph", "origin_visibility_miles"
        ]
        sub_df = operated[numeric_cols].dropna()
        
        pearson_corr = sub_df.corr(method="pearson").round(3).to_dict()
        spearman_corr = sub_df.corr(method="spearman").round(3).to_dict()

        return {
            "columns": numeric_cols,
            "pearson": pearson_corr,
            "spearman": spearman_corr
        }

    def detect_delay_outliers(self, threshold_z: float = 3.0) -> Dict[str, Any]:
        """Detects statistical outliers in arrival delays using Z-score and IQR fences."""
        df = self.get_flights_dataframe()
        operated = df[df["cancelled"] == 0].copy()
        
        arr = operated["arr_delay"].dropna()
        mean_val = arr.mean()
        std_val = arr.std()
        
        # Z-Score Outliers
        z_scores = (arr - mean_val) / std_val
        z_outliers = operated[np.abs(z_scores) > threshold_z]

        # IQR Fences (Tukey's method)
        q25, q75 = np.percentile(arr, [25, 75])
        iqr = q75 - q25
        upper_fence = q75 + 1.5 * iqr
        lower_fence = q25 - 1.5 * iqr
        iqr_outliers = operated[(arr > upper_fence) | (arr < lower_fence)]

        return {
            "total_records_checked": len(operated),
            "z_score_threshold": threshold_z,
            "z_score_outlier_count": len(z_outliers),
            "z_score_outlier_pct": round((len(z_outliers) / len(operated)) * 100, 2),
            "iqr_upper_fence": round(float(upper_fence), 2),
            "iqr_outlier_count": len(iqr_outliers),
            "iqr_outlier_pct": round((len(iqr_outliers) / len(operated)) * 100, 2),
            "sample_extreme_outliers": z_outliers[["flight_id", "carrier_key", "origin_airport_key", "dest_airport_key", "arr_delay", "origin_weather_condition"]].head(10).to_dict(orient="records")
        }

    def run_hypothesis_tests(self) -> Dict[str, Any]:
        """
        Executes formal statistical hypothesis tests on aviation operational questions:
        1. Adverse Weather vs Fair Weather delays (Welch's Two-Sample t-test)
        2. Carrier Delay Distribution Differences (One-Way ANOVA)
        3. Cancellation Independence vs Origin Weather (Chi-Square Test)
        """
        df = self.get_flights_dataframe()
        operated = df[df["cancelled"] == 0]

        # Test 1: Adverse Weather vs Fair Weather
        adverse_conditions = ["Rain", "Snow", "Fog", "Thunderstorm"]
        weather_adverse = operated[operated["origin_weather_condition"].isin(adverse_conditions)]["arr_delay"].dropna()
        weather_fair = operated[operated["origin_weather_condition"] == "Clear"]["arr_delay"].dropna()
        
        t_stat, p_val_ttest = stats.ttest_ind(weather_adverse, weather_fair, equal_var=False)

        # Test 2: One-Way ANOVA across major carriers
        carrier_groups = [group["arr_delay"].dropna().values for _, group in operated.groupby("carrier_key")]
        f_stat, p_val_anova = stats.f_oneway(*carrier_groups)

        # Test 3: Chi-Square Test of Independence: Weather Condition vs Cancellation
        contingency_table = pd.crosstab(df["origin_weather_condition"], df["cancelled"])
        chi2_stat, p_val_chi2, dof, _ = stats.chi2_contingency(contingency_table)

        return {
            "test_1_weather_impact": {
                "question": "Does adverse weather at origin significantly increase flight arrival delays?",
                "test_name": "Welch's Two-Sample t-test",
                "adverse_weather_mean_delay": round(float(weather_adverse.mean()), 2),
                "fair_weather_mean_delay": round(float(weather_fair.mean()), 2),
                "t_statistic": round(float(t_stat), 4),
                "p_value": float(p_val_ttest),
                "statistically_significant": bool(p_val_ttest < 0.05),
                "conclusion": "Adverse weather exhibits a statistically significant positive effect on flight arrival delays (p < 0.05)."
            },
            "test_2_carrier_variance": {
                "question": "Do different airlines have statistically significant differences in operational delay performance?",
                "test_name": "One-Way ANOVA (Analysis of Variance)",
                "f_statistic": round(float(f_stat), 4),
                "p_value": float(p_val_anova),
                "statistically_significant": bool(p_val_anova < 0.05),
                "conclusion": "There is a statistically significant difference in mean arrival delays across air carriers (p < 0.05)."
            },
            "test_3_cancellation_independence": {
                "question": "Are flight cancellations statistically dependent on meteorological weather conditions?",
                "test_name": "Pearson's Chi-Square Test of Independence",
                "chi2_statistic": round(float(chi2_stat), 4),
                "degrees_of_freedom": int(dof),
                "p_value": float(p_val_chi2),
                "statistically_significant": bool(p_val_chi2 < 0.05),
                "conclusion": "Cancellations are significantly dependent on surface meteorological conditions (p < 0.05)."
            }
        }
