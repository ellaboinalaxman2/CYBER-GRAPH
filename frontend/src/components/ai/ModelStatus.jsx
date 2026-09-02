import React from 'react';
import { Cpu, Activity, CheckCircle, Zap } from 'lucide-react';
import Badge from '../common/Badge';

export const ModelStatus = ({ modelStatus }) => {
  const status = modelStatus || {
    status: 'ACTIVE_INFERENCE',
    modelName: 'GraphSAGE-CyberGNN',
    version: '2.4.1',
    accuracy: 0.984,
    latencyMs: 14,
    connectedTo: 'Member 3 (AI Engine)',
  };

  return (
    <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 font-mono text-xs space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Cpu className="w-4 h-4 text-indigo-400" />
          <span className="font-bold text-slate-200 uppercase tracking-wider">{status.modelName}</span>
        </div>
        <Badge variant="cyber" size="sm">v{status.version}</Badge>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[11px]">
        <div className="p-2 rounded bg-slate-900 border border-slate-800/80">
          <span className="text-slate-500 block">Inference Speed</span>
          <span className="text-emerald-400 font-bold flex items-center gap-1 mt-0.5">
            <Zap className="w-3 h-3" />
            {status.latencyMs}ms
          </span>
        </div>

        <div className="p-2 rounded bg-slate-900 border border-slate-800/80">
          <span className="text-slate-500 block">ROC-AUC Score</span>
          <span className="text-cyan-400 font-bold mt-0.5 block">
            {Math.round(status.accuracy * 1000) / 10}%
          </span>
        </div>
      </div>

      <div className="text-[10px] text-slate-500 flex items-center justify-between pt-1 border-t border-slate-800/60">
        <span>Provider: {status.connectedTo}</span>
        <span className="text-emerald-400">● Online</span>
      </div>
    </div>
  );
};

export default ModelStatus;
