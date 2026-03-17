"""
AeroSight Machine Learning Inference Engine
Loads serialized model artifacts and performs real-time scoring for FastAPI endpoints.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from ml.features import compute_cyclical_features, FEATURE_COLUMNS
from warehouse.db import get_db

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "ml", "models")

class InferenceEngine:
    _instance: Optional["InferenceEngine"] = None

    def __init__(self, models_dir: str = MODELS_DIR):
        self.models_dir = models_dir
        self.clf = None
        self.reg = None
        self.anomaly_detector = None
        self.model_card = None
        self.db = get_db()
        self._load_artifacts()

    @classmethod
    def get_instance(cls) -> "InferenceEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_artifacts(self):
        """Loads serialized models from disk."""
        clf_path = os.path.join(self.models_dir, "delay_classifier.joblib")
        reg_path = os.path.join(self.models_dir, "delay_regressor.joblib")
        iso_path = os.path.join(self.models_dir, "anomaly_detector.joblib")
        card_path = os.path.join(self.models_dir, "model_card.json")

        if os.path.exists(clf_path):
            self.clf = joblib.load(clf_path)
        if os.path.exists(reg_path):
            self.reg = joblib.load(reg_path)
        if os.path.exists(iso_path):
            self.anomaly_detector = joblib.load(iso_path)
        if os.path.exists(card_path):
            with open(card_path, "r") as f:
                self.model_card = json.load(f)

    def predict_delay(self, flight_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Infers delay probability and expected duration for a planned flight.
        Input dictionary contains:
        - carrier_code: str (e.g. 'DL')
        - origin_airport: str (e.g. 'ATL')
        - dest_airport: str (e.g. 'LGA')
        - dep_hour: int (0-23)
        - day_of_week: int (1-7)
        - month: int (1-12)
        - distance: int
        - origin_temp_f: float
        - origin_wind_mph: float
        - origin_visibility_miles: float
        - origin_weather_condition: str
        """
        if self.clf is None or self.reg is None:
            self._load_artifacts()
            if self.clf is None or self.reg is None:
                raise RuntimeError("ML Models not loaded. Please run ml/train.py first.")

        # Extract input parameters with sensible defaults
        hour = flight_input.get("dep_hour", 14)
        dow = flight_input.get("day_of_week", 3)
        month = flight_input.get("month", 2)
        dist = flight_input.get("distance", 750)
        temp = flight_input.get("origin_temp_f", 55.0)
        wind = flight_input.get("origin_wind_mph", 8.0)
        vis = flight_input.get("origin_visibility_miles", 10.0)
        weather_cond = flight_input.get("origin_weather_condition", "Clear")
        carrier = flight_input.get("carrier_code", "DL")

        # Cyclical features
        cyclical = compute_cyclical_features(hour, dow, month)
        
        # Historical carrier baseline lookup from warehouse
        carrier_rate = 0.20
        carrier_stats = self.db.execute_query(
            "SELECT ROUND(AVG(is_delayed_15), 4) as rate FROM fact_flights WHERE carrier_key = ? GROUP BY carrier_key",
            [carrier]
        )
        if carrier_stats and carrier_stats[0]["rate"] is not None:
            carrier_rate = float(carrier_stats[0]["rate"])

        # Origin hourly delay baseline
        origin_delay = 12.0
        origin_stats = self.db.execute_query(
            "SELECT ROUND(AVG(dep_delay), 2) as avg_delay FROM fact_flights WHERE origin_airport_key = ? AND crs_dep_time / 100 = ? GROUP BY origin_airport_key",
            [flight_input.get("origin_airport", "ATL"), hour]
        )
        if origin_stats and origin_stats[0]["avg_delay"] is not None:
            origin_delay = float(origin_stats[0]["avg_delay"])

        is_severe = 1 if (weather_cond in ["Thunderstorm", "Snow", "Fog"] or wind > 20) else 0
        crs_elapsed = int(dist / 7.5 + 30) # Estimation: 450 knots + taxi

        feature_vector = np.array([[
            cyclical["dep_hour_sin"],
            cyclical["dep_hour_cos"],
            cyclical["day_of_week_sin"],
            cyclical["day_of_week_cos"],
            cyclical["month_sin"],
            cyclical["month_cos"],
            dist,
            crs_elapsed,
            carrier_rate,
            origin_delay,
            temp,
            wind,
            vis,
            cyclical["is_weekend"],
            cyclical["is_rush_hour"],
            is_severe
        ]], dtype=np.float32)

        # Classification inference
        prob_delay = float(self.clf.predict_proba(feature_vector)[0, 1])
        predicted_class = int(prob_delay >= 0.45) # 0.45 threshold tuned for balanced recall

        # Regression inference
        predicted_duration = max(0.0, float(self.reg.predict(feature_vector)[0]))
        if not predicted_class:
            predicted_duration = min(predicted_duration, 14.0)

        # Determine risk level
        if prob_delay < 0.25:
            risk_tier = "Low"
        elif prob_delay < 0.50:
            risk_tier = "Moderate"
        elif prob_delay < 0.75:
            risk_tier = "High"
        else:
            risk_tier = "Critical"

        return {
            "is_delayed_prediction": bool(predicted_class),
            "delay_probability": round(prob_delay, 4),
            "delay_probability_pct": round(prob_delay * 100, 1),
            "risk_tier": risk_tier,
            "predicted_delay_minutes": round(predicted_duration, 1),
            "input_features": {
                "carrier": carrier,
                "origin": flight_input.get("origin_airport", "ATL"),
                "dest": flight_input.get("dest_airport", "LGA"),
                "departure_hour": hour,
                "weather_condition": weather_cond,
                "wind_mph": wind,
                "visibility_miles": vis
            }
        }

    def detect_anomaly(self, dep_delay: float, arr_delay: float, taxi_out: float, taxi_in: float) -> Dict[str, Any]:
        """Runs unsupervised Isolation Forest anomaly detection on flight operational telemetry."""
        if self.anomaly_detector is None:
            self._load_artifacts()

        vec = np.array([[dep_delay, arr_delay, taxi_out, taxi_in]], dtype=np.float32)
        score = float(self.anomaly_detector.decision_function(vec)[0])
        is_anomaly = int(self.anomaly_detector.predict(vec)[0]) == -1

        return {
            "is_anomaly": bool(is_anomaly),
            "anomaly_score": round(score, 4),
            "severity": "High Anomaly" if score < -0.15 else ("Moderate Anomaly" if is_anomaly else "Normal Operations"),
            "telemetry": {
                "departure_delay": dep_delay,
                "arrival_delay": arr_delay,
                "taxi_out": taxi_out,
                "taxi_in": taxi_in
            }
        }

    def forecast_daily_traffic(self, horizon_days: int = 14) -> List[Dict[str, Any]]:
        """Generates forward-looking daily flight traffic forecast."""
        if not self.model_card:
            self._load_artifacts()

        traffic_info = self.model_card.get("models", {}).get("demand_forecaster", {})
        base_vol = traffic_info.get("avg_daily_volume", 330.0)
        multipliers = traffic_info.get("dow_seasonality_multipliers", {})

        forecasts = []
        today = datetime.utcnow().date()

        for i in range(1, horizon_days + 1):
            future_date = today + timedelta(days=i)
            dow = str(future_date.weekday())
            mult = multipliers.get(dow, 1.0)
            noise = np.random.normal(0, base_vol * 0.03)
            predicted_vol = int(max(100, (base_vol * mult) + noise))
            forecasts.append({
                "forecast_date": future_date.strftime("%Y-%m-%d"),
                "day_name": future_date.strftime("%A"),
                "predicted_flight_volume": predicted_vol,
                "confidence_lower_80": int(predicted_vol * 0.92),
                "confidence_upper_80": int(predicted_vol * 1.08),
            })

        return forecasts

    def get_model_card(self) -> Dict[str, Any]:
        if not self.model_card:
            self._load_artifacts()
        return self.model_card or {}
