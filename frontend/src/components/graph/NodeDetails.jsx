import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  X,
  Server,
  Activity,
  AlertTriangle,
  Cpu,
  ArrowRight,
  ShieldCheck,
  ExternalLink,
} from 'lucide-react';
import Badge from '../common/Badge';
import { formatPercentage } from '../../utils/formatters';

export const NodeDetails = ({ node, onClose }) => {
  const navigate = useNavigate();

  if (!node) return null;

  const isHighRisk = node.anomaly_score > 0.7 || node.risk === 'CRITICAL' || node.risk === 'HIGH';

  return (
    <div className="bg-slate-900/95 border border-slate-800 rounded-xl p-5 shadow-2xl backdrop-blur-md w-80 sm:w-96 text-xs font-mono animate-in fade-in slide-in-from-right-4">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className={`p-1.5 rounded-lg ${isHighRisk ? 'bg-red-500/20 text-red-400' : 'bg-cyan-500/20 text-cyan-400'}`}>
            <Server className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100">{node.label || node.id}</h3>
            <span className="text-[10px] text-slate-400 uppercase tracking-widest">{node.type}</span>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Node Metrics Grid */}
      <div className="mt-4 space-y-2.5">
        <div className="flex justify-between py-1.5 border-b border-slate-800/60">
          <span className="text-slate-400">IP Address:</span>
          <span className="text-slate-200 font-semibold">{node.ip || '192.168.1.20'}</span>
        </div>

        <div className="flex justify-between py-1.5 border-b border-slate-800/60">
          <span className="text-slate-400">Security Status:</span>
          <Badge severity={node.risk || 'LOW'} size="sm">
            {node.status || 'Normal'}
          </Badge>
        </div>

        <div className="flex justify-between py-1.5 border-b border-slate-800/60">
          <span className="text-slate-400">Active Connections:</span>
          <span className="text-slate-200 font-bold">{node.connections || 0}</span>
        </div>

        <div className="flex justify-between py-1.5 border-b border-slate-800/60">
          <span className="text-slate-400">Triggered Alerts:</span>
          <span className={`font-bold ${node.alerts > 0 ? 'text-red-400' : 'text-slate-200'}`}>
            {node.alerts || 0}
          </span>
        </div>

        <div className="py-2">
          <div className="flex justify-between mb-1.5">
            <span className="text-slate-400">AI Anomaly Score:</span>
            <span className={`font-bold ${isHighRisk ? 'text-red-400' : 'text-cyan-400'}`}>
              {formatPercentage(node.anomaly_score)}
            </span>
          </div>
          <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800">
            <div
              className={`h-full transition-all duration-500 ${
                isHighRisk ? 'bg-gradient-to-r from-orange-500 to-red-500' : 'bg-cyan-500'
              }`}
              style={{ width: `${(node.anomaly_score || 0.1) * 100}%` }}
            />
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="mt-4 pt-3 border-t border-slate-800 flex gap-2">
        <button
          onClick={() => navigate(`/nodes/${node.id}`)}
          className="flex-1 py-2 px-3 bg-cyan-950/60 hover:bg-cyan-900/60 text-cyan-300 rounded-lg border border-cyan-500/30 flex items-center justify-center gap-1.5 transition-all text-xs font-semibold"
        >
          <span>Deep Inspect</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </button>

        <button
          onClick={() => navigate(`/events?search=${node.id}`)}
          className="py-2 px-3 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg border border-slate-700 transition-all text-xs"
          title="View related telemetry events"
        >
          <Activity className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};

export default NodeDetails;
