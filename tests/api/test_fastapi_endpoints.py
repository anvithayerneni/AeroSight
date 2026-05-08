"""
API Integration Tests for FastAPI Endpoints
"""

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"

def test_api_system_status():
    res = client.get("/api/health/status")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "operational"
    assert data["data_lake"]["record_counts"]["fact_flights"] > 0

def test_get_flights():
    res = client.get("/api/flights?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert "flights" in data
    assert len(data["flights"]) == 10
    assert data["total_count"] > 0

def test_get_single_flight():
    res_list = client.get("/api/flights?limit=1")
    flight_id = res_list.json()["flights"][0]["flight_id"]
    
    res = client.get(f"/api/flights/{flight_id}")
    assert res.status_code == 200
    assert res.json()["flight_id"] == flight_id

def test_get_airports():
    res = client.get("/api/airports")
    assert res.status_code == 200
    data = res.json()
    assert len(data) > 0
    assert any(a["iata"] == "ATL" for a in data)

def test_get_airlines():
    res = client.get("/api/airlines")
    assert res.status_code == 200
    data = res.json()
    assert len(data) > 0
    assert any(a["carrier_code"] == "DL" for a in data)

def test_get_routes():
    res = client.get("/api/routes?limit=5")
    assert res.status_code == 200
    assert len(res.json()) == 5

def test_get_analytics_kpis():
    res = client.get("/api/analytics/kpis")
    assert res.status_code == 200
    data = res.json()
    assert data["total_flights"] > 0
    assert "on_time_arrival_otp15_pct" in data

def test_ml_predict_endpoint():
    payload = {
        "carrier_code": "DL",
        "origin_airport": "ATL",
        "dest_airport": "LGA",
        "dep_hour": 17,
        "day_of_week": 5,
        "month": 2,
        "distance": 762,
        "origin_temp_f": 32.0,
        "origin_wind_mph": 15.0,
        "origin_visibility_miles": 6.0,
        "origin_weather_condition": "Snow"
    }
    res = client.post("/api/ml/predict-delay", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "delay_probability" in data
    assert "risk_tier" in data

def test_reports_list():
    res = client.get("/api/reports/list")
    assert res.status_code == 200
    data = res.json()
    assert len(data) > 0
