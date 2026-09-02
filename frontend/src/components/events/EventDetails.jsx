import React from 'react';
import { useNavigate } from 'react-router-dom';
import { X, ShieldCheck, Activity, Copy, CheckCircle2 } from 'lucide-react';
import Badge from '../common/Badge';
import { truncateHash } from '../../utils/formatters';

export const EventDetails = ({ event, onClose }) => {
  const navigate = useNavigate();

  if (!event) return null;

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/95 backdrop-blur-md font-mono text-xs space-y-4 shadow-2xl">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-cyan-400" />
          <h4 className="font-bold text-slate-100 text-sm">{event.id} Telemetry Details</h4>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      <div className="space-y-2.5">
        <div className="flex justify-between py-1 border-b border-slate-800/60">
          <span className="text-slate-400">Time:</span>
          <span className="text-slate-200">{event.time}</span>
        </div>

        <div className="flex justify-between py-1 border-b border-slate-800/60">
          <span className="text-slate-400">Source:</span>
          <span className="text-cyan-400 font-bold">{event.source} ({event.sourceIp})</span>
        </div>

        <div className="flex justify-between py-1 border-b border-slate-800/60">
          <span className="text-slate-400">Destination:</span>
          <span className="text-red-400 font-bold">{event.destination} ({event.destIp})</span>
        </div>

        <div className="flex justify-between py-1 border-b border-slate-800/60">
          <span className="text-slate-400">Protocol:</span>
          <span className="text-slate-200 font-bold">{event.protocol || 'TCP/22'}</span>
        </div>

        <div className="pt-2">
          <span className="text-slate-400 block mb-1">SHA-256 Digest:</span>
          <div className="flex items-center justify-between p-2 rounded bg-slate-950 border border-slate-800 text-[11px] text-slate-300">
            <span className="truncate pr-2">{event.rawHash || 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'}</span>
            <button onClick={() => copyToClipboard(event.rawHash)} className="text-slate-400 hover:text-slate-200">
              <Copy className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        <div className="p-3 rounded-xl bg-emerald-950/20 border border-emerald-500/30 flex items-center justify-between">
          <div className="flex items-center gap-2 text-emerald-400">
            <CheckCircle2 className="w-4 h-4" />
            <span className="font-bold text-xs">PoA Blockchain Verified</span>
          </div>
          <button
            onClick={() => navigate('/blockchain')}
            className="text-[11px] text-cyan-400 hover:underline"
          >
            Audit Trail &rarr;
          </button>
        </div>
      </div>
    </div>
  );
};

export default EventDetails;
