import React from 'react';

export const Footer = () => {
  return (
    <footer className="py-4 px-6 border-t border-slate-800/60 bg-slate-950/40 text-xs text-slate-500 flex flex-col sm:flex-row items-center justify-between gap-2">
      <div className="flex items-center gap-2 font-mono">
        <span className="text-cyan-500">CYBER GRAPH</span>
        <span>• SOC Operations Defense Platform</span>
      </div>
      <div className="flex items-center gap-4 font-mono text-[11px]">
        <span>Member 1 (Frontend)</span>
        <span>Connected to Member 7 (API)</span>
        <span className="text-emerald-400">● Live Synced</span>
      </div>
    </footer>
  );
};

export default Footer;
