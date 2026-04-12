import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  unit?: string;
  change?: string;
  isPositive?: boolean;
  icon: LucideIcon;
  subtitle?: string;
  badge?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  unit,
  change,
  isPositive,
  icon: Icon,
  subtitle,
  badge
}) => {
  return (
    <div className="bg-aviation-card hover:bg-aviation-cardHover transition-all duration-200 border border-aviation-border rounded-xl p-5 shadow-lg relative overflow-hidden group">
      <div className="absolute top-0 right-0 w-24 h-24 bg-aviation-accent/5 rounded-full -mr-8 -mt-8 pointer-events-none group-hover:scale-110 transition-transform duration-300" />
      
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          {title}
        </span>
        <div className="p-2 rounded-lg bg-aviation-navy border border-aviation-border text-aviation-cyan">
          <Icon className="w-5 h-5" />
        </div>
      </div>

      <div className="flex items-baseline space-x-2">
        <span className="text-2xl lg:text-3xl font-bold tracking-tight text-white font-mono">
          {value}
        </span>
        {unit && <span className="text-sm font-medium text-slate-400">{unit}</span>}
      </div>

      {(subtitle || change || badge) && (
        <div className="mt-3 flex items-center justify-between text-xs">
          {subtitle && <span className="text-slate-400">{subtitle}</span>}
          {change && (
            <span className={`font-semibold ${isPositive ? 'text-emerald-400' : 'text-amber-400'}`}>
              {change}
            </span>
          )}
          {badge && (
            <span className="px-2 py-0.5 rounded bg-aviation-slate/40 text-aviation-cyan font-mono text-[10px] border border-aviation-border">
              {badge}
            </span>
          )}
        </div>
      )}
    </div>
  );
};
