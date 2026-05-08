"""
Tests for Data Quality Validator and Rules
"""

from data_quality.reporter import DataQualityReporter
from data_quality.validator import DataQualityValidator


def test_data_quality_on_valid_data(sample_flight_data):
    validator = DataQualityValidator(sample_flight_data)
    results = validator.run_all_checks()
    
    assert results["passed"] is True
    assert results["quality_score"] >= 95.0
    assert results["total_rows"] == len(sample_flight_data)

def test_data_quality_detects_nulls(sample_flight_data):
    corrupted = sample_flight_data.copy()
    corrupted.loc[0:10, "flight_id"] = None
    
    validator = DataQualityValidator(corrupted)
    results = validator.run_all_checks()
    
    assert results["checks"]["null_violations"]["passed"] is False
    assert len(validator.get_quarantine_dataframe()) >= 10

def test_reporter_formatting(sample_flight_data):
    validator = DataQualityValidator(sample_flight_data)
    results = validator.run_all_checks()
    reporter = DataQualityReporter(results)
    
    summary = reporter.generate_console_summary()
    assert "AEROSIGHT DATA QUALITY SCORECARD" in summary
    assert "PASSED" in summary
