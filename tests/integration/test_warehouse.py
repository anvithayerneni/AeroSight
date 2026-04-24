"""
Integration tests for Data Warehouse querying and integrity
"""

from warehouse.db import get_db

def test_warehouse_dimensions_populated():
    db = get_db()
    
    airports = db.execute_query("SELECT COUNT(*) as cnt FROM dim_airport")[0]["cnt"]
    airlines = db.execute_query("SELECT COUNT(*) as cnt FROM dim_airline")[0]["cnt"]
    routes = db.execute_query("SELECT COUNT(*) as cnt FROM dim_route")[0]["cnt"]
    
    assert airports >= 20
    assert airlines >= 5
    assert routes >= 100

def test_warehouse_facts_populated():
    db = get_db()
    
    flights = db.execute_query("SELECT COUNT(*) as cnt FROM fact_flights")[0]["cnt"]
    delays = db.execute_query("SELECT COUNT(*) as cnt FROM fact_delays")[0]["cnt"]
    
    assert flights >= 1000
    assert delays > 0

def test_analytical_views_integrity():
    db = get_db()
    
    carrier_summary = db.execute_query("SELECT * FROM v_carrier_monthly_summary LIMIT 5")
    assert len(carrier_summary) > 0
    
    airport_summary = db.execute_query("SELECT * FROM v_airport_congestion_summary LIMIT 5")
    assert len(airport_summary) > 0
