"""
Unit tests for AeroSight Statistical Analysis Engine
"""

from analytics.statistics import StatisticalEngine

def test_descriptive_statistics():
    engine = StatisticalEngine()
    stats = engine.compute_delay_descriptive_stats()
    
    assert "arrival_delay" in stats
    assert "departure_delay" in stats
    
    arr = stats["arrival_delay"]
    assert arr["count"] > 0
    assert arr["p50"] <= arr["p90"]
    assert arr["p25"] <= arr["p75"]
    assert "skewness" in arr

def test_correlation_matrix():
    engine = StatisticalEngine()
    corrs = engine.compute_correlation_matrix()
    
    assert "columns" in corrs
    assert "pearson" in corrs
    assert "spearman" in corrs
    assert corrs["pearson"]["dep_delay"]["arr_delay"] > 0.5 # High correlation expected

def test_outlier_detection():
    engine = StatisticalEngine()
    outliers = engine.detect_delay_outliers(threshold_z=3.0)
    
    assert "z_score_outlier_count" in outliers
    assert outliers["z_score_outlier_pct"] < 5.0 # Less than 5% outliers under 3-sigma
    assert "iqr_upper_fence" in outliers

def test_hypothesis_testing():
    engine = StatisticalEngine()
    tests = engine.run_hypothesis_tests()
    
    assert "test_1_weather_impact" in tests
    assert "test_2_carrier_variance" in tests
    assert "test_3_cancellation_independence" in tests
    
    t1 = tests["test_1_weather_impact"]
    assert t1["p_value"] < 0.05
    assert t1["statistically_significant"] is True
