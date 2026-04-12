import React from 'react';
import {
  LayoutDashboard,
  Plane,
  Building2,
  Route,
  ClockAlert,
  Radio,
  Cpu,
  FileSpreadsheet,
  Layers,
  Database
} from 'lucide-react';

export type PageId =
  | 'dashboard'
  | 'flights'
  | 'airports'
  | 'routes'
  | 'delays'
  | 'realtime'
  | 'ml'
  | 'reports';

interface SidebarProps {
  activePage: PageId;
  onSelectPage: (page: PageId) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activePage, onSelectPage }) => {
  const menuItems: { id: PageId; label: string; icon: any; badge?: string }[] = [
    { id: 'dashboard', label: 'Executive Dashboard', icon: LayoutDashboard },
    { id: 'flights', label: 'Flight Operations', icon: Plane },
    { id: 'airports', label: 'Airport Congestion', icon: Building2 },
    { id: 'routes', label: 'Route Network', icon: Route },
    { id: 'delays', label: 'Delay Root Cause', icon: ClockAlert },
    { id: 'realtime', label: 'Live Operations Radar', icon: Radio, badge: 'LIVE' },
    { id: 'ml', label: 'AI & ML Intelligence', icon: Cpu, badge: 'ML' },
    { id: 'reports', label: 'Reports & SQL Studio', icon: FileSpreadsheet },
  ];

  return (
    <aside className="w-64 bg-aviation-navy border-r border-aviation-border flex flex-col justify-between shrink-0 min-h-screen">
      <div>
        {/* Brand Header */}
        <div className="h-16 flex items-center px-6 border-b border-aviation-border space-x-3">
          <div className="p-2 rounded-lg bg-aviation-accent text-white shadow-md shadow-aviation-accent/30">
            <Plane className="w-5 h-5 transform -rotate-45" />
          </div>
          <div>
            <h1 className="font-extrabold tracking-wider text-white text-lg flex items-center gap-1.5">
              AEROSIGHT
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            </h1>
            <p className="text-[10px] uppercase tracking-widest text-slate-400 font-semibold">
              Airline Ops Platform
            </p>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="p-4 space-y-1.5">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activePage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectPage(item.id)}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-aviation-accent text-white shadow-md shadow-aviation-accent/20'
                    : 'text-slate-300 hover:bg-aviation-card hover:text-white'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span
                    className={`text-[10px] font-mono px-1.5 py-0.5 rounded font-bold ${
                      item.badge === 'LIVE'
                        ? 'bg-red-500/20 text-red-400 border border-red-500/40 animate-pulse'
                        : 'bg-aviation-cyan/20 text-aviation-cyan border border-aviation-cyan/40'
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Platform Architecture Status Badge */}
      <div className="p-4 border-t border-aviation-border bg-aviation-dark/40 m-3 rounded-xl">
        <div className="flex items-center justify-between text-xs mb-2">
          <span className="text-slate-400 font-medium flex items-center gap-1.5">
            <Database className="w-3.5 h-3.5 text-aviation-cyan" />
            Lakehouse Engine
          </span>
          <span className="text-emerald-400 font-mono text-[11px]">Ready</span>
        </div>
        <div className="flex items-center space-x-1.5 text-[10px] text-slate-400 font-mono">
          <span className="px-1.5 py-0.5 rounded bg-aviation-navy border border-aviation-border">Delta</span>
          <span className="px-1.5 py-0.5 rounded bg-aviation-navy border border-aviation-border">Spark</span>
          <span className="px-1.5 py-0.5 rounded bg-aviation-navy border border-aviation-border">DuckDB</span>
        </div>
      </div>
    </aside>
  );
};
