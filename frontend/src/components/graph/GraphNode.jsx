import React from 'react';
import { Server, Monitor, Database, Router, Shield, User } from 'lucide-react';
import Badge from '../common/Badge';

const NODE_ICONS = {
  endpoint: Monitor,
  pc: Monitor,
  server: Server,
  database: Database,
  router: Router,
  firewall: Shield,
  user: User,
};

export const GraphNode = ({ node, isSelected, onClick }) => {
  const Icon = NODE_ICONS[node.type?.toLowerCase()] || Server;
  const isSuspicious = node.anomaly_score > 0.7 || node.risk === 'CRITICAL' || node.risk === 'HIGH';

  return (
    <div
      onClick={() => onClick?.(node)}
      className={`p-3 rounded-xl border transition-all cursor-pointer flex items-center justify-between gap-3 ${
        isSelected
          ? 'bg-cyan-950/60 border-cyan-400 ring-1 ring-cyan-400'
          : isSuspicious
          ? 'bg-red-950/20 border-red-500/40 hover:border-red-400'
          : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
      }`}
    >
      <div className="flex items-center gap-2.5 min-w-0">
        <div
          className={`p-2 rounded-lg ${
            isSuspicious ? 'bg-red-500/20 text-red-400' : 'bg-cyan-500/20 text-cyan-400'
          }`}
        >
          <Icon className="w-4 h-4" />
        </div>
        <div className="min-w-0">
          <p className="text-xs font-bold font-mono text-slate-200 truncate">{node.label || node.id}</p>
          <p className="text-[10px] text-slate-400 font-mono">{node.ip}</p>
        </div>
      </div>

      <Badge severity={node.risk || 'LOW'} size="sm">
        {node.type}
      </Badge>
    </div>
  );
};

export default GraphNode;
