import React from 'react';
import { TrendingUp, TrendingDown, ArrowUpRight } from 'lucide-react';

export const StatsCard = ({
  title,
  value,
  change,
  isPositive,
  icon: Icon,
  variant = 'default',
  subtitle,
  onClick,
}) => {
  const variantStyles = {
    default: 'border-slate-800 hover:border-slate-700 bg-slate-900/60',
    cyan: 'border-cyan-500/30 hover:border-cyan-400 bg-cyan-950/20 shadow-lg shadow-cyan-950/20',
    critical: 'border-red-500/30 hover:border-red-400 bg-red-950/20 shadow-lg shadow-red-950/20',
    warning: 'border-orange-500/30 hover:border-orange-400 bg-orange-950/20',
    emerald: 'border-emerald-500/30 hover:border-emerald-400 bg-emerald-950/20',
  };

  const iconColors = {
    default: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20',
    cyan: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/30',
    critical: 'text-red-400 bg-red-500/10 border-red-500/30 animate-pulse',
    warning: 'text-orange-400 bg-orange-500/10 border-orange-500/30',
    emerald: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
  };

  return (
    <div
      onClick={onClick}
      className={`p-5 rounded-xl border backdrop-blur-sm transition-all duration-200 ${variantStyles[variant]} ${
        onClick ? 'cursor-pointer hover:-translate-y-0.5' : ''
      }`}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">{title}</span>
        {Icon && (
          <div className={`p-2.5 rounded-lg border ${iconColors[variant]}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>

      <div className="mt-4 flex items-baseline justify-between">
        <span className="text-3xl font-bold font-mono tracking-tight text-slate-100">{value}</span>
        {change && (
          <span
            className={`inline-flex items-center text-xs font-mono font-medium ${
              isPositive ? 'text-emerald-400' : 'text-red-400'
            }`}
          >
            {isPositive ? <TrendingUp className="w-3.5 h-3.5 mr-1" /> : <TrendingDown className="w-3.5 h-3.5 mr-1" />}
            {change}
          </span>
        )}
      </div>

      {subtitle && <p className="mt-2 text-xs text-slate-400 font-mono">{subtitle}</p>}
    </div>
  );
};

export default StatsCard;
