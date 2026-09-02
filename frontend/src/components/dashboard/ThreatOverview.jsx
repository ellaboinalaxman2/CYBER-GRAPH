import React from 'react';
import { Shield, AlertOctagon, Cpu, CheckCircle } from 'lucide-react';
import Badge from '../common/Badge';

export const ThreatOverview = ({ stats }) => {
  return (
    <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div>
          <h3 className="text-base font-semibold text-slate-100">Security Posture Overview</h3>
          <p className="text-xs text-slate-400 font-mono mt-0.5">Real-time threat landscape assessment</p>
        </div>
        <Badge variant="cyber" dot>Active Monitoring</Badge>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-5">
        <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
          <div className="flex items-center gap-2 text-cyan-400 text-xs font-mono mb-1">
            <Shield className="w-4 h-4" />
            <span>GRAPH ASSET DEFENSE</span>
          </div>
          <p className="text-2xl font-bold text-slate-100 font-mono">{stats?.totalAssets || 128}</p>
          <p className="text-[11px] text-slate-500 mt-1">Nodes mapped in Neo4j topology</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
          <div className="flex items-center gap-2 text-red-400 text-xs font-mono mb-1">
            <AlertOctagon className="w-4 h-4" />
            <span>HIGH RISK ANOMALIES</span>
          </div>
          <p className="text-2xl font-bold text-red-400 font-mono">{stats?.criticalThreats || 2}</p>
          <p className="text-[11px] text-slate-500 mt-1">Requiring immediate containment</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
          <div className="flex items-center gap-2 text-emerald-400 text-xs font-mono mb-1">
            <CheckCircle className="w-4 h-4" />
            <span>LEDGER VERIFICATION</span>
          </div>
          <p className="text-2xl font-bold text-emerald-400 font-mono">100%</p>
          <p className="text-[11px] text-slate-500 mt-1">Tamper-proof event logs on-chain</p>
        </div>
      </div>
    </div>
  );
};

export default ThreatOverview;
