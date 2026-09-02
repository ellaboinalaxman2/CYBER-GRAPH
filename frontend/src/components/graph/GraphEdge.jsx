import React from 'react';
import { ArrowRight } from 'lucide-react';

export const GraphEdge = ({ edge, isHighlighted }) => {
  return (
    <div
      className={`p-2.5 rounded-lg border text-xs font-mono flex items-center justify-between gap-3 ${
        isHighlighted
          ? 'bg-red-950/40 border-red-500/50 text-red-300'
          : 'bg-slate-900/40 border-slate-800 text-slate-400'
      }`}
    >
      <div className="flex items-center gap-2">
        <span className="font-bold text-slate-200">{edge.source}</span>
        <ArrowRight className="w-3.5 h-3.5 text-cyan-400" />
        <span className="font-bold text-slate-200">{edge.target}</span>
      </div>
      <div className="flex items-center gap-2">
        <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-cyan-300">
          {edge.protocol || edge.type}
        </span>
      </div>
    </div>
  );
};

export default GraphEdge;
