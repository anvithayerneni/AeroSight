import React from 'react';
import { Activity, ShieldCheck, Clock, RefreshCw } from 'lucide-react';

interface NavbarProps {
  onRefresh?: () => void;
  isRefreshing?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ onRefresh, isRefreshing }) => {
  const [currentTime, setCurrentTime] = React.useState(new Date().toUTCString());

  React.useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date().toUTCString().replace('GMT', 'UTC'));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="h-16 bg-aviation-navy border-b border-aviation-border px-6 flex items-center justify-between shrink-0">
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-950/60 border border-emerald-800/50 text-emerald-400 text-xs font-mono">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          <span>NETWORK ONLINE</span>
        </div>

        <div className="hidden md:flex items-center space-x-2 text-xs text-slate-400">
          <ShieldCheck className="w-3.5 h-3.5 text-aviation-cyan" />
          <span>Data Quality Score: <strong className="text-white font-mono">100.0%</strong></span>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        {/* UTC Operational Clock */}
        <div className="flex items-center space-x-2 text-xs text-slate-300 font-mono bg-aviation-dark/80 px-3 py-1.5 rounded-lg border border-aviation-border">
          <Clock className="w-3.5 h-3.5 text-aviation-cyan" />
          <span>{currentTime}</span>
        </div>

        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="p-2 rounded-lg bg-aviation-card hover:bg-aviation-cardHover text-slate-300 border border-aviation-border transition-colors disabled:opacity-50"
            title="Refresh Lakehouse & KPI Data"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-aviation-accent' : ''}`} />
          </button>
        )}
      </div>
    </header>
  );
};
