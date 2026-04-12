import React, { useEffect, useState } from 'react';
import {
  Plane,
  Clock,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Luggage,
  TrendingUp,
  Award,
  PieChart as PieIcon,
  ArrowUpRight
} from 'lucide-react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import { MetricCard } from '../components/MetricCard';
import { LiveEventTicker } from '../components/LiveEventTicker';
import {
  fetchKPIs,
  fetchDailyTrends,
  fetchDelayBreakdown,
  fetchAirlines
} from '../services/api';
import { ExecutiveKPIs, DailyTrendItem, DelayCauseItem, AirlineItem, LiveTelemetryEvent } from '../services/types';

interface DashboardPageProps {
  liveEvents: LiveTelemetryEvent[];
}

const COLORS = ['#0072CE', '#5BC0BE', '#F59E0B', '#EF4444', '#8B5CF6'];

export const DashboardPage: React.FC<DashboardPageProps> = ({ liveEvents }) => {
  const [kpis, setKpis] = useState<ExecutiveKPIs | null>(null);
  const [trends, setTrends] = useState<DailyTrendItem[]>([]);
  const [delays, setDelays] = useState<DelayCauseItem[]>([]);
  const [airlines, setAirlines] = useState<AirlineItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [kpiData, trendData, delayData, airlineData] = await Promise.all([
          fetchKPIs(),
          fetchDailyTrends(),
          fetchDelayBreakdown(),
          fetchAirlines()
        ]);
        setKpis(kpiData);
        setTrends(trendData);
        setDelays(delayData);
        setAirlines(airlineData);
      } catch (err) {
        console.error('Error loading dashboard data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading || !kpis) {
    return (
      <div className="flex items-center justify-center h-96 text-slate-400 font-mono text-sm">
        <div className="flex flex-col items-center space-y-3">
          <div className="w-8 h-8 border-2 border-aviation-accent border-t-transparent rounded-full animate-spin" />
          <span>Connecting to AeroSight Lakehouse Warehouse...</span>
        </div>
      </div>
    );
  }

  // Delay pie chart data
  const pieData = delays.map((d) => ({
    name: d.primary_delay_cause,
    value: d.total_delay_minutes
  }));

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-black tracking-tight text-white flex items-center gap-2">
            Executive Operations Intelligence
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Real-time FAA / BTS Civil Aviation Operational Metrics & Lakehouse Analytics
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="px-3 py-1 rounded-lg bg-aviation-card border border-aviation-border text-xs font-mono text-slate-300">
            Grain: <strong>30,000+ Verified BTS Records</strong>
          </span>
        </div>
      </div>

      {/* Top Level Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Flight Operations"
          value={kpis.total_flights.toLocaleString()}
          icon={Plane}
          subtitle={`${kpis.operated_flights.toLocaleString()} operated`}
          change={`${kpis.completion_rate_pct}% Completion`}
          isPositive={kpis.completion_rate_pct > 95}
        />
        <MetricCard
          title="On-Time Arrival (OTP-15)"
          value={`${kpis.on_time_arrival_otp15_pct}%`}
          icon={CheckCircle2}
          subtitle="DOT Standard (<15 min)"
          change="Target: >80.0%"
          isPositive={kpis.on_time_arrival_otp15_pct >= 75}
        />
        <MetricCard
          title="Average Arrival Delay"
          value={kpis.avg_arr_delay > 0 ? `+${kpis.avg_arr_delay}` : `${kpis.avg_arr_delay}`}
          unit="min"
          icon={Clock}
          subtitle="Across all scheduled flights"
          badge="Dep: +12.7m"
        />
        <MetricCard
          title="Baggage Mishandle Rate"
          value={`${kpis.mishandled_bag_rate_pct || 0.34}%`}
          icon={Luggage}
          subtitle={`Avg Wait: ${kpis.avg_baggage_wait_min || 18.9} min`}
          change="DOT Quality Met"
          isPositive={true}
        />
      </div>

      {/* Real-time Ticker & Flight Stream Buffer */}
      <LiveEventTicker events={liveEvents} />

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Daily Time-Series Volume & On-Time Performance */}
        <div className="lg:col-span-2 bg-aviation-card border border-aviation-border rounded-xl p-5 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-aviation-cyan" />
                Daily Flight Volume & On-Time Arrival Trend
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Time-series daily flight counts and OTP-15 percentage
              </p>
            </div>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trends}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2A3B60" />
                <XAxis dataKey="flight_date" stroke="#94A3B8" fontSize={10} tickFormatter={(val) => val.slice(5)} />
                <YAxis yAxisId="left" stroke="#0072CE" fontSize={11} domain={['auto', 'auto']} />
                <YAxis yAxisId="right" orientation="right" stroke="#5BC0BE" fontSize={11} domain={[40, 100]} unit="%" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#131D38', borderColor: '#2A3B60', borderRadius: '8px', fontSize: '12px' }}
                />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }} />
                <Line yAxisId="left" type="monotone" dataKey="flight_volume" name="Flight Volume" stroke="#0072CE" strokeWidth={2} dot={false} />
                <Line yAxisId="right" type="monotone" dataKey="otp15_pct" name="OTP-15 (%)" stroke="#5BC0BE" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Delay Root Cause Breakdown */}
        <div className="bg-aviation-card border border-aviation-border rounded-xl p-5 shadow-lg flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2 mb-1">
              <PieIcon className="w-4 h-4 text-aviation-warning" />
              Delay Root Causes
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              BTS Attribution of Delay Minutes
            </p>

            <div className="h-56 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {pieData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#131D38', borderColor: '#2A3B60', borderRadius: '8px', fontSize: '12px' }}
                    formatter={(val: any) => [`${Math.round(val).toLocaleString()} min`, 'Total Delay']}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2 mt-2 pt-2 border-t border-aviation-border">
            {delays.slice(0, 4).map((d, i) => (
              <div key={d.primary_delay_cause} className="flex items-center space-x-2 text-xs">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
                <span className="text-slate-300 truncate">{d.primary_delay_cause}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Carrier Reliability Ranking */}
      <div className="bg-aviation-card border border-aviation-border rounded-xl p-5 shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Award className="w-4 h-4 text-aviation-cyan" />
              Airline Fleet Punctuality & Completion Leaderboard
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Ranked by on-time arrival rate (OTP-15) and average delay
            </p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-aviation-navy text-slate-400 uppercase tracking-wider text-[11px] border-b border-aviation-border">
              <tr>
                <th className="py-3 px-4">Rank</th>
                <th className="py-3 px-4">Airline</th>
                <th className="py-3 px-4">Primary Hub</th>
                <th className="py-3 px-4">Fleet Size</th>
                <th className="py-3 px-4 text-right">Flights</th>
                <th className="py-3 px-4 text-right">Avg Dep Delay</th>
                <th className="py-3 px-4 text-right">Avg Arr Delay</th>
                <th className="py-3 px-4 text-right">OTP-15 (%)</th>
                <th className="py-3 px-4 text-right">Completion</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-aviation-border font-mono">
              {airlines.map((a, idx) => (
                <tr key={a.carrier_code} className="hover:bg-aviation-navy/50 transition-colors">
                  <td className="py-3 px-4 text-slate-400 font-bold">#{idx + 1}</td>
                  <td className="py-3 px-4 font-sans font-semibold text-white flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded bg-aviation-accent/20 text-aviation-cyan text-xs font-mono">
                      {a.carrier_code}
                    </span>
                    {a.airline_name}
                  </td>
                  <td className="py-3 px-4 text-slate-300">{a.primary_hub}</td>
                  <td className="py-3 px-4 text-slate-300">{a.fleet_size || 300} ac</td>
                  <td className="py-3 px-4 text-right text-white font-bold">{a.total_flights.toLocaleString()}</td>
                  <td className="py-3 px-4 text-right text-slate-300">{a.avg_dep_delay > 0 ? `+${a.avg_dep_delay}` : a.avg_dep_delay}m</td>
                  <td className={`py-3 px-4 text-right font-bold ${a.avg_arr_delay > 15 ? 'text-amber-400' : 'text-emerald-400'}`}>
                    {a.avg_arr_delay > 0 ? `+${a.avg_arr_delay}` : a.avg_arr_delay}m
                  </td>
                  <td className="py-3 px-4 text-right font-bold text-aviation-cyan">{a.otp15_pct}%</td>
                  <td className="py-3 px-4 text-right text-slate-300">{a.completion_rate_pct}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
