import React from 'react';
import { ShieldCheck } from 'lucide-react';

export const EmptyState = ({
  icon: Icon = ShieldCheck,
  title = 'No threats detected',
  description = 'Everything is secure. No anomalies or active incidents found in current scope.',
  action,
  className = '',
}) => {
  return (
    <div
      className={`p-10 rounded-xl border border-slate-800 bg-slate-900/40 flex flex-col items-center justify-center text-center gap-3 ${className}`}
    >
      <div className="p-4 rounded-full bg-slate-800/80 text-cyan-400 border border-slate-700">
        <Icon className="w-8 h-8" />
      </div>
      <h4 className="text-base font-semibold text-slate-200">{title}</h4>
      <p className="text-sm text-slate-400 max-w-md">{description}</p>
      {action && <div className="mt-2">{action}</div>}
    </div>
  );
};

export default EmptyState;
