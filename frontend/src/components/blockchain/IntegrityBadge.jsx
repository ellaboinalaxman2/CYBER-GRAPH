import React from 'react';
import { CheckCircle2, AlertTriangle, HelpCircle } from 'lucide-react';

export const IntegrityBadge = ({ status = 'VERIFIED', size = 'md' }) => {
  const normalized = status?.toUpperCase() || 'NOT_VERIFIED';

  const sizeClasses = {
    sm: 'text-[10px] px-2 py-0.5',
    md: 'text-xs px-2.5 py-1',
    lg: 'text-sm px-3.5 py-1.5',
  };

  if (normalized === 'VERIFIED') {
    return (
      <span className={`inline-flex items-center gap-1.5 rounded-full font-mono font-bold uppercase bg-emerald-950/80 text-emerald-400 border border-emerald-500/50 ${sizeClasses[size]}`}>
        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
        <span>✓ Integrity Verified</span>
      </span>
    );
  }

  if (normalized === 'FAILED' || normalized === 'VERIFICATION_FAILED') {
    return (
      <span className={`inline-flex items-center gap-1.5 rounded-full font-mono font-bold uppercase bg-red-950/80 text-red-400 border border-red-500/50 ${sizeClasses[size]}`}>
        <AlertTriangle className="w-3.5 h-3.5 text-red-400" />
        <span>⚠ Verification Failed</span>
      </span>
    );
  }

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full font-mono font-bold uppercase bg-slate-800 text-slate-400 border border-slate-700 ${sizeClasses[size]}`}>
      <HelpCircle className="w-3.5 h-3.5 text-slate-400" />
      <span>? Not Verified</span>
    </span>
  );
};

export default IntegrityBadge;
