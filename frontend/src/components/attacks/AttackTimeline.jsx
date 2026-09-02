import React from 'react';
import { Clock, CheckCircle2, XCircle, AlertTriangle, ArrowDown } from 'lucide-react';
import Badge from '../common/Badge';

export const AttackTimeline = ({ timeline = [] }) => {
  if (!timeline || timeline.length === 0) {
    return (
      <div className="p-6 text-center text-xs font-mono text-slate-500">
        No attack reconstruction events available
      </div>
    );
  }

  const getStatusBadge = (status) => {
    switch (status?.toLowerCase()) {
      case 'failed':
        return <Badge severity="MEDIUM" size="sm">Failed</Badge>;
      case 'success':
      case 'allowed':
        return <Badge severity="LOW" size="sm">Success</Badge>;
      case 'suspicious':
        return <Badge severity="HIGH" size="sm">Suspicious</Badge>;
      case 'targeted':
      case 'blocked':
        return <Badge severity="CRITICAL" size="sm">{status}</Badge>;
      default:
        return <Badge severity="INFO" size="sm">{status}</Badge>;
    }
  };

  return (
    <div className="space-y-4 font-mono">
      {timeline.map((step, idx) => (
        <div key={idx} className="relative">
          <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 hover:border-red-500/40 transition-colors">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-slate-800 text-cyan-400 font-bold text-xs flex items-center justify-center">
                  {idx + 1}
                </span>
                <span className="text-xs font-bold text-slate-100">{step.event}</span>
              </div>
              <div className="flex items-center gap-2">
                {getStatusBadge(step.status)}
                <span className="text-xs text-slate-400 flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {step.time}
                </span>
              </div>
            </div>

            {step.desc && (
              <p className="mt-2 text-xs text-slate-400 font-sans pl-7 leading-relaxed">
                {step.desc}
              </p>
            )}
          </div>

          {idx < timeline.length - 1 && (
            <div className="flex justify-center my-1.5">
              <ArrowDown className="w-4 h-4 text-slate-600 animate-bounce" />
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default AttackTimeline;
