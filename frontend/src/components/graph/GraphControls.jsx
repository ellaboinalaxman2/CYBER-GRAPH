import React from 'react';
import { ZoomIn, ZoomOut, Maximize2, RotateCcw, Search, Sparkles } from 'lucide-react';

export const GraphControls = ({
  onZoomIn,
  onZoomOut,
  onFit,
  onResetLayout,
  onToggleLayout,
  currentLayout = 'cose',
}) => {
  return (
    <div className="flex items-center gap-1.5 p-1.5 rounded-xl bg-slate-900/90 border border-slate-800 shadow-2xl backdrop-blur-md">
      <button
        onClick={onZoomIn}
        className="p-2 rounded-lg text-slate-300 hover:text-cyan-400 hover:bg-slate-800 transition-colors"
        title="Zoom In"
      >
        <ZoomIn className="w-4 h-4" />
      </button>

      <button
        onClick={onZoomOut}
        className="p-2 rounded-lg text-slate-300 hover:text-cyan-400 hover:bg-slate-800 transition-colors"
        title="Zoom Out"
      >
        <ZoomOut className="w-4 h-4" />
      </button>

      <div className="w-[1px] h-5 bg-slate-800 mx-1" />

      <button
        onClick={onFit}
        className="p-2 rounded-lg text-slate-300 hover:text-cyan-400 hover:bg-slate-800 transition-colors"
        title="Fit Graph to Viewport"
      >
        <Maximize2 className="w-4 h-4" />
      </button>

      <button
        onClick={onResetLayout}
        className="p-2 rounded-lg text-slate-300 hover:text-cyan-400 hover:bg-slate-800 transition-colors"
        title="Reset Physics Layout"
      >
        <RotateCcw className="w-4 h-4" />
      </button>

      {onToggleLayout && (
        <button
          onClick={onToggleLayout}
          className="flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-mono text-cyan-400 hover:bg-cyan-950/50 transition-colors"
          title="Switch Layout Algorithm"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span className="capitalize">{currentLayout}</span>
        </button>
      )}
    </div>
  );
};

export default GraphControls;
