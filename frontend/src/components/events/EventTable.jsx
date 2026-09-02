import React from 'react';
import { ArrowRight, CheckCircle2, XCircle, AlertTriangle, ShieldCheck } from 'lucide-react';
import Badge from '../common/Badge';

export const EventTable = ({
  events = [],
  selectedEventId,
  onSelectEvent,
}) => {
  const getStatusBadge = (status) => {
    switch (status?.toLowerCase()) {
      case 'allowed':
      case 'success':
        return <span className="px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-500/40 text-[11px] font-bold">Allowed</span>;
      case 'failed':
        return <span className="px-2 py-0.5 rounded bg-red-950/80 text-red-400 border border-red-500/40 text-[11px] font-bold">Failed</span>;
      case 'blocked':
        return <span className="px-2 py-0.5 rounded bg-rose-950/80 text-rose-300 border border-rose-500/40 text-[11px] font-bold">Blocked</span>;
      case 'suspicious':
        return <span className="px-2 py-0.5 rounded bg-amber-950/80 text-amber-400 border border-amber-500/40 text-[11px] font-bold">Suspicious</span>;
      default:
        return <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[11px] font-bold">{status}</span>;
    }
  };

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-900/60 font-mono text-xs shadow-xl">
      <table className="w-full text-left">
        <thead className="bg-slate-950/90 text-slate-400 text-[11px] uppercase border-b border-slate-800">
          <tr>
            <th className="px-4 py-3.5">Time</th>
            <th className="px-4 py-3.5">Event ID</th>
            <th className="px-4 py-3.5">Source</th>
            <th className="px-4 py-3.5">Destination</th>
            <th className="px-4 py-3.5">Event Type</th>
            <th className="px-4 py-3.5">Status</th>
            <th className="px-4 py-3.5">PoA Ledger</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/60">
          {events.map((evt) => {
            const isSelected = selectedEventId === evt.id;
            return (
              <tr
                key={evt.id}
                onClick={() => onSelectEvent?.(evt)}
                className={`hover:bg-slate-800/60 cursor-pointer transition-colors ${
                  isSelected ? 'bg-cyan-950/40 border-l-2 border-cyan-400' : ''
                }`}
              >
                <td className="px-4 py-3 text-slate-400">{evt.time}</td>
                <td className="px-4 py-3 font-bold text-cyan-400">{evt.id}</td>
                <td className="px-4 py-3 text-slate-200">
                  <span>{evt.source}</span>
                  {evt.sourceIp && <span className="text-[10px] text-slate-500 block">{evt.sourceIp}</span>}
                </td>
                <td className="px-4 py-3 text-slate-200">
                  <span>{evt.destination}</span>
                  {evt.destIp && <span className="text-[10px] text-slate-500 block">{evt.destIp}</span>}
                </td>
                <td className="px-4 py-3 font-bold text-slate-300">{evt.event}</td>
                <td className="px-4 py-3">{getStatusBadge(evt.status)}</td>
                <td className="px-4 py-3">
                  <span className="inline-flex items-center gap-1 text-[11px] text-emerald-400">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Verified</span>
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default EventTable;
