"""
Unit tests for ML feature transformations and cyclical encodings
"""

import math
from ml.features import compute_cyclical_features, FEATURE_COLUMNS

def test_cyclical_features_bounds():
    # Test midnight (hour 0)
    f0 = compute_cyclical_features(hour=0, day_of_week=1, month=1)
    assert abs(f0["dep_hour_sin"] - 0.0) < 1e-4
    assert abs(f0["dep_hour_cos"] - 1.0) < 1e-4
    
    # Test noon (hour 12)
    f12 = compute_cyclical_features(hour=12, day_of_week=3, month=6)
    assert abs(f12["dep_hour_sin"] - 0.0) < 1e-4
    assert abs(f12["dep_hour_cos"] - (-1.0)) < 1e-4

def test_rush_hour_classification():
    f_rush = compute_cyclical_features(hour=17, day_of_week=2, month=3)
    assert f_rush["is_rush_hour"] == 1
    
    f_offpeak = compute_cyclical_features(hour=3, day_of_week=2, month=3)
    assert f_offpeak["is_rush_hour"] == 0

def test_feature_columns_list():
    assert "dep_hour_sin" in FEATURE_COLUMNS
    assert "distance" in FEATURE_COLUMNS
    assert len(FEATURE_COLUMNS) >= 12
