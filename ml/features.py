"""
AeroSight Machine Learning Feature Engineering
Implements preprocessing transformers, cyclical encodings, and lookup builders.
"""

import math

import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "dep_hour_sin", "dep_hour_cos",
    "day_of_week_sin", "day_of_week_cos",
    "month_sin", "month_cos",
    "distance", "crs_elapsed_time",
    "carrier_historical_delay_rate",
    "origin_hourly_avg_dep_delay",
    "origin_temp_f", "origin_wind_mph", "origin_visibility_miles",
    "is_weekend", "is_rush_hour", "is_severe_weather"
]

def compute_cyclical_features(hour: int, day_of_week: int, month: int) -> dict[str, float]:
    """Computes continuous cyclical sine and cosine representations for temporal variables."""
    return {
        "dep_hour_sin": math.sin(hour * (2.0 * math.pi / 24.0)),
        "dep_hour_cos": math.cos(hour * (2.0 * math.pi / 24.0)),
        "day_of_week_sin": math.sin(day_of_week * (2.0 * math.pi / 7.0)),
        "day_of_week_cos": math.cos(day_of_week * (2.0 * math.pi / 7.0)),
        "month_sin": math.sin(month * (2.0 * math.pi / 12.0)),
        "month_cos": math.cos(month * (2.0 * math.pi / 12.0)),
        "is_weekend": 1 if day_of_week in [1, 7] else 0,
        "is_rush_hour": 1 if hour in [7, 8, 9, 16, 17, 18, 19] else 0,
    }

def prepare_training_matrices(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[str]]:
    """
    Extracts feature matrix X, classification target y_clf (is_delayed_15),
    and regression target y_reg (arr_delay).
    """
    df_clean = df.dropna(subset=FEATURE_COLUMNS + ["is_delayed_15", "arr_delay"]).copy()
    
    X = df_clean[FEATURE_COLUMNS].to_numpy(dtype=np.float32)
    y_clf = df_clean["is_delayed_15"].to_numpy(dtype=np.int32)
    y_reg = df_clean["arr_delay"].to_numpy(dtype=np.float32)
    
    return X, y_clf, y_reg, FEATURE_COLUMNS
