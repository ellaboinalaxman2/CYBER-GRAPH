import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Flame, ArrowRight, ShieldAlert, Clock, Target } from 'lucide-react';
import Badge from '../common/Badge';
import { formatTimestamp } from '../../utils/dateUtils';

export const AttackCard = ({ attack, onClick }) => {
  const navigate = useNavigate();

  const handleClick = () => {
    if (onClick) onClick(attack);
    else navigate(`/attacks/${attack.id}`);
  };

  return (
    <div
      onClick={handleClick}
      className="p-6 rounded-2xl border border-slate-800 bg-slate-900/60 hover:border-red-500/40 hover:bg-slate-900/90 transition-all duration-200 cursor-pointer shadow-lg group"
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-800/80">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-lg bg-red-500/10 text-red-400 border border-red-500/20 group-hover:scale-110 transition-transform">
            <Flame className="w-5 h-5" />
          </div>
          <div>
            <span className="text-xs font-mono text-slate-400">{attack.id}</span>
            <h4 className="text-base font-bold text-slate-100 group-hover:text-red-400 transition-colors">
              {attack.title}
            </h4>
          </div>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto">
          <Badge severity={attack.riskLevel}>
            Risk {attack.riskScore}/100
          </Badge>
        </div>
      </div>

      <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs font-mono">
        <div className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/60">
          <span className="text-slate-500 block text-[10px] uppercase">Attack Vector Type</span>
          <span className="text-slate-200 font-semibold">{attack.type}</span>
        </div>
        <div className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/60">
          <span className="text-slate-500 block text-[10px] uppercase">MITRE Technique</span>
          <span className="text-indigo-400 font-semibold">{attack.mitre?.techniqueId} - {attack.mitre?.techniqueName}</span>
        </div>
      </div>

      {/* Traversal Path */}
      <div className="mt-4 pt-3 border-t border-slate-800/60 flex items-center justify-between text-xs font-mono">
        <div className="flex items-center gap-1.5 overflow-x-auto py-1">
          <span className="text-slate-500">Path:</span>
          {attack.path?.map((step, idx) => (
            <React.Fragment key={idx}>
              <span className={`px-2 py-0.5 rounded text-[11px] ${idx === attack.path.length - 1 ? 'bg-red-500/20 text-red-300 font-bold' : 'bg-slate-800 text-slate-300'}`}>
                {step}
              </span>
              {idx < attack.path.length - 1 && <span className="text-slate-600">&rarr;</span>}
            </React.Fragment>
          ))}
        </div>

        <span className="text-cyan-400 group-hover:translate-x-1 transition-transform flex items-center gap-1 font-bold pl-2 flex-shrink-0">
          Inspect &rarr;
        </span>
      </div>
    </div>
  );
};

export default AttackCard;
