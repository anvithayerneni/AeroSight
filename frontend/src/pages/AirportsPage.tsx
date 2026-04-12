import React, { useState, useEffect } from 'react';
import { Building2, MapPin, Gauge, Clock, AlertTriangle, ShieldCheck } from 'lucide-react';
import { fetchAirports } from '../services/api';
import { AirportItem } from '../services/types';

export const AirportsPage: React.FC = () => {
  const [airports, setAirports] = useState<AirportItem[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [hubFilter, setHubFilter] = useState('ALL');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchAirports();
        setAirports(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const filteredAirports = airports.filter((a) => {
    const matchesSearch =
      a.iata.toLowerCase().includes(searchTerm.toLowerCase()) ||
      a.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      a.city.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesHub = hubFilter === 'ALL' || a.hub === hubFilter;
    return matchesSearch && matchesHub;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-black text-white tracking-tight">Airport Congestion & Hub Analytics</h2>
          <p className="text-xs text-slate-400 mt-1">
            Origin Departures, Runway Taxi-Out Latencies, and Hub Gate Capacity Metrics
          </p>
        </div>
      </div>

      {/* Filter controls */}
      <div className="bg-aviation-card border border-aviation-border rounded-xl p-4 shadow-lg flex flex-wrap items-center gap-3">
        <input
          type="text"
          placeholder="Search Airport IATA, City, or Name..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="bg-aviation-navy border border-aviation-border rounded-lg px-3 py-2 text-xs text-white placeholder-slate-500 w-72 focus:outline-none focus:border-aviation-accent"
        />

        <div className="flex items-center space-x-2 bg-aviation-navy border border-aviation-border rounded-lg px-3 py-2 text-xs">
          <span className="text-slate-400 font-semibold">Hub Tier:</span>
          <select
            value={hubFilter}
            onChange={(e) => setHubFilter(e.target.value)}
            className="bg-transparent text-white font-mono focus:outline-none"
          >
            <option value="ALL" className="bg-aviation-navy">ALL HUBS</option>
            <option value="Large Hub" className="bg-aviation-navy">Large Hub</option>
            <option value="Medium Hub" className="bg-aviation-navy">Medium Hub</option>
          </select>
        </div>
      </div>

      {/* Airport Grid Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {loading ? (
          <div className="col-span-3 text-center py-12 text-slate-400 font-mono">
            Loading airport metrics from data warehouse...
          </div>
        ) : (
          filteredAirports.map((ap) => (
            <div
              key={ap.iata}
              className="bg-aviation-card border border-aviation-border rounded-xl p-5 shadow-lg hover:border-aviation-accent/50 transition-all duration-150 relative overflow-hidden"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <div className="px-2.5 py-1.5 rounded-lg bg-aviation-accent/20 border border-aviation-accent/40 text-aviation-cyan font-black text-lg font-mono">
                    {ap.iata}
                  </div>
                  <div>
                    <h3 className="font-bold text-white text-sm leading-snug">{ap.name}</h3>
                    <p className="text-xs text-slate-400 flex items-center gap-1 mt-0.5">
                      <MapPin className="w-3 h-3 text-aviation-slate" />
                      {ap.city}, {ap.state}
                    </p>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-2 bg-aviation-navy/60 p-3 rounded-lg border border-aviation-border text-center font-mono my-3">
                <div>
                  <span className="text-[10px] text-slate-400 uppercase block">Departures</span>
                  <span className="text-sm font-bold text-white">
                    {ap.total_departures ? ap.total_departures.toLocaleString() : 0}
                  </span>
                </div>

                <div>
                  <span className="text-[10px] text-slate-400 uppercase block">Avg Taxi-Out</span>
                  <span className="text-sm font-bold text-slate-200">
                    {ap.avg_taxi_out_min || 0}m
                  </span>
                </div>

                <div>
                  <span className="text-[10px] text-slate-400 uppercase block">Dep Delay</span>
                  <span className={`text-sm font-bold ${(ap.avg_dep_delay_min || 0) > 15 ? 'text-amber-400' : 'text-emerald-400'}`}>
                    {(ap.avg_dep_delay_min || 0) > 0 ? `+${ap.avg_dep_delay_min}` : (ap.avg_dep_delay_min || 0)}m
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between text-xs text-slate-400 mt-2">
                <span className="px-2 py-0.5 rounded bg-aviation-navy border border-aviation-border text-[11px] font-mono">
                  {ap.hub || 'Commercial Hub'}
                </span>
                <span className="font-mono">
                  Gates: <strong>{ap.gates || 'N/A'}</strong>
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
