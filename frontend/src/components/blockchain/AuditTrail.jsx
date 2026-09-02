import React from 'react';
import { ArrowRight, CheckCircle2, Shield, Search } from 'lucide-react';
import IntegrityBadge from './IntegrityBadge';
import { truncateHash } from '../../utils/formatters';
import { formatDateTime } from '../../utils/dateUtils';

export const AuditTrail = ({
  auditRecords = [],
  onSelectRecord,
  selectedRecordId,
}) => {
  return (
    <div className="space-y-3 font-mono text-xs">
      {/* Flow Explanation Banner */}
      <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 flex flex-wrap items-center justify-between gap-2 text-[11px] text-slate-400">
        <div className="flex items-center gap-2">
          <Shield className="w-4 h-4 text-emerald-400" />
          <span className="font-bold text-slate-200">Zero-Trust Immutability Pipeline:</span>
        </div>
        <div className="flex items-center gap-2 text-cyan-400">
          <span>Security Event</span>
          <ArrowRight className="w-3 h-3 text-slate-600" />
          <span>SHA-256 Hash</span>
          <ArrowRight className="w-3 h-3 text-slate-600" />
          <span>On-Chain PoA</span>
          <ArrowRight className="w-3 h-3 text-slate-600" />
          <span className="text-emerald-400 font-bold">Tamper Proof</span>
        </div>
      </div>

      {/* List / Table of Records */}
      <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-900/60">
        <table className="w-full text-left">
          <thead className="bg-slate-950/90 text-slate-400 text-[11px] uppercase border-b border-slate-800">
            <tr>
              <th className="px-4 py-3">Event ID</th>
              <th className="px-4 py-3">Raw Event Hash</th>
              <th className="px-4 py-3">Transaction Proof</th>
              <th className="px-4 py-3">Block #</th>
              <th className="px-4 py-3">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {auditRecords.map((rec) => {
              const isSelected = selectedRecordId === rec.eventId;
              return (
                <tr
                  key={rec.eventId}
                  onClick={() => onSelectRecord?.(rec)}
                  className={`hover:bg-slate-800/50 cursor-pointer transition-colors ${
                    isSelected ? 'bg-cyan-950/40 border-l-2 border-cyan-400' : ''
                  }`}
                >
                  <td className="px-4 py-3 font-bold text-cyan-400">{rec.eventId}</td>
                  <td className="px-4 py-3 text-slate-400 font-mono" title={rec.hash}>
                    {truncateHash(rec.hash, 8, 6)}
                  </td>
                  <td className="px-4 py-3 text-emerald-400 font-mono" title={rec.txHash}>
                    {truncateHash(rec.txHash, 10, 6)}
                  </td>
                  <td className="px-4 py-3 text-slate-300">#{rec.blockNumber}</td>
                  <td className="px-4 py-3">
                    <IntegrityBadge status={rec.status} size="sm" />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AuditTrail;
