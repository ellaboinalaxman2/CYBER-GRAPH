import React from 'react';
import { Clock, Target, ArrowRight, ShieldAlert, Cpu } from 'lucide-react';
import Badge from '../common/Badge';
import { formatTimestamp } from '../../utils/dateUtils';
import { formatPercentage } from '../../utils/formatters';

export const AlertCard = ({
  alert,
  onSelect,
  isSelected = false,
  onStatusChange,
}) => {
  const isCritical = alert.severity === 'CRITICAL';

  return (
    <div
      onClick={() => onSelect?.(alert)}
      className={`p-5 rounded-xl border transition-all duration-200 cursor-pointer ${
        isSelected
          ? 'bg-cyan-950/40 border-cyan-400 ring-1 ring-cyan-400 shadow-xl'
          : isCritical
          ? 'bg-red-950/20 border-red-500/30 hover:border-red-400'
          : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2">
          <Badge severity={alert.severity} dot>
            {alert.severity}
          </Badge>
          <span className="text-xs font-mono text-slate-400">{alert.id}</span>
        </div>
        <span className="text-[11px] font-mono text-slate-400 flex items-center gap-1">
          <Clock className="w-3 h-3" />
          {formatTimestamp(alert.timestamp)}
        </span>
      </div>

      <h4 className="text-sm font-semibold text-slate-100 mt-2.5 line-clamp-1">
        {alert.title}
      </h4>

      <p className="text-xs text-slate-400 mt-1 line-clamp-2 font-sans">
        {alert.description}
      </p>

      <div className="mt-4 pt-3 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-2 text-xs font-mono">
        <div className="flex items-center gap-1.5 text-slate-300">
          <span className="text-slate-400">Path:</span>
          <span className="text-cyan-400 font-bold">{alert.source}</span>
          <ArrowRight className="w-3 h-3 text-slate-400" />
          <span className="text-red-400 font-bold">{alert.destination}</span>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 text-slate-400">
            <Cpu className="w-3.5 h-3.5 text-indigo-400" />
            <span>AI Conf:</span>
            <span className="text-slate-200 font-bold">{formatPercentage(alert.confidence)}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AlertCard;
