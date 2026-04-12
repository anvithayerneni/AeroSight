"""
AeroSight Machine Learning API Endpoints
"""

from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict, Any
from ml.inference import InferenceEngine
from backend.schemas import (
    DelayPredictionRequest,
    DelayPredictionResponse,
    AnomalyDetectionRequest,
    AnomalyDetectionResponse,
    TrafficForecastItem
)

router = APIRouter(prefix="/ml", tags=["Machine Learning"])

@router.post("/predict-delay", response_model=DelayPredictionResponse, summary="Predict Flight Delay Risk & Duration")
def predict_flight_delay(req: DelayPredictionRequest):
    engine = InferenceEngine.get_instance()
    try:
        return engine.predict_delay(req.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")

@router.post("/detect-anomaly", response_model=AnomalyDetectionResponse, summary="Detect Operational Flight Telemetry Anomalies")
def detect_operational_anomaly(req: AnomalyDetectionRequest):
    engine = InferenceEngine.get_instance()
    try:
        return engine.detect_anomaly(req.dep_delay, req.arr_delay, req.taxi_out, req.taxi_in)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Anomaly detection error: {str(e)}")

@router.get("/forecast", response_model=List[TrafficForecastItem], summary="Get Network Daily Flight Traffic Forecast")
def get_traffic_forecast(horizon_days: int = Query(14, ge=1, le=30)):
    engine = InferenceEngine.get_instance()
    return engine.forecast_daily_traffic(horizon_days=horizon_days)

@router.get("/model-info", summary="Get ML Model Metadata & Evaluation Cards")
def get_model_metadata():
    engine = InferenceEngine.get_instance()
    return engine.get_model_card()
