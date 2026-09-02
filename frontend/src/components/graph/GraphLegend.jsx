import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Layers, Info } from 'lucide-react';
import { NODE_TYPE_CONFIG } from '../../constants/nodeTypes';

export const GraphLegend = () => {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3.5 shadow-2xl backdrop-blur-md max-w-xs text-xs font-mono">
      <div
        onClick={() => setCollapsed(!collapsed)}
        className="flex items-center justify-between cursor-pointer text-slate-300 hover:text-cyan-400"
      >
        <div className="flex items-center gap-2">
          <Layers className="w-3.5 h-3.5 text-cyan-400" />
          <span className="font-semibold uppercase tracking-wider">Topology Legend</span>
        </div>
        {collapsed ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
      </div>

      {!collapsed && (
        <div className="mt-3 space-y-3 pt-2 border-t border-slate-800/80">
          <div>
            <p className="text-[10px] text-slate-500 uppercase tracking-widest mb-1.5 font-bold">Node Roles</p>
            <div className="grid grid-cols-2 gap-2 text-[11px]">
              {Object.entries(NODE_TYPE_CONFIG).map(([key, item]) => (
                <div key={key} className="flex items-center gap-1.5 text-slate-300">
                  <span
                    className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="truncate">{item.label.split('/')[0]}</span>
                </div>
              ))}
            </div>
          </div>

          <div>
            <p className="text-[10px] text-slate-500 uppercase tracking-widest mb-1.5 font-bold">Status Indication</p>
            <div className="space-y-1 text-[11px]">
              <div className="flex items-center gap-2 text-slate-300">
                <span className="w-2.5 h-2.5 rounded-full bg-red-500 ring-2 ring-red-500/30 animate-pulse" />
                <span>Suspicious / High Anomaly (&gt;0.70)</span>
              </div>
              <div className="flex items-center gap-2 text-slate-300">
                <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" />
                <span>Normal Baseline Telemetry</span>
              </div>
              <div className="flex items-center gap-2 text-slate-300">
                <span className="w-3 h-0.5 bg-red-500 border border-red-400" />
                <span className="text-red-400 font-bold">Active Attack Path Traversal</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GraphLegend;
