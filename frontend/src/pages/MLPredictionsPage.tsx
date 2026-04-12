import React, { useState, useEffect } from 'react';
import { Cpu, Zap, AlertTriangle, TrendingUp, Sparkles, CheckCircle2, ShieldAlert } from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import { predictFlightDelay, detectOperationalAnomaly, fetchTrafficForecast } from '../services/api';
import { DelayPredictionResponse, AnomalyDetectionResponse, TrafficForecastItem } from '../services/types';

export const MLPredictionsPage: React.FC = () => {
  // Delay Predictor Form State
  const [carrier, setCarrier] = useState('DL');
  const [origin, setOrigin] = useState('ATL');
  const [dest, setDest] = useState('LGA');
  const [depHour, setDepHour] = useState(17);
  const [dayOfWeek, setDayOfWeek] = useState(5);
  const [weatherCondition, setWeatherCondition] = useState('Clear');
  const [windMph, setWindMph] = useState(12);
  const [tempF, setTempF] = useState(45);

  const [prediction, setPrediction] = useState<DelayPredictionResponse | null>(null);
  const [predicting, setPredicting] = useState(false);

  // Anomaly Detector Form State
  const [depDelayInput, setDepDelayInput] = useState(50);
  const [arrDelayInput, setArrDelayInput] = useState(65);
  const [taxiOutInput, setTaxiOutInput] = useState(45);
  const [taxiInInput, setTaxiInInput] = useState(15);
  const [anomalyResult, setAnomalyResult] = useState<AnomalyDetectionResponse | null>(null);

  // Forecast State
  const [forecast, setForecast] = useState<TrafficForecastItem[]>([]);

  useEffect(() => {
    // Initial forecast load
    fetchTrafficForecast(14).then(setForecast).catch(console.error);
    handlePredict();
    handleDetectAnomaly();
  }, []);

  const handlePredict = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setPredicting(true);
    try {
      const res = await predictFlightDelay({
        carrier_code: carrier,
        origin_airport: origin,
        dest_airport: dest,
        dep_hour: Number(depHour),
        day_of_week: Number(dayOfWeek),
        month: 2,
        distance: 762,
        origin_temp_f: Number(tempF),
        origin_wind_mph: Number(windMph),
        origin_visibility_miles: weatherCondition === 'Clear' ? 10.0 : 3.0,
        origin_weather_condition: weatherCondition
      });
      setPrediction(res);
    } catch (err) {
      console.error(err);
    } finally {
      setPredicting(false);
    }
  };

  const handleDetectAnomaly = async () => {
    try {
      const res = await detectOperationalAnomaly({
        dep_delay: Number(depDelayInput),
        arr_delay: Number(arrDelayInput),
        taxi_out: Number(taxiOutInput),
        taxi_in: Number(taxiInInput)
      });
      setAnomalyResult(res);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-black text-white tracking-tight flex items-center gap-2">
          <Cpu className="w-6 h-6 text-aviation-cyan" />
          AI & Machine Learning Intelligence Hub
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Real-Time Flight Delay Prediction, Operational Anomaly Detection, and Demand Forecasting Models
        </p>
      </div>

      {/* Grid: Predictor & Anomaly Detector */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Interactive Delay Predictor Form */}
        <div className="lg:col-span-7 bg-aviation-card border border-aviation-border rounded-xl p-5 shadow-lg flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2 mb-1">
              <Zap className="w-4 h-4 text-aviation-accent" />
              Flight Delay Risk Predictor (Random Forest & Gradient Boosting)
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Enter planned flight parameters to evaluate delay probability and forecast duration
            </p>

            <form onSubmit={handlePredict} className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs mb-4">
              <div>
                <label className="text-slate-400 block mb-1">Airline Carrier</label>
                <select
                  value={carrier}
                  onChange={(e) => setCarrier(e.target.value)}
                  className="w-full bg-aviation-navy border border-aviation-border rounded-lg px-2.5 py-1.5 text-white font-mono focus:outline-none"
                >
                  {['DL', 'AA', 'UA', 'WN', 'AS', 'B6', 'NK', 'OO', 'F9', 'HA'].map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Origin Airport</label>
                <input
                  type="text"
                  value={origin}
                  onChange={(e) => setOrigin(e.target.value.toUpperCase())}
                  className="w-full bg-aviation-navy border border-aviation-border rounded-lg px-2.5 py-1.5 text-white uppercase font-mono focus:outline-none"
                  maxLength={3}
                />
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Destination Airport</label>
                <input
                  type="text"
                  value={dest}
                  onChange={(e) => setDest(e.target.value.toUpperCase())}
                  className="w-full bg-aviation-navy border border-aviation-border rounded-lg px-2.5 py-1.5 text-white uppercase font-mono focus:outline-none"
                  maxLength={3}
                />
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Scheduled Dep Hour</label>
                <select
                  value={depHour}
                  onChange={(e) => setDepHour(Number(e.target.value))}
                  className="w-full bg-aviation-navy border border-aviation-border rounded-lg px-2.5 py-1.5 text-white font-mono focus:outline-none"
                >
                  {Array.from({ length: 24 }).map((_, i) => (
                    <option key={i} value={i}>{String(i).padStart(2, '0')}:00</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Weather Condition</label>
                <select
                  value={weatherCondition}
                  onChange={(e) => setWeatherCondition(e.target.value)}
                  className="w-full bg-aviation-navy border border-aviation-border rounded-lg px-2.5 py-1.5 text-white focus:outline-none"
                >
                  {['Clear', 'Cloudy', 'Rain', 'Snow', 'Fog', 'Thunderstorm'].map((w) => (
                    <option key={w} value={w}>{w}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Surface Wind (mph)</label>
                <input
                  type="number"
                  value={windMph}
                  onChange={(e) => setWindMph(Number(e.target.value))}
                  className="w-full bg-aviation-navy border border-aviation-border rounded-lg px-2.5 py-1.5 text-white font-mono focus:outline-none"
                />
              </div>

              <div className="col-span-2 sm:col-span-3 pt-1">
                <button
                  type="submit"
                  disabled={predicting}
                  className="w-full py-2.5 rounded-lg bg-aviation-accent hover:bg-aviation-accent/80 text-white font-semibold text-xs transition-colors flex items-center justify-center gap-2 shadow-lg shadow-aviation-accent/20"
                >
                  <Sparkles className="w-4 h-4" />
                  {predicting ? 'Running ML Inference...' : 'Run Real-Time Delay Inference'}
                </button>
              </div>
            </form>
          </div>

          {/* Prediction Results Banner */}
          {prediction && (
            <div className="bg-aviation-navy/90 border border-aviation-border rounded-xl p-4 mt-2">
              <div className="flex items-center justify-between pb-3 border-b border-aviation-border">
                <div>
                  <span className="text-[11px] text-slate-400 block">Delay Risk Evaluation</span>
                  <span className={`text-lg font-black font-mono ${prediction.risk_tier === 'Critical' || prediction.risk_tier === 'High' ? 'text-red-400' : (prediction.risk_tier === 'Moderate' ? 'text-amber-400' : 'text-emerald-400')}`}>
                    {prediction.risk_tier} Risk ({prediction.delay_probability_pct}%)
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-[11px] text-slate-400 block">Forecasted Arrival Delay</span>
                  <span className="text-lg font-black text-white font-mono">
                    +{prediction.predicted_delay_minutes} min
                  </span>
                </div>
              </div>
              <p className="text-[11px] text-slate-400 font-mono mt-2">
                Features: {prediction.input_features.carrier} • {prediction.input_features.origin}&rarr;{prediction.input_features.dest} • {prediction.input_features.weather_condition} ({prediction.input_features.wind_mph} mph)
              </p>
            </div>
          )}
        </div>

        {/* Operational Anomaly Detector */}
        <div className="lg:col-span-5 bg-aviation-card border border-aviation-border rounded-xl p-5 shadow-lg flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2 mb-1">
              <ShieldAlert className="w-4 h-4 text-aviation-warning" />
              Telemetry Anomaly Detector (Isolation Forest)
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Detects statistical operational outliers in turnaround and taxi latencies
            </p>

            <div className="grid grid-cols-2 gap-3 text-xs mb-4">
              <div>
                <label className="text-slate-400 block mb-1">Dep Delay (min)</label>
                <input
                  type="number"
                  value={depDelayInput}
                  onChange={(e) => setDepDelayInput(Number(e.target.value))}
                  className="w-full bg-aviation-navy border border-aviation-border rounded-lg px-2.5 py-1.5 text-white font-mono"
                />
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Arr Delay (min)</label>
                <input
                  type="number"
                  value={arrDelayInput}
                  onChange={(e) => setArrDelayInput(Number(e.target.value))}
                  className="w-full bg-aviation-navy border border-aviation-border rounded-lg px-2.5 py-1.5 text-white font-mono"
                />
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Taxi-Out (min)</label>
                <input
                  type="number"
                  value={taxiOutInput}
                  onChange={(e) => setTaxiOutInput(Number(e.target.value))}
                  className="w-full bg-aviation-navy border border-aviation-border rounded-lg px-2.5 py-1.5 text-white font-mono"
                />
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Taxi-In (min)</label>
                <input
                  type="number"
                  value={taxiInInput}
                  onChange={(e) => setTaxiInInput(Number(e.target.value))}
                  className="w-full bg-aviation-navy border border-aviation-border rounded-lg px-2.5 py-1.5 text-white font-mono"
                />
              </div>
            </div>

            <button
              onClick={handleDetectAnomaly}
              className="w-full py-2 rounded-lg bg-aviation-navy hover:bg-aviation-navy/70 border border-aviation-border text-white text-xs font-semibold transition-colors"
            >
              Evaluate Anomaly Score
            </button>
          </div>

          {anomalyResult && (
            <div className="bg-aviation-navy/90 border border-aviation-border rounded-xl p-4 mt-3 text-xs font-mono">
              <div className="flex items-center justify-between mb-2">
                <span className="text-slate-400">Classification:</span>
                <span className={`font-bold px-2 py-0.5 rounded ${anomalyResult.is_anomaly ? 'bg-amber-950 text-amber-400 border border-amber-800' : 'bg-emerald-950 text-emerald-400 border border-emerald-800'}`}>
                  {anomalyResult.severity}
                </span>
              </div>
              <div className="flex items-center justify-between text-slate-400">
                <span>Anomaly Score:</span>
                <span className="text-white font-bold">{anomalyResult.anomaly_score}</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Demand / Flight Volume Traffic Forecast Chart */}
      <div className="bg-aviation-card border border-aviation-border rounded-xl p-5 shadow-lg">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2 mb-1">
          <TrendingUp className="w-4 h-4 text-aviation-cyan" />
          Forward 14-Day Network Flight Traffic Volume Forecast
        </h3>
        <p className="text-xs text-slate-400 mb-4">
          Time-Series Seasonality & Moving Demand Projection with 80% Confidence Interval
        </p>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={forecast}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2A3B60" />
              <XAxis dataKey="forecast_date" stroke="#94A3B8" fontSize={11} tickFormatter={(v) => v.slice(5)} />
              <YAxis stroke="#94A3B8" fontSize={11} domain={['auto', 'auto']} />
              <Tooltip
                contentStyle={{ backgroundColor: '#131D38', borderColor: '#2A3B60', borderRadius: '8px', fontSize: '12px' }}
              />
              <Line type="monotone" dataKey="predicted_flight_volume" name="Predicted Flights" stroke="#5BC0BE" strokeWidth={2} dot={{ r: 3 }} />
              <Line type="monotone" dataKey="confidence_upper_80" name="Upper 80% CI" stroke="#2A3B60" strokeDasharray="3 3" dot={false} />
              <Line type="monotone" dataKey="confidence_lower_80" name="Lower 80% CI" stroke="#2A3B60" strokeDasharray="3 3" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
