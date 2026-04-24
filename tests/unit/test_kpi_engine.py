"""
Unit tests for KPI Engine calculations
"""

from analytics.kpi_engine import KPIEngine

def test_executive_kpis():
    engine = KPIEngine()
    summary = engine.get_executive_summary()
    
    assert summary["total_flights"] > 0
    assert 0.0 <= summary["completion_rate_pct"] <= 100.0
    assert 0.0 <= summary["on_time_arrival_otp15_pct"] <= 100.0
    assert summary["avg_dep_delay"] is not None

def test_carrier_leaderboard():
    engine = KPIEngine()
    carriers = engine.get_carrier_leaderboard()
    
    assert len(carriers) > 0
    first = carriers[0]
    assert "carrier_code" in first
    assert "airline_name" in first
    assert "otp15_pct" in first

def test_delay_root_causes():
    engine = KPIEngine()
    causes = engine.get_delay_root_cause_breakdown()
    
    assert len(causes) > 0
    cause_names = [c["primary_delay_cause"] for c in causes]
    assert any(c in cause_names for c in ["Carrier", "Weather", "NAS", "Late Aircraft"])
