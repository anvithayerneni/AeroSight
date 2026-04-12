"""
AeroSight Pydantic Request & Response Schemas
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# Flight Schemas
class FlightItem(BaseModel):
    flight_id: str
    flight_date: str
    carrier_key: str
    flight_number: int
    aircraft_key: Optional[str] = None
    origin_airport_key: str
    dest_airport_key: str
    route_key: str
    crs_dep_time: int
    dep_time: Optional[int] = None
    dep_delay: Optional[float] = 0.0
    taxi_out: Optional[float] = 0.0
    crs_arr_time: int
    arr_time: Optional[int] = None
    arr_delay: Optional[float] = 0.0
    cancelled: int = 0
    cancellation_code: Optional[str] = None
    diverted: int = 0
    distance: int
    is_delayed_15: int = 0
    origin_temp_f: Optional[float] = None
    origin_weather_condition: Optional[str] = None

class PaginatedFlightsResponse(BaseModel):
    total_count: int
    page: int
    limit: int
    flights: List[FlightItem]

# Airport Schemas
class AirportItem(BaseModel):
    iata: str
    icao: Optional[str] = None
    name: str
    city: str
    state: str
    lat: float
    lon: float
    elev: Optional[int] = None
    hub: Optional[str] = None
    terminals: Optional[int] = None
    gates: Optional[int] = None

# Airline Schemas
class AirlineItem(BaseModel):
    carrier_code: str
    airline_name: str
    callsign: Optional[str] = None
    country: Optional[str] = None
    fleet_size: Optional[int] = None
    primary_hub: Optional[str] = None

# ML Prediction Schemas
class DelayPredictionRequest(BaseModel):
    carrier_code: str = Field(..., example="DL")
    origin_airport: str = Field(..., example="ATL")
    dest_airport: str = Field(..., example="LGA")
    dep_hour: int = Field(14, ge=0, le=23, example=17)
    day_of_week: int = Field(3, ge=1, le=7, example=5)
    month: int = Field(2, ge=1, le=12, example=1)
    distance: int = Field(750, ge=50, le=5000, example=762)
    origin_temp_f: float = Field(55.0, example=34.0)
    origin_wind_mph: float = Field(8.0, example=18.0)
    origin_visibility_miles: float = Field(10.0, example=3.0)
    origin_weather_condition: str = Field("Clear", example="Snow")

class DelayPredictionResponse(BaseModel):
    is_delayed_prediction: bool
    delay_probability: float
    delay_probability_pct: float
    risk_tier: str
    predicted_delay_minutes: float
    input_features: Dict[str, Any]

class AnomalyDetectionRequest(BaseModel):
    dep_delay: float = Field(..., example=45.0)
    arr_delay: float = Field(..., example=55.0)
    taxi_out: float = Field(..., example=42.0)
    taxi_in: float = Field(..., example=12.0)

class AnomalyDetectionResponse(BaseModel):
    is_anomaly: bool
    anomaly_score: float
    severity: str
    telemetry: Dict[str, float]

class TrafficForecastItem(BaseModel):
    forecast_date: str
    day_name: str
    predicted_flight_volume: int
    confidence_lower_80: int
    confidence_upper_80: int

class SQLQueryRequest(BaseModel):
    query: str = Field(..., example="SELECT carrier_key, COUNT(*) as flights FROM fact_flights GROUP BY carrier_key")
