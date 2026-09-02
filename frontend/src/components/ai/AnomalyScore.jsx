import React from 'react';
import { formatPercentage } from '../../utils/formatters';

export const AnomalyScore = ({ score = 0.94, label = 'Anomaly Score' }) => {
  const percentage = score <= 1 ? Math.round(score * 100) : Math.round(score);
  const isHigh = percentage > 70;

  return (
    <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 font-mono">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-slate-400 uppercase tracking-wider">{label}</span>
        <span className={`text-xs font-bold ${isHigh ? 'text-red-400' : 'text-cyan-400'}`}>
          {formatPercentage(score)}
        </span>
      </div>

      <div className="w-full bg-slate-900 rounded-full h-2.5 overflow-hidden border border-slate-800">
        <div
          className={`h-full transition-all duration-700 ${
            isHigh ? 'bg-gradient-to-r from-orange-500 to-red-500' : 'bg-cyan-500'
          }`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

export default AnomalyScore;
