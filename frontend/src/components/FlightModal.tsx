import React from 'react';
import { X, Plane, Clock, CloudSun, MapPin, Gauge, ShieldAlert } from 'lucide-react';
import { FlightItem } from '../services/types';
import { StatusBadge } from './StatusBadge';

interface FlightModalProps {
  flight: (FlightItem & { delay_breakdown?: any }) | null;
  onClose: () => void;
}

export const FlightModal: React.FC<FlightModalProps> = ({ flight, onClose }) => {
  if (!flight) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-aviation-card border border-aviation-border rounded-2xl max-w-2xl w-full p-6 shadow-2xl relative animate-in fade-in zoom-in duration-150">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-1.5 rounded-lg bg-aviation-navy text-slate-400 hover:text-white border border-aviation-border transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="flex items-center space-x-3 mb-6 pb-4 border-b border-aviation-border">
          <div className="p-3 rounded-xl bg-aviation-accent text-white shadow-lg shadow-aviation-accent/30">
            <Plane className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-xl font-bold text-white font-mono">
                {flight.carrier_key} {flight.flight_number}
              </h2>
              <StatusBadge status={flight.cancelled ? 'CANCELLED' : (flight.is_delayed_15 ? 'DELAYED' : 'ON-TIME')} delayMinutes={flight.arr_delay} />
            </div>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              Flight ID: {flight.flight_id} • Date: {flight.flight_date} • Tail: {flight.aircraft_key || 'N/A'}
            </p>
          </div>
        </div>

        {/* Route Corridor Banner */}
        <div className="grid grid-cols-3 items-center bg-aviation-navy/70 border border-aviation-border p-4 rounded-xl mb-6 text-center">
          <div>
            <span className="text-2xl font-black text-white font-mono">{flight.origin_airport_key}</span>
            <p className="text-xs text-slate-400 mt-0.5">Origin Airport</p>
            <p className="text-xs text-aviation-cyan font-mono mt-1">
              Sched: {String(flight.crs_dep_time).padStart(4, '0')}
            </p>
          </div>

          <div className="flex flex-col items-center">
            <span className="text-xs text-slate-400 font-mono mb-1">{flight.distance} NM</span>
            <div className="w-full flex items-center justify-center relative">
              <div className="h-[2px] w-full bg-aviation-border"></div>
              <Plane className="w-4 h-4 text-aviation-accent absolute bg-aviation-navy px-0.5" />
            </div>
            <span className="text-[11px] text-slate-400 mt-1">Direct Routing</span>
          </div>

          <div>
            <span className="text-2xl font-black text-white font-mono">{flight.dest_airport_key}</span>
            <p className="text-xs text-slate-400 mt-0.5">Destination Airport</p>
            <p className="text-xs text-aviation-cyan font-mono mt-1">
              Sched: {String(flight.crs_arr_time).padStart(4, '0')}
            </p>
          </div>
        </div>

        {/* Operational Metrics Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
          <div className="bg-aviation-navy/40 p-3 rounded-lg border border-aviation-border">
            <span className="text-[11px] text-slate-400 block mb-1">Departure Delay</span>
            <span className={`text-base font-bold font-mono ${flight.dep_delay && flight.dep_delay > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>
              {flight.dep_delay !== undefined && flight.dep_delay !== null ? `${flight.dep_delay > 0 ? '+' : ''}${flight.dep_delay} min` : 'N/A'}
            </span>
          </div>

          <div className="bg-aviation-navy/40 p-3 rounded-lg border border-aviation-border">
            <span className="text-[11px] text-slate-400 block mb-1">Arrival Delay</span>
            <span className={`text-base font-bold font-mono ${flight.arr_delay && flight.arr_delay > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>
              {flight.arr_delay !== undefined && flight.arr_delay !== null ? `${flight.arr_delay > 0 ? '+' : ''}${flight.arr_delay} min` : 'N/A'}
            </span>
          </div>

          <div className="bg-aviation-navy/40 p-3 rounded-lg border border-aviation-border">
            <span className="text-[11px] text-slate-400 block mb-1">Taxi-Out Time</span>
            <span className="text-base font-bold font-mono text-slate-200">
              {flight.taxi_out || 0} min
            </span>
          </div>

          <div className="bg-aviation-navy/40 p-3 rounded-lg border border-aviation-border">
            <span className="text-[11px] text-slate-400 block mb-1">Origin Weather</span>
            <span className="text-sm font-semibold text-slate-200">
              {flight.origin_weather_condition || 'Clear'} ({flight.origin_temp_f || 50}°F)
            </span>
          </div>
        </div>

        {/* Delay Root Cause Breakdown if delayed */}
        {flight.delay_breakdown && (
          <div className="bg-aviation-navy/80 border border-aviation-border rounded-xl p-4">
            <h4 className="text-xs font-bold uppercase tracking-wider text-amber-400 flex items-center gap-1.5 mb-2">
              <ShieldAlert className="w-4 h-4" />
              Root-Cause Delay Attribution (BTS Standard)
            </h4>
            <div className="grid grid-cols-5 gap-2 text-center text-xs">
              <div className="p-2 rounded bg-aviation-dark border border-aviation-border">
                <span className="text-[10px] text-slate-400 block">Carrier</span>
                <span className="font-bold text-white font-mono">{flight.delay_breakdown.carrier_delay || 0}m</span>
              </div>
              <div className="p-2 rounded bg-aviation-dark border border-aviation-border">
                <span className="text-[10px] text-slate-400 block">Weather</span>
                <span className="font-bold text-white font-mono">{flight.delay_breakdown.weather_delay || 0}m</span>
              </div>
              <div className="p-2 rounded bg-aviation-dark border border-aviation-border">
                <span className="text-[10px] text-slate-400 block">NAS</span>
                <span className="font-bold text-white font-mono">{flight.delay_breakdown.nas_delay || 0}m</span>
              </div>
              <div className="p-2 rounded bg-aviation-dark border border-aviation-border">
                <span className="text-[10px] text-slate-400 block">Late Aircraft</span>
                <span className="font-bold text-white font-mono">{flight.delay_breakdown.late_aircraft_delay || 0}m</span>
              </div>
              <div className="p-2 rounded bg-aviation-dark border border-aviation-border">
                <span className="text-[10px] text-slate-400 block">Security</span>
                <span className="font-bold text-white font-mono">{flight.delay_breakdown.security_delay || 0}m</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
