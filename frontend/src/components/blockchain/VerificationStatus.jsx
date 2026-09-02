import React from 'react';
import { CheckCircle, AlertTriangle, HelpCircle, ShieldCheck } from 'lucide-react';
import IntegrityBadge from './IntegrityBadge';
import { truncateHash } from '../../utils/formatters';
import { formatDateTime } from '../../utils/dateUtils';

export const VerificationStatus = ({
  eventId = 'EVT-1001',
  verified = true,
  transactionHash = '0xabc123789fed456123456789abcdef0123456789abcdef0123456789abcdef01',
  timestamp,
  blockNumber = 1849201,
}) => {
  return (
    <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/90 font-mono shadow-xl text-xs space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <h4 className="font-bold text-slate-100 text-sm">Blockchain Verification</h4>
        </div>
        <IntegrityBadge status={verified ? 'VERIFIED' : 'NOT_VERIFIED'} size="sm" />
      </div>

      <div className="space-y-2.5">
        <div className="flex justify-between py-1 border-b border-slate-800/60">
          <span className="text-slate-400">Target Event ID:</span>
          <span className="text-cyan-400 font-bold">{eventId}</span>
        </div>

        <div className="flex justify-between py-1 border-b border-slate-800/60">
          <span className="text-slate-400">Block Number:</span>
          <span className="text-slate-200 font-bold">#{blockNumber}</span>
        </div>

        <div className="flex justify-between py-1 border-b border-slate-800/60">
          <span className="text-slate-400">On-Chain Time:</span>
          <span className="text-slate-300">{formatDateTime(timestamp)}</span>
        </div>

        <div className="pt-2">
          <span className="text-slate-400 block mb-1">Transaction Proof Hash:</span>
          <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800/80 text-[11px] text-emerald-300 break-all select-all font-mono">
            {transactionHash || '0xabc123...'}
          </div>
        </div>
      </div>
    </div>
  );
};

export default VerificationStatus;
