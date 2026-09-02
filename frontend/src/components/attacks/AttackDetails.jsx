import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Flame, ShieldAlert, Cpu, CheckCircle, Network, ArrowLeft } from 'lucide-react';
import Badge from '../common/Badge';
import RiskScore from './RiskScore';
import MitreTechnique from './MitreTechnique';
import AttackTimeline from './AttackTimeline';
import AttackPath from './AttackPath';
import { formatDateTime } from '../../utils/dateUtils';
import Button from '../common/Button';

export const AttackDetails = ({ attack }) => {
  const navigate = useNavigate();

  if (!attack) {
    return (
      <div className="p-8 text-center text-xs font-mono text-slate-500">
        Attack incident details not loaded
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Overview Card */}
      <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/80 backdrop-blur-md">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <Badge severity={attack.riskLevel} dot>
                {attack.riskLevel} RISK
              </Badge>
              <span className="text-xs font-mono text-slate-400">{attack.id}</span>
            </div>
            <h2 className="text-xl font-bold text-slate-100">{attack.title}</h2>
          </div>

          <Button
            variant="outline"
            size="sm"
            icon={Network}
            onClick={() => navigate('/graph')}
          >
            Trace in Cyber Graph
          </Button>
        </div>

        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <RiskScore score={attack.riskScore} />
          <MitreTechnique mitre={attack.mitre} />

          {/* AI Assessment Brief */}
          <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 font-mono text-xs space-y-2">
            <div className="flex items-center justify-between text-indigo-300">
              <span className="font-bold uppercase tracking-wider">AI Engine (M3)</span>
              <Cpu className="w-4 h-4 text-indigo-400" />
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Class:</span>
              <span className="text-red-400 font-bold">{attack.aiAnalysis?.prediction || 'ATTACK'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Model:</span>
              <span className="text-slate-300 font-mono">{attack.aiAnalysis?.model || 'GraphSAGE'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Anomaly:</span>
              <span className="text-orange-400 font-bold">{Math.round((attack.aiAnalysis?.anomaly_score || 0.9) * 100)}%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Path Reconstitution & Timeline */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Visual Attack Path */}
        <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/80">
          <h3 className="text-sm font-bold font-mono text-slate-200 uppercase tracking-wider mb-4 flex items-center gap-2">
            <Network className="w-4 h-4 text-cyan-400" />
            Multi-Hop Attack Path
          </h3>
          <AttackPath
            attackPath={attack.path || []}
            timeline={attack.timeline || []}
          />
        </div>

        {/* Step-by-Step Timeline */}
        <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/80">
          <h3 className="text-sm font-bold font-mono text-slate-200 uppercase tracking-wider mb-4 flex items-center gap-2">
            <Flame className="w-4 h-4 text-red-400" />
            Reconstructed Chronological Sequence
          </h3>
          <AttackTimeline timeline={attack.timeline || []} />
        </div>
      </div>
    </div>
  );
};

export default AttackDetails;
