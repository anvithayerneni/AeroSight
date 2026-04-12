import React, { useState, useEffect } from 'react';
import { FileSpreadsheet, Download, Database, Play, CheckCircle2, AlertCircle } from 'lucide-react';
import { fetchReports, executeCustomSQL } from '../services/api';
import { ReportItem } from '../services/types';

export const ReportsPage: React.FC = () => {
  const [reports, setReports] = useState<ReportItem[]>([]);
  const [sqlQuery, setSqlQuery] = useState(
    "SELECT carrier_key, COUNT(flight_id) as total_flights, ROUND(AVG(dep_delay), 2) as avg_dep_delay FROM fact_flights GROUP BY carrier_key ORDER BY total_flights DESC LIMIT 10;"
  );
  const [queryResults, setQueryResults] = useState<{ query: string; row_count: number; rows: any[] } | null>(null);
  const [executing, setExecuting] = useState(false);
  const [sqlError, setSqlError] = useState<string | null>(null);

  useEffect(() => {
    fetchReports().then(setReports).catch(console.error);
  }, []);

  const handleRunSQL = async () => {
    setExecuting(true);
    setSqlError(null);
    try {
      const res = await executeCustomSQL(sqlQuery);
      setQueryResults(res);
    } catch (err: any) {
      setSqlError(err.message || 'Query error');
      setQueryResults(null);
    } finally {
      setExecuting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-black text-white tracking-tight">Executive Excel Reports & SQL Studio</h2>
        <p className="text-xs text-slate-400 mt-1">
          Automated openpyxl Formatted Business Workbooks, CSV Exports, and Direct Lakehouse SQL Explorer
        </p>
      </div>

      {/* Available Reports Section */}
      <div className="bg-aviation-card border border-aviation-border rounded-xl p-5 shadow-lg">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2 mb-4">
          <FileSpreadsheet className="w-4 h-4 text-emerald-400" />
          Pre-Compiled Executive Business Workbooks
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {reports.filter(r => r.filename.endsWith('.xlsx') || r.filename.endsWith('.csv')).map((rep) => (
            <div
              key={rep.filename}
              className="bg-aviation-navy/70 border border-aviation-border rounded-xl p-4 flex flex-col justify-between hover:border-aviation-accent/50 transition-colors"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold ${rep.filename.endsWith('.xlsx') ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-aviation-slate/30 text-aviation-cyan border border-aviation-border'}`}>
                    {rep.file_type}
                  </span>
                  <span className="text-[11px] font-mono text-slate-400">{rep.size_kb} KB</span>
                </div>
                <h4 className="font-bold text-white text-xs mb-1 truncate">{rep.filename}</h4>
                <p className="text-[11px] text-slate-400">
                  {rep.filename.includes('monthly') ? 'Monthly Operations & Delay Summary' : (rep.filename.includes('airport') ? 'Hub Traffic & Runway Congestion' : 'Airline Carrier Reliability & Root Cause')}
                </p>
              </div>

              <div className="mt-4 pt-3 border-t border-aviation-border">
                <a
                  href={rep.download_url}
                  download
                  className="w-full py-2 rounded-lg bg-aviation-navy hover:bg-aviation-accent text-slate-200 hover:text-white text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors border border-aviation-border"
                >
                  <Download className="w-3.5 h-3.5" />
                  Download {rep.filename.endsWith('.xlsx') ? 'Excel (.xlsx)' : 'CSV'}
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Interactive SQL Studio */}
      <div className="bg-aviation-card border border-aviation-border rounded-xl p-5 shadow-lg">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Database className="w-4 h-4 text-aviation-cyan" />
              Live Lakehouse SQL Studio (DuckDB / PostgreSQL)
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Execute read-only SQL queries against Star Schema fact and dimension tables
            </p>
          </div>
          <button
            onClick={handleRunSQL}
            disabled={executing}
            className="px-4 py-2 rounded-lg bg-aviation-accent hover:bg-aviation-accent/80 text-white font-semibold text-xs flex items-center gap-1.5 transition-colors disabled:opacity-50"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            {executing ? 'Running...' : 'Execute SQL'}
          </button>
        </div>

        <textarea
          rows={3}
          value={sqlQuery}
          onChange={(e) => setSqlQuery(e.target.value)}
          className="w-full bg-aviation-dark border border-aviation-border rounded-xl p-3 text-xs font-mono text-slate-200 focus:outline-none focus:border-aviation-accent resize-y"
        />

        {sqlError && (
          <div className="mt-3 p-3 rounded-lg bg-red-950/80 border border-red-800 text-xs text-red-300 flex items-center gap-2 font-mono">
            <AlertCircle className="w-4 h-4 shrink-0 text-red-400" />
            <span>{sqlError}</span>
          </div>
        )}

        {queryResults && (
          <div className="mt-4 border border-aviation-border rounded-xl overflow-hidden">
            <div className="bg-aviation-navy px-4 py-2 text-xs font-mono text-slate-400 flex items-center justify-between border-b border-aviation-border">
              <span>Returned {queryResults.row_count} rows</span>
              <span className="text-emerald-400 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> Executed successfully
              </span>
            </div>

            <div className="max-h-72 overflow-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-aviation-dark text-slate-400 uppercase tracking-wider text-[10px] border-b border-aviation-border">
                  <tr>
                    {queryResults.rows.length > 0 &&
                      Object.keys(queryResults.rows[0]).map((col) => (
                        <th key={col} className="py-2.5 px-4">{col}</th>
                      ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-aviation-border">
                  {queryResults.rows.map((row, idx) => (
                    <tr key={idx} className="hover:bg-aviation-navy/40">
                      {Object.values(row).map((val: any, cIdx) => (
                        <td key={cIdx} className="py-2 px-4 text-slate-200">
                          {val !== null && val !== undefined ? String(val) : 'NULL'}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
