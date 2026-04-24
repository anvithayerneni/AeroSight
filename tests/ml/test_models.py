"""
Tests for Machine Learning Models and Inference Engine
"""

from ml.inference import InferenceEngine

def test_inference_delay_prediction():
    engine = InferenceEngine.get_instance()
    flight_input = {
        "carrier_code": "DL",
        "origin_airport": "ATL",
        "dest_airport": "LGA",
        "dep_hour": 17,
        "day_of_week": 5,
        "month": 1,
        "distance": 762,
        "origin_temp_f": 32.0,
        "origin_wind_mph": 22.0,
        "origin_visibility_miles": 4.0,
        "origin_weather_condition": "Snow"
    }
    
    res = engine.predict_delay(flight_input)
    assert "is_delayed_prediction" in res
    assert 0.0 <= res["delay_probability"] <= 1.0
    assert res["risk_tier"] in ["Low", "Moderate", "High", "Critical"]
    assert res["predicted_delay_minutes"] >= 0.0

def test_anomaly_detection():
    engine = InferenceEngine.get_instance()
    
    # Severe anomaly: 90min dep delay, 120min arr delay, 65min taxi
    anom_res = engine.detect_anomaly(dep_delay=90.0, arr_delay=120.0, taxi_out=65.0, taxi_in=25.0)
    assert "is_anomaly" in anom_res
    assert "anomaly_score" in anom_res

def test_traffic_forecast():
    engine = InferenceEngine.get_instance()
    forecast = engine.forecast_daily_traffic(horizon_days=7)
    
    assert len(forecast) == 7
    assert forecast[0]["predicted_flight_volume"] > 0
    assert forecast[0]["confidence_lower_80"] <= forecast[0]["confidence_upper_80"]
