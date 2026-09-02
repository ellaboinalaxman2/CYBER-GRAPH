import React from 'react';
import { getSeverityConfig } from '../../utils/severityUtils';

export const Badge = ({
  children,
  variant = 'default',
  severity,
  size = 'md',
  dot = false,
  className = '',
}) => {
  const sizeClasses = {
    sm: 'text-[10px] px-2 py-0.5 font-mono',
    md: 'text-xs px-2.5 py-1 font-mono',
    lg: 'text-sm px-3.5 py-1.5 font-mono',
  };

  let colorClasses = 'bg-slate-800 text-slate-300 border border-slate-700';

  if (severity) {
    const config = getSeverityConfig(severity);
    colorClasses = config.badgeClass;
  } else if (variant === 'cyber') {
    colorClasses = 'bg-cyan-950/80 text-cyan-400 border border-cyan-500/50 shadow-sm shadow-cyan-500/20';
  } else if (variant === 'success') {
    colorClasses = 'bg-emerald-950/80 text-emerald-400 border border-emerald-500/50';
  } else if (variant === 'warning') {
    colorClasses = 'bg-amber-950/80 text-amber-400 border border-amber-500/50';
  } else if (variant === 'danger') {
    colorClasses = 'bg-red-950/80 text-red-400 border border-red-500/50';
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full font-semibold uppercase tracking-wider ${sizeClasses[size]} ${colorClasses} ${className}`}
    >
      {dot && <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />}
      {children}
    </span>
  );
};

export default Badge;
