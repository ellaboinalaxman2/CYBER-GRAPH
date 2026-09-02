import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Flame, ShieldAlert, ArrowRight, Target } from 'lucide-react';
import Badge from '../common/Badge';

export const AttackSummary = ({ attacks = [] }) => {
  const navigate = useNavigate();

  return (
    <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Flame className="w-5 h-5 text-red-400" />
          <h3 className="text-base font-semibold text-slate-100">Correlated Attack Campaigns</h3>
        </div>
        <button
          onClick={() => navigate('/attacks')}
          className="text-xs text-cyan-400 hover:text-cyan-300 font-mono flex items-center gap-1"
        >
          View all &rarr;
        </button>
      </div>

      <div className="mt-4 space-y-3">
        {attacks.slice(0, 2).map((atk) => (
          <div
            key={atk.id}
            onClick={() => navigate(`/attacks/${atk.id}`)}
            className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 hover:border-red-500/40 cursor-pointer transition-all duration-200"
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <span className="text-xs font-mono text-slate-400">{atk.id}</span>
                <h4 className="text-sm font-semibold text-slate-200 mt-0.5">{atk.title}</h4>
              </div>
              <div className="flex items-center gap-2">
                <Badge severity={atk.riskLevel}>{atk.riskLevel} RISK ({atk.riskScore}/100)</Badge>
              </div>
            </div>

            <div className="mt-3 flex items-center gap-2 text-xs font-mono text-slate-400 overflow-x-auto py-1">
              <span className="text-slate-500 font-sans">Attack Vector:</span>
              {atk.path?.map((step, idx) => (
                <React.Fragment key={idx}>
                  <span className={`px-2 py-0.5 rounded ${idx === atk.path.length - 1 ? 'bg-red-500/20 text-red-400 border border-red-500/30' : 'bg-slate-800 text-slate-300'}`}>
                    {step}
                  </span>
                  {idx < atk.path.length - 1 && <span className="text-slate-600">&rarr;</span>}
                </React.Fragment>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AttackSummary;
