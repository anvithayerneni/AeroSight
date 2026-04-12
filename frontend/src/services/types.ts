export interface FlightItem {
  flight_id: string;
  flight_date: string;
  carrier_key: string;
  flight_number: number;
  aircraft_key?: string;
  origin_airport_key: string;
  dest_airport_key: string;
  route_key: string;
  crs_dep_time: number;
  dep_time?: number;
  dep_delay?: number;
  taxi_out?: number;
  crs_arr_time: number;
  arr_time?: number;
  arr_delay?: number;
  cancelled: number;
  cancellation_code?: string;
  diverted: number;
  distance: number;
  is_delayed_15: number;
  origin_temp_f?: number;
  origin_weather_condition?: string;
}

export interface PaginatedFlights {
  total_count: number;
  limit: number;
  offset: number;
  flights: FlightItem[];
}

export interface AirportItem {
  iata: string;
  icao?: string;
  name: string;
  city: string;
  state: string;
  lat: number;
  lon: number;
  hub?: string;
  gates?: number;
  total_departures: number;
  avg_dep_delay_min?: number;
  avg_taxi_out_min?: number;
  delayed_dep_pct?: number;
  cancellation_rate_pct?: number;
}

export interface AirlineItem {
  carrier_code: string;
  airline_name: string;
  callsign?: string;
  fleet_size?: number;
  primary_hub?: string;
  total_flights: number;
  avg_arr_delay: number;
  avg_dep_delay: number;
  otp15_pct: number;
  completion_rate_pct: number;
}

export interface RouteItem {
  route_key: string;
  origin: string;
  dest: string;
  distance_miles: number;
  distance_category?: string;
  flight_count: number;
  avg_arr_delay: number;
  avg_dep_delay: number;
  otp15_pct: number;
  cancellation_rate_pct: number;
}

export interface ExecutiveKPIs {
  total_flights: number;
  operated_flights: number;
  cancelled_flights: number;
  diverted_flights: number;
  delayed_flights: number;
  avg_dep_delay: number;
  avg_arr_delay: number;
  on_time_departure_pct: number;
  on_time_arrival_otp15_pct: number;
  completion_rate_pct: number;
  cancellation_rate_pct: number;
  total_distance_flown_miles: number;
  total_bags_checked?: number;
  mishandled_bag_rate_pct?: number;
  avg_baggage_wait_min?: number;
}

export interface DelayCauseItem {
  primary_delay_cause: string;
  delayed_flights: number;
  total_delay_minutes: number;
  avg_delay_duration_min: number;
  carrier_minutes: number;
  weather_minutes: number;
  nas_minutes: number;
  late_aircraft_minutes: number;
}

export interface DailyTrendItem {
  flight_date: string;
  flight_volume: number;
  operated_volume: number;
  cancellations: number;
  avg_arr_delay: number;
  otp15_pct: number;
}

export interface DelayPredictionResponse {
  is_delayed_prediction: boolean;
  delay_probability: number;
  delay_probability_pct: number;
  risk_tier: 'Low' | 'Moderate' | 'High' | 'Critical';
  predicted_delay_minutes: number;
  input_features: Record<string, any>;
}

export interface AnomalyDetectionResponse {
  is_anomaly: boolean;
  anomaly_score: number;
  severity: string;
  telemetry: Record<string, number>;
}

export interface TrafficForecastItem {
  forecast_date: string;
  day_name: string;
  predicted_flight_volume: number;
  confidence_lower_80: number;
  confidence_upper_80: number;
}

export interface LiveTelemetryEvent {
  event_id: string;
  timestamp: string;
  flight_id: string;
  carrier_code: string;
  flight_number: number;
  origin_airport: string;
  dest_airport: string;
  status: string;
  dep_delay: number;
  arr_delay: number;
  gate: string;
  altitude_ft: number;
  ground_speed_knots: number;
}

export interface ReportItem {
  filename: string;
  file_type: string;
  size_kb: number;
  download_url: string;
}
