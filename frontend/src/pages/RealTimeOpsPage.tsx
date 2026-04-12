import React, { useState } from 'react';
import { Radio, AlertOctagon, Plane, Wind, MapPin, Gauge } from 'lucide-react';
import { LiveTelemetryEvent } from '../services/types';
import { StatusBadge } from '../components/StatusBadge';

interface RealTimeOpsPageProps {
  liveEvents: LiveTelemetryEvent[];
}

export const RealTimeOpsPage: React.FC<RealTimeOpsPageProps> = ({ liveEvents }) => {
  const [activeTab, setActiveTab] = useState<'stream' | 'radar'>('stream');

  const delayedEvents = liveEvents.filter((e) => e.status === 'DELAYED');
  const onTimeEvents = liveEvents.filter((e) => e.status === 'ON-TIME');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-black text-white tracking-tight flex items-center gap-2">
            Real-Time Flight Operations Radar
            <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-ping" />
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Live Telemetry Ingestion from Apache Kafka Topic: <code className="text-aviation-cyan">flight_status</code>
          </p>
        </div>
      </div>

      {/* Streaming Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 font-mono">
        <div className="bg-aviation-card p-4 rounded-xl border border-aviation-border flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-400 block mb-1">Live Events Received</span>
            <span className="text-2xl font-bold text-white">{liveEvents.length}</span>
          </div>
          <Radio className="w-6 h-6 text-aviation-accent animate-pulse" />
        </div>

        <div className="bg-aviation-card p-4 rounded-xl border border-aviation-border flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-400 block mb-1">Active Punctual Flights</span>
            <span className="text-2xl font-bold text-emerald-400">{onTimeEvents.length}</span>
          </div>
          <Plane className="w-6 h-6 text-emerald-400" />
        </div>

        <div className="bg-aviation-card p-4 rounded-xl border border-aviation-border flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-400 block mb-1">Delay Spikes Detected</span>
            <span className="text-2xl font-bold text-amber-400">{delayedEvents.length}</span>
          </div>
          <AlertOctagon className="w-6 h-6 text-amber-400" />
        </div>
      </div>

      {/* Radar Flight Ticker Table */}
      <div className="bg-aviation-card border border-aviation-border rounded-xl shadow-lg p-5">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2 mb-4">
          <Plane className="w-4 h-4 text-aviation-cyan" />
          Active Flight Telemetry Feed
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-aviation-navy text-slate-400 uppercase tracking-wider text-[11px] border-b border-aviation-border">
              <tr>
                <th className="py-3 px-4">Event ID</th>
                <th className="py-3 px-4">Timestamp (UTC)</th>
                <th className="py-3 px-4">Flight</th>
                <th className="py-3 px-4">Corridor</th>
                <th className="py-3 px-4">Gate</th>
                <th className="py-3 px-4">Altitude (ft)</th>
                <th className="py-3 px-4">Speed (kts)</th>
                <th className="py-3 px-4 text-right">Delay</th>
                <th className="py-3 px-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-aviation-border">
              {liveEvents.length === 0 ? (
                <tr>
                  <td colSpan={9} className="text-center py-12 text-slate-400">
                    Listening for incoming Kafka event stream...
                  </td>
                </tr>
              ) : (
                liveEvents.map((evt) => (
                  <tr key={evt.event_id} className="hover:bg-aviation-navy/50 transition-colors">
                    <td className="py-3 px-4 text-slate-400">#{evt.event_id}</td>
                    <td className="py-3 px-4 text-slate-300">{evt.timestamp}</td>
                    <td className="py-3 px-4 font-bold text-white font-sans flex items-center gap-1.5">
                      <span className="px-1.5 py-0.5 rounded bg-aviation-accent/20 text-aviation-cyan text-[11px] font-mono">
                        {evt.carrier_code}
                      </span>
                      {evt.flight_number}
                    </td>
                    <td className="py-3 px-4 text-slate-200">
                      {evt.origin_airport} &rarr; {evt.dest_airport}
                    </td>
                    <td className="py-3 px-4 text-slate-300">Gate {evt.gate}</td>
                    <td className="py-3 px-4 text-slate-300">{evt.altitude_ft.toLocaleString()}</td>
                    <td className="py-3 px-4 text-slate-300">{evt.ground_speed_knots}</td>
                    <td className={`py-3 px-4 text-right font-bold ${evt.arr_delay >= 15 ? 'text-amber-400' : 'text-emerald-400'}`}>
                      {evt.arr_delay > 0 ? `+${evt.arr_delay}` : evt.arr_delay}m
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge status={evt.status} delayMinutes={evt.arr_delay} />
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
