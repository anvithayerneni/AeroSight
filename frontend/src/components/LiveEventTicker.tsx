import React from 'react';
import { Radio, AlertTriangle } from 'lucide-react';
import { LiveTelemetryEvent } from '../services/types';
import { StatusBadge } from './StatusBadge';

interface LiveEventTickerProps {
  events: LiveTelemetryEvent[];
}

export const LiveEventTicker: React.FC<LiveEventTickerProps> = ({ events }) => {
  return (
    <div className="bg-aviation-card border border-aviation-border rounded-xl p-4 shadow-lg">
      <div className="flex items-center justify-between mb-3 border-b border-aviation-border pb-2">
        <div className="flex items-center space-x-2">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-red-500"></span>
          </span>
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
            Real-Time Stream Feed (Kafka Event Buffer)
          </h3>
        </div>
        <span className="text-[11px] font-mono text-slate-400">
          Buffer Size: {events.length}
        </span>
      </div>

      <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
        {events.length === 0 ? (
          <div className="text-center py-6 text-xs text-slate-500 font-mono">
            Awaiting streaming events from Kafka topic...
          </div>
        ) : (
          events.slice(0, 10).map((evt) => (
            <div
              key={evt.event_id}
              className="flex items-center justify-between p-2.5 rounded-lg bg-aviation-navy/70 border border-aviation-border/60 text-xs hover:border-aviation-accent/50 transition-colors"
            >
              <div className="flex items-center space-x-3">
                <span className="font-mono text-slate-400 text-[10px]">
                  {evt.timestamp.split(' ')[1] || evt.timestamp}
                </span>
                <span className="font-bold text-white font-mono">
                  {evt.carrier_code} {evt.flight_number}
                </span>
                <span className="text-slate-300 font-mono">
                  {evt.origin_airport} → {evt.dest_airport}
                </span>
                <span className="text-[10px] text-slate-400 px-1.5 py-0.5 rounded bg-aviation-dark border border-aviation-border">
                  Gate {evt.gate}
                </span>
              </div>

              <div className="flex items-center space-x-3">
                <StatusBadge status={evt.status} delayMinutes={evt.arr_delay} />
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
