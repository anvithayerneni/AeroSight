import React from 'react';

interface StatusBadgeProps {
  status: string;
  delayMinutes?: number;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, delayMinutes }) => {
  const normalized = status.toUpperCase();

  if (normalized === 'CANCELLED' || normalized === 'CANCELED') {
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-red-950/80 text-red-400 border border-red-800/60">
        CANCELLED
      </span>
    );
  }

  if (normalized === 'DIVERTED') {
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-purple-950/80 text-purple-400 border border-purple-800/60">
        DIVERTED
      </span>
    );
  }

  if (normalized === 'DELAYED' || (delayMinutes !== undefined && delayMinutes >= 15)) {
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-amber-950/80 text-amber-400 border border-amber-800/60">
        DELAYED {delayMinutes !== undefined ? `(+${Math.round(delayMinutes)}m)` : ''}
      </span>
    );
  }

  return (
    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-emerald-950/80 text-emerald-400 border border-emerald-800/60">
      ON-TIME
    </span>
  );
};
