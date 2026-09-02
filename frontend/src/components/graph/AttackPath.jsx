import React, { useState } from 'react';
import { Play, Pause, RotateCcw, AlertTriangle, ShieldCheck, ChevronRight } from 'lucide-react';
import Badge from '../common/Badge';

export const AttackPath = ({
  attackPath = [],
  timeline = [],
  onStepSelect,
  activeStepIndex = 0,
}) => {
  const [isPlaying, setIsPlaying] = useState(false);

  return (
    <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 shadow-2xl backdrop-blur-md">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-red-400" />
          <h4 className="text-xs font-bold font-mono text-slate-200 uppercase tracking-wider">
            Reconstructed Attack Path
          </h4>
        </div>
        <Badge severity="CRITICAL" size="sm">
          Active Traversal
        </Badge>
      </div>

      {/* Path Breadcrumbs / Steps */}
      <div className="mt-3 flex items-center gap-2 overflow-x-auto pb-2">
        {attackPath.map((nodeId, idx) => {
          const isCurrent = idx === activeStepIndex;
          const isPast = idx < activeStepIndex;

          return (
            <React.Fragment key={idx}>
              <button
                onClick={() => onStepSelect?.(idx)}
                className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition-all flex items-center gap-1.5 flex-shrink-0 ${
                  isCurrent
                    ? 'bg-red-500 text-white shadow-lg shadow-red-500/30 scale-105'
                    : isPast
                    ? 'bg-red-950/60 text-red-300 border border-red-500/40'
                    : 'bg-slate-800 text-slate-400 hover:text-slate-200'
                }`}
              >
                <span className="text-[10px] opacity-75">{idx + 1}.</span>
                <span>{nodeId}</span>
              </button>

              {idx < attackPath.length - 1 && (
                <ChevronRight className="w-3.5 h-3.5 text-slate-600 flex-shrink-0" />
              )}
            </React.Fragment>
          );
        })}
      </div>

      {/* Timeline details for the active step if available */}
      {timeline && timeline[activeStepIndex] && (
        <div className="mt-3 p-3 rounded-lg bg-slate-950/80 border border-slate-800/80 text-xs font-mono">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-cyan-400 font-bold">Step {activeStepIndex + 1}: {timeline[activeStepIndex].event}</span>
            <span>{timeline[activeStepIndex].time}</span>
          </div>
          <p className="text-slate-300 mt-1 text-[11px] font-sans">
            {timeline[activeStepIndex].desc}
          </p>
        </div>
      )}
    </div>
  );
};

export default AttackPath;
