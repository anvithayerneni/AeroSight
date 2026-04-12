import React, { useState, useEffect } from 'react';
import { Route as RouteIcon, TrendingDown, ArrowRight, MapPin, Gauge } from 'lucide-react';
import { fetchRoutes, fetchTopDelayedRoutes } from '../services/api';
import { RouteItem } from '../services/types';

export const RoutesPage: React.FC = () => {
  const [routes, setRoutes] = useState<RouteItem[]>([]);
  const [delayedRoutes, setDelayedRoutes] = useState<RouteItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [allRoutes, topDelayed] = await Promise.all([
          fetchRoutes(),
          fetchTopDelayedRoutes()
        ]);
        setRoutes(allRoutes);
        setDelayedRoutes(topDelayed);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-black text-white tracking-tight">Route Network & Corridor Bottlenecks</h2>
        <p className="text-xs text-slate-400 mt-1">
          City-Pair Route Punctuality, Distance Segments, and Airway Delay Variance
        </p>
      </div>

      {/* Top Delayed Bottlenecks Table */}
      <div className="bg-aviation-card border border-aviation-border rounded-xl p-5 shadow-lg">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2 mb-4">
          <TrendingDown className="w-4 h-4 text-aviation-warning" />
          Top Delayed Operational Route Corridors (High Latency)
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-aviation-navy text-slate-400 uppercase tracking-wider text-[11px] border-b border-aviation-border">
              <tr>
                <th className="py-3 px-4">Route Corridor</th>
                <th className="py-3 px-4">Distance</th>
                <th className="py-3 px-4 text-right">Flight Count</th>
                <th className="py-3 px-4 text-right">Avg Dep Delay</th>
                <th className="py-3 px-4 text-right">Avg Arr Delay</th>
                <th className="py-3 px-4 text-right">Delayed Flights (%)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-aviation-border font-mono">
              {delayedRoutes.map((r) => (
                <tr key={r.route_key} className="hover:bg-aviation-navy/50 transition-colors">
                  <td className="py-3 px-4 font-bold text-white flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded bg-aviation-navy border border-aviation-border text-aviation-cyan">
                      {r.origin}
                    </span>
                    <ArrowRight className="w-3.5 h-3.5 text-slate-400" />
                    <span className="px-2 py-0.5 rounded bg-aviation-navy border border-aviation-border text-aviation-cyan">
                      {r.dest}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-slate-300">{r.distance_miles} NM</td>
                  <td className="py-3 px-4 text-right text-white font-bold">{r.flight_count}</td>
                  <td className="py-3 px-4 text-right text-slate-300">+{r.avg_dep_delay}m</td>
                  <td className="py-3 px-4 text-right font-bold text-amber-400">+{r.avg_arr_delay}m</td>
                  <td className="py-3 px-4 text-right font-bold text-aviation-warning">{r.otp15_pct ? (100 - r.otp15_pct).toFixed(1) : 42.5}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Network Routes Table */}
      <div className="bg-aviation-card border border-aviation-border rounded-xl p-5 shadow-lg">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2 mb-4">
          <RouteIcon className="w-4 h-4 text-aviation-cyan" />
          Primary Network Flight Corridors
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-aviation-navy text-slate-400 uppercase tracking-wider text-[11px] border-b border-aviation-border">
              <tr>
                <th className="py-3 px-4">Route</th>
                <th className="py-3 px-4">Segment Haul</th>
                <th className="py-3 px-4">Distance</th>
                <th className="py-3 px-4 text-right">Flight Volume</th>
                <th className="py-3 px-4 text-right">Avg Arr Delay</th>
                <th className="py-3 px-4 text-right">OTP-15 (%)</th>
                <th className="py-3 px-4 text-right">Cancellation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-aviation-border font-mono">
              {routes.slice(0, 20).map((r) => (
                <tr key={r.route_key} className="hover:bg-aviation-navy/50 transition-colors">
                  <td className="py-3 px-4 font-bold text-white">
                    {r.origin} &rarr; {r.dest}
                  </td>
                  <td className="py-3 px-4 text-slate-300 font-sans">{r.distance_category || 'Medium Haul'}</td>
                  <td className="py-3 px-4 text-slate-300">{r.distance_miles} NM</td>
                  <td className="py-3 px-4 text-right text-white font-bold">{r.flight_count}</td>
                  <td className={`py-3 px-4 text-right font-bold ${r.avg_arr_delay > 15 ? 'text-amber-400' : 'text-emerald-400'}`}>
                    {r.avg_arr_delay > 0 ? `+${r.avg_arr_delay}` : r.avg_arr_delay}m
                  </td>
                  <td className="py-3 px-4 text-right font-bold text-aviation-cyan">{r.otp15_pct}%</td>
                  <td className="py-3 px-4 text-right text-slate-300">{r.cancellation_rate_pct}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
