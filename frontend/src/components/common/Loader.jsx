import React from 'react';
import { Loader2 } from 'lucide-react';

export const Loader = ({ text = 'Loading cyber telemetry...', size = 'md', className = '' }) => {
  const sizeMap = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  return (
    <div className={`flex flex-col items-center justify-center p-8 text-cyan-400 gap-3 ${className}`}>
      <Loader2 className={`${sizeMap[size] || sizeMap.md} animate-spin text-cyan-400`} />
      {text && <span className="text-xs font-mono text-slate-400 tracking-wider animate-pulse">{text}</span>}
    </div>
  );
};

export default Loader;
