import React, { useState, useEffect } from 'react';
import { ClockAlert, ShieldAlert, BarChart3, Activity, Info } from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import { fetchDelayBreakdown, fetchStatisticalAnalysis } from '../services/api';
import { DelayCauseItem } from '../services/types';

export const DelayAnalyticsPage: React.FC = () => {
  const [delays, setDelays] = useState<DelayCauseItem[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [delayData, statsData] = await Promise.all([
          fetchDelayBreakdown(),
          fetchStatisticalAnalysis()
        ]);
        setDelays(delayData);
        setStats(statsData);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading || !stats) {
    return (
      <div className="flex items-center justify-center h-96 text-slate-400 font-mono text-sm">
        <span>Calculating statistical distributions & hypothesis tests...</span>
      </div>
    );
  }

  const arrStats = stats.descriptive_statistics.arrival_delay;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-black text-white tracking-tight">Delay Attribution & Statistical Analysis</h2>
        <p className="text-xs text-slate-400 mt-1">
          Root-Cause Delay Attribution, Descriptive Percentiles, and Formal Hypothesis Tests
        </p>
      </div>

      {/* Statistical Summary Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3 font-mono">
        <div className="bg-aviation-card p-4 rounded-xl border border-aviation-border">
          <span className="text-[10px] text-slate-400 uppercase block">Mean Delay</span>
          <span className="text-xl font-bold text-white">+{arrStats.mean}m</span>
        </div>
        <div className="bg-aviation-card p-4 rounded-xl border border-aviation-border">
          <span className="text-[10px] text-slate-400 uppercase block">Median (P50)</span>
          <span className="text-xl font-bold text-aviation-cyan">{arrStats.p50 > 0 ? `+${arrStats.p50}` : arrStats.p50}m</span>
        </div>
        <div className="bg-aviation-card p-4 rounded-xl border border-aviation-border">
          <span className="text-[10px] text-slate-400 uppercase block">75th Percentile</span>
          <span className="text-xl font-bold text-amber-400">+{arrStats.p75}m</span>
        </div>
        <div className="bg-aviation-card p-4 rounded-xl border border-aviation-border">
          <span className="text-[10px] text-slate-400 uppercase block">90th Percentile</span>
          <span className="text-xl font-bold text-red-400">+{arrStats.p90}m</span>
        </div>
        <div className="bg-aviation-card p-4 rounded-xl border border-aviation-border">
          <span className="text-[10px] text-slate-400 uppercase block">Std Deviation</span>
          <span className="text-xl font-bold text-slate-300">&plusmn;{arrStats.std}m</span>
        </div>
        <div className="bg-aviation-card p-4 rounded-xl border border-aviation-border">
          <span className="text-[10px] text-slate-400 uppercase block">IQR Range</span>
          <span className="text-xl font-bold text-slate-300">{arrStats.iqr}m</span>
        </div>
      </div>

      {/* Delay Breakdown Chart */}
      <div className="bg-aviation-card border border-aviation-border rounded-xl p-5 shadow-lg">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2 mb-4">
          <BarChart3 className="w-4 h-4 text-aviation-accent" />
          Primary Delay Minutes by Root Cause
        </h3>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={delays}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2A3B60" />
              <XAxis dataKey="primary_delay_cause" stroke="#94A3B8" fontSize={11} />
              <YAxis stroke="#94A3B8" fontSize={11} />
              <Tooltip
                contentStyle={{ backgroundColor: '#131D38', borderColor: '#2A3B60', borderRadius: '8px', fontSize: '12px' }}
                formatter={(val: any) => [`${Math.round(val).toLocaleString()} min`, 'Total Delay']}
              />
              <Bar dataKey="total_delay_minutes" name="Total Delay Minutes" fill="#0072CE" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Hypothesis Testing Results Grid */}
      <div className="bg-aviation-card border border-aviation-border rounded-xl p-5 shadow-lg">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2 mb-4">
          <Activity className="w-4 h-4 text-emerald-400" />
          Statistical Hypothesis Test Evaluations (p-value &lt; 0.05)
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {Object.entries(stats.hypothesis_tests).map(([key, test]: [string, any]) => (
            <div key={key} className="bg-aviation-navy/70 border border-aviation-border rounded-xl p-4 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-aviation-accent/20 text-aviation-cyan border border-aviation-accent/40">
                    {test.test_name}
                  </span>
                  <span className="text-xs font-mono font-bold text-emerald-400">p = {test.p_value < 1e-4 ? '< 0.0001' : test.p_value.toFixed(4)}</span>
                </div>
                <h4 className="font-bold text-white text-xs mb-2 leading-relaxed">{test.question}</h4>
                <p className="text-xs text-slate-300 leading-relaxed font-sans">{test.conclusion}</p>
              </div>

              <div className="mt-4 pt-3 border-t border-aviation-border text-[11px] font-mono text-slate-400 flex items-center justify-between">
                <span>Significant: <strong className="text-emerald-400">YES</strong></span>
                <span>Statistic: {test.t_statistic || test.f_statistic || test.chi2_statistic}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
