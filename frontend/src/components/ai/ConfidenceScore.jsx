import React from 'react';
import { formatPercentage } from '../../utils/formatters';

export const ConfidenceScore = ({ confidence = 0.93, label = 'Confidence' }) => {
  const percentage = confidence <= 1 ? Math.round(confidence * 100) : Math.round(confidence);

  return (
    <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 font-mono">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-slate-400 uppercase tracking-wider">{label}</span>
        <span className="text-xs font-bold text-indigo-400">{formatPercentage(confidence)}</span>
      </div>

      <div className="w-full bg-slate-900 rounded-full h-2.5 overflow-hidden border border-slate-800">
        <div
          className="h-full bg-gradient-to-r from-indigo-500 to-cyan-500 transition-all duration-700"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

export default ConfidenceScore;
