import React from 'react';
import { ShieldAlert, AlertTriangle, ShieldCheck } from 'lucide-react';
import { formatRiskScore } from '../../utils/formatters';

export const RiskScore = ({ score = 88, max = 100, label = 'Risk Score' }) => {
  const percentage = Math.min(Math.max((score / max) * 100, 0), 100);

  const getRiskColor = (val) => {
    if (val >= 80) return { bar: 'bg-red-500', text: 'text-red-400', level: 'CRITICAL' };
    if (val >= 60) return { bar: 'bg-orange-500', text: 'text-orange-400', level: 'HIGH' };
    if (val >= 40) return { bar: 'bg-yellow-500', text: 'text-yellow-400', level: 'MEDIUM' };
    return { bar: 'bg-emerald-500', text: 'text-emerald-400', level: 'LOW' };
  };

  const riskInfo = getRiskColor(percentage);

  return (
    <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 font-mono">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-slate-400 uppercase tracking-wider">{label}</span>
        <span className={`text-xs font-bold ${riskInfo.text}`}>{riskInfo.level} SEVERITY</span>
      </div>

      {/* Progress / Gauge Bar */}
      <div className="w-full bg-slate-900 rounded-full h-3 overflow-hidden border border-slate-800/80 mb-2">
        <div
          className={`h-full ${riskInfo.bar} transition-all duration-700 shadow-lg shadow-red-500/20`}
          style={{ width: `${percentage}%` }}
        />
      </div>

      <div className="flex items-center justify-between text-xs">
        <span className="text-xl font-bold text-slate-100">{score} <span className="text-xs text-slate-500">/ {max}</span></span>
        <span className="text-[11px] text-slate-500 font-sans">Calculated by Member 5 (Attack Engine)</span>
      </div>
    </div>
  );
};

export default RiskScore;
