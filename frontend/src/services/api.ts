import {
  PaginatedFlights,
  FlightItem,
  AirportItem,
  AirlineItem,
  RouteItem,
  ExecutiveKPIs,
  DelayCauseItem,
  DailyTrendItem,
  DelayPredictionResponse,
  AnomalyDetectionResponse,
  TrafficForecastItem,
  ReportItem
} from './types';

const API_BASE = '/api';

export async function fetchKPIs(): Promise<ExecutiveKPIs> {
  const res = await fetch(`${API_BASE}/analytics/kpis`);
  if (!res.ok) throw new Error('Failed to fetch KPIs');
  return res.json();
}

export async function fetchDailyTrends(): Promise<DailyTrendItem[]> {
  const res = await fetch(`${API_BASE}/analytics/trends`);
  if (!res.ok) throw new Error('Failed to fetch daily trends');
  return res.json();
}

export async function fetchDelayBreakdown(): Promise<DelayCauseItem[]> {
  const res = await fetch(`${API_BASE}/analytics/delays`);
  if (!res.ok) throw new Error('Failed to fetch delay breakdown');
  return res.json();
}

export async function fetchStatisticalAnalysis(): Promise<any> {
  const res = await fetch(`${API_BASE}/analytics/statistics`);
  if (!res.ok) throw new Error('Failed to fetch statistics');
  return res.json();
}

export async function fetchFlights(
  limit = 50,
  offset = 0,
  carrier?: string,
  origin?: string,
  dest?: string,
  delayedOnly?: boolean
): Promise<PaginatedFlights> {
  const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  if (carrier) params.append('carrier', carrier);
  if (origin) params.append('origin', origin);
  if (dest) params.append('dest', dest);
  if (delayedOnly) params.append('delayed_only', 'true');

  const res = await fetch(`${API_BASE}/flights?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch flights');
  return res.json();
}

export async function fetchFlightById(flightId: string): Promise<FlightItem & { delay_breakdown?: any }> {
  const res = await fetch(`${API_BASE}/flights/${flightId}`);
  if (!res.ok) throw new Error(`Failed to fetch flight ${flightId}`);
  return res.json();
}

export async function fetchAirports(): Promise<AirportItem[]> {
  const res = await fetch(`${API_BASE}/airports`);
  if (!res.ok) throw new Error('Failed to fetch airports');
  return res.json();
}

export async function fetchAirlines(): Promise<AirlineItem[]> {
  const res = await fetch(`${API_BASE}/airlines`);
  if (!res.ok) throw new Error('Failed to fetch airlines');
  return res.json();
}

export async function fetchRoutes(): Promise<RouteItem[]> {
  const res = await fetch(`${API_BASE}/routes?limit=50`);
  if (!res.ok) throw new Error('Failed to fetch routes');
  return res.json();
}

export async function fetchTopDelayedRoutes(): Promise<RouteItem[]> {
  const res = await fetch(`${API_BASE}/routes/top-delayed?limit=15`);
  if (!res.ok) throw new Error('Failed to fetch delayed routes');
  return res.json();
}

export async function predictFlightDelay(payload: {
  carrier_code: string;
  origin_airport: string;
  dest_airport: string;
  dep_hour: number;
  day_of_week: number;
  month: number;
  distance: number;
  origin_temp_f: number;
  origin_wind_mph: number;
  origin_visibility_miles: number;
  origin_weather_condition: string;
}): Promise<DelayPredictionResponse> {
  const res = await fetch(`${API_BASE}/ml/predict-delay`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error('Prediction API failed');
  return res.json();
}

export async function detectOperationalAnomaly(payload: {
  dep_delay: number;
  arr_delay: number;
  taxi_out: number;
  taxi_in: number;
}): Promise<AnomalyDetectionResponse> {
  const res = await fetch(`${API_BASE}/ml/detect-anomaly`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error('Anomaly API failed');
  return res.json();
}

export async function fetchTrafficForecast(horizonDays = 14): Promise<TrafficForecastItem[]> {
  const res = await fetch(`${API_BASE}/ml/forecast?horizon_days=${horizonDays}`);
  if (!res.ok) throw new Error('Forecast API failed');
  return res.json();
}

export async function fetchReports(): Promise<ReportItem[]> {
  const res = await fetch(`${API_BASE}/reports/list`);
  if (!res.ok) throw new Error('Failed to fetch reports');
  return res.json();
}

export async function executeCustomSQL(query: string): Promise<{ query: string; row_count: number; rows: any[] }> {
  const res = await fetch(`${API_BASE}/analytics/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query })
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'SQL Query execution failed');
  }
  return res.json();
}
