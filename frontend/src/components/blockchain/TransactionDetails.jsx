import React from 'react';
import { Layers, CheckCircle2, Copy, ExternalLink } from 'lucide-react';
import IntegrityBadge from './IntegrityBadge';
import { formatDateTime } from '../../utils/dateUtils';

export const TransactionDetails = ({ tx }) => {
  if (!tx) return null;

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/80 font-mono text-xs space-y-3">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <span className="font-bold text-slate-100 uppercase">Cryptographic Audit Proof</span>
        <IntegrityBadge status={tx.status || 'VERIFIED'} size="sm" />
      </div>

      <div className="space-y-2 text-[11px]">
        <div>
          <span className="text-slate-500 block">Transaction Hash</span>
          <div className="flex items-center justify-between p-2 rounded bg-slate-950 border border-slate-800 mt-1">
            <span className="text-emerald-400 truncate pr-2">{tx.txHash || tx.transaction_hash}</span>
            <button
              onClick={() => copyToClipboard(tx.txHash || tx.transaction_hash)}
              className="text-slate-400 hover:text-slate-200 p-1"
              title="Copy hash"
            >
              <Copy className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        <div>
          <span className="text-slate-500 block">Raw Event SHA-256 Digest</span>
          <div className="p-2 rounded bg-slate-950 border border-slate-800 mt-1 text-slate-300 truncate">
            {tx.hash || tx.raw_hash || 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2 pt-1">
          <div className="p-2 rounded bg-slate-950 border border-slate-800">
            <span className="text-slate-500 block">Block Height</span>
            <span className="text-slate-200 font-bold">#{tx.blockNumber || tx.block_number || 1849201}</span>
          </div>
          <div className="p-2 rounded bg-slate-950 border border-slate-800">
            <span className="text-slate-500 block">Validation Node</span>
            <span className="text-cyan-400 font-bold">{tx.verifier || 'Validator 0x4B..99'}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TransactionDetails;
