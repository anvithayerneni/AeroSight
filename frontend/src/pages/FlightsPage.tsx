import React, { useState, useEffect } from 'react';
import { Search, Filter, ChevronLeft, ChevronRight, Eye, RefreshCw } from 'lucide-react';
import { fetchFlights, fetchFlightById } from '../services/api';
import { FlightItem } from '../services/types';
import { StatusBadge } from '../components/StatusBadge';
import { FlightModal } from '../components/FlightModal';

export const FlightsPage: React.FC = () => {
  const [flights, setFlights] = useState<FlightItem[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(0);
  const [limit] = useState(25);
  const [carrierFilter, setCarrierFilter] = useState('');
  const [originFilter, setOriginFilter] = useState('');
  const [destFilter, setDestFilter] = useState('');
  const [delayedOnly, setDelayedOnly] = useState(false);
  const [loading, setLoading] = useState(true);
  const [selectedFlight, setSelectedFlight] = useState<(FlightItem & { delay_breakdown?: any }) | null>(null);

  const loadFlights = async () => {
    setLoading(true);
    try {
      const data = await fetchFlights(
        limit,
        page * limit,
        carrierFilter || undefined,
        originFilter || undefined,
        destFilter || undefined,
        delayedOnly
      );
      setFlights(data.flights);
      setTotalCount(data.total_count);
    } catch (err) {
      console.error('Error fetching flights:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFlights();
  }, [page, carrierFilter, originFilter, destFilter, delayedOnly]);

  const handleViewFlight = async (flightId: string) => {
    try {
      const detail = await fetchFlightById(flightId);
      setSelectedFlight(detail);
    } catch (err) {
      console.error(err);
    }
  };

  const totalPages = Math.ceil(totalCount / limit);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-black text-white tracking-tight">Flight Operations Registry</h2>
          <p className="text-xs text-slate-400 mt-1">
            Searchable Granular Flight Records from the Lakehouse Fact Store
          </p>
        </div>
        <div className="text-xs font-mono text-slate-400">
          Showing {totalCount.toLocaleString()} total flights
        </div>
      </div>

      {/* Filters Bar */}
      <div className="bg-aviation-card border border-aviation-border rounded-xl p-4 shadow-lg flex flex-wrap items-center gap-3">
        <div className="flex items-center space-x-2 bg-aviation-navy border border-aviation-border rounded-lg px-3 py-2 text-xs">
          <Filter className="w-3.5 h-3.5 text-aviation-cyan" />
          <span className="text-slate-400 font-semibold">Carrier:</span>
          <select
            value={carrierFilter}
            onChange={(e) => { setCarrierFilter(e.target.value); setPage(0); }}
            className="bg-transparent text-white font-mono focus:outline-none"
          >
            <option value="" className="bg-aviation-navy">ALL</option>
            {['DL', 'AA', 'UA', 'WN', 'AS', 'B6', 'NK', 'OO', 'F9', 'HA'].map((c) => (
              <option key={c} value={c} className="bg-aviation-navy">{c}</option>
            ))}
          </select>
        </div>

        <input
          type="text"
          placeholder="Origin (e.g. ATL)"
          value={originFilter}
          onChange={(e) => { setOriginFilter(e.target.value.toUpperCase()); setPage(0); }}
          className="bg-aviation-navy border border-aviation-border rounded-lg px-3 py-2 text-xs text-white uppercase placeholder-slate-500 font-mono w-28 focus:outline-none focus:border-aviation-accent"
          maxLength={3}
        />

        <input
          type="text"
          placeholder="Dest (e.g. LGA)"
          value={destFilter}
          onChange={(e) => { setDestFilter(e.target.value.toUpperCase()); setPage(0); }}
          className="bg-aviation-navy border border-aviation-border rounded-lg px-3 py-2 text-xs text-white uppercase placeholder-slate-500 font-mono w-28 focus:outline-none focus:border-aviation-accent"
          maxLength={3}
        />

        <label className="flex items-center space-x-2 text-xs text-slate-300 cursor-pointer bg-aviation-navy border border-aviation-border rounded-lg px-3 py-2">
          <input
            type="checkbox"
            checked={delayedOnly}
            onChange={(e) => { setDelayedOnly(e.target.checked); setPage(0); }}
            className="rounded border-aviation-border text-aviation-accent focus:ring-0"
          />
          <span>Delayed Only (&ge;15m)</span>
        </label>

        <button
          onClick={loadFlights}
          className="ml-auto p-2 rounded-lg bg-aviation-navy hover:bg-aviation-navy/70 border border-aviation-border text-slate-300"
          title="Reload"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-aviation-cyan' : ''}`} />
        </button>
      </div>

      {/* Flight Data Table */}
      <div className="bg-aviation-card border border-aviation-border rounded-xl shadow-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-aviation-navy text-slate-400 uppercase tracking-wider text-[11px] border-b border-aviation-border">
              <tr>
                <th className="py-3 px-4">Flight ID</th>
                <th className="py-3 px-4">Date</th>
                <th className="py-3 px-4">Flight #</th>
                <th className="py-3 px-4">Route</th>
                <th className="py-3 px-4">Sched Dep</th>
                <th className="py-3 px-4">Dep Delay</th>
                <th className="py-3 px-4">Sched Arr</th>
                <th className="py-3 px-4">Arr Delay</th>
                <th className="py-3 px-4">Weather</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-aviation-border font-mono">
              {loading ? (
                <tr>
                  <td colSpan={11} className="text-center py-12 text-slate-400">
                    <div className="flex items-center justify-center space-x-2">
                      <div className="w-5 h-5 border-2 border-aviation-accent border-t-transparent rounded-full animate-spin" />
                      <span>Querying Fact Flights Table...</span>
                    </div>
                  </td>
                </tr>
              ) : flights.length === 0 ? (
                <tr>
                  <td colSpan={11} className="text-center py-12 text-slate-400">
                    No flights matching current filter criteria.
                  </td>
                </tr>
              ) : (
                flights.map((f) => (
                  <tr key={f.flight_id} className="hover:bg-aviation-navy/50 transition-colors">
                    <td className="py-3 px-4 text-slate-400">{f.flight_id}</td>
                    <td className="py-3 px-4 text-slate-300">{f.flight_date}</td>
                    <td className="py-3 px-4 font-bold text-white font-sans">
                      <span className="px-1.5 py-0.5 rounded bg-aviation-accent/20 text-aviation-cyan text-[11px] font-mono mr-1.5">
                        {f.carrier_key}
                      </span>
                      {f.flight_number}
                    </td>
                    <td className="py-3 px-4 text-slate-200">
                      {f.origin_airport_key} &rarr; {f.dest_airport_key}
                    </td>
                    <td className="py-3 px-4 text-slate-300">{String(f.crs_dep_time).padStart(4, '0')}</td>
                    <td className={`py-3 px-4 ${f.dep_delay && f.dep_delay > 0 ? 'text-amber-400 font-bold' : 'text-slate-300'}`}>
                      {f.dep_delay !== undefined && f.dep_delay !== null ? `${f.dep_delay > 0 ? '+' : ''}${f.dep_delay}m` : '-'}
                    </td>
                    <td className="py-3 px-4 text-slate-300">{String(f.crs_arr_time).padStart(4, '0')}</td>
                    <td className={`py-3 px-4 font-bold ${f.arr_delay && f.arr_delay >= 15 ? 'text-amber-400' : 'text-emerald-400'}`}>
                      {f.arr_delay !== undefined && f.arr_delay !== null ? `${f.arr_delay > 0 ? '+' : ''}${f.arr_delay}m` : '-'}
                    </td>
                    <td className="py-3 px-4 text-slate-400 text-[11px]">
                      {f.origin_weather_condition || 'Clear'}
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge status={f.cancelled ? 'CANCELLED' : (f.is_delayed_15 ? 'DELAYED' : 'ON-TIME')} delayMinutes={f.arr_delay} />
                    </td>
                    <td className="py-3 px-4 text-center">
                      <button
                        onClick={() => handleViewFlight(f.flight_id)}
                        className="p-1.5 rounded bg-aviation-navy hover:bg-aviation-accent text-slate-300 hover:text-white transition-colors"
                        title="View Flight Details"
                      >
                        <Eye className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div className="p-4 bg-aviation-navy/80 border-t border-aviation-border flex items-center justify-between text-xs">
          <span className="text-slate-400 font-mono">
            Page {page + 1} of {totalPages || 1}
          </span>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0 || loading}
              className="px-3 py-1.5 rounded-lg bg-aviation-card hover:bg-aviation-cardHover border border-aviation-border text-slate-300 disabled:opacity-40"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
              disabled={page >= totalPages - 1 || loading}
              className="px-3 py-1.5 rounded-lg bg-aviation-card hover:bg-aviation-cardHover border border-aviation-border text-slate-300 disabled:opacity-40"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Detail Modal */}
      {selectedFlight && (
        <FlightModal flight={selectedFlight} onClose={() => setSelectedFlight(null)} />
      )}
    </div>
  );
};
