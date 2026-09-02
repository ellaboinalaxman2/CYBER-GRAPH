import React from 'react';
import { Shield, ExternalLink } from 'lucide-react';
import Badge from '../common/Badge';

export const MitreTechnique = ({ mitre }) => {
  if (!mitre) {
    return (
      <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 text-xs font-mono text-slate-500">
        No MITRE ATT&CK mapping assigned
      </div>
    );
  }

  return (
    <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 font-mono">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Shield className="w-4 h-4 text-cyan-400" />
          <span className="text-xs text-slate-300 font-bold uppercase tracking-wider">MITRE ATT&CK Mapping</span>
        </div>
        {mitre.url && (
          <a
            href={mitre.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-[11px] text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
          >
            <span>MITRE KB</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        )}
      </div>

      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <span className="px-2 py-1 rounded bg-red-950/80 text-red-400 border border-red-500/40 text-xs font-bold">
            {mitre.techniqueId || 'T1021'}
          </span>
          <span className="text-xs font-semibold text-slate-100">{mitre.techniqueName || 'Remote Services'}</span>
        </div>

        {mitre.tactic && (
          <div className="text-[11px] text-slate-400">
            <span className="text-slate-500">Tactic: </span>
            <span className="text-slate-300">{mitre.tactic}</span>
          </div>
        )}

        {mitre.subTechnique && (
          <div className="text-[11px] text-slate-400">
            <span className="text-slate-500">Sub-Technique: </span>
            <span className="text-slate-300">{mitre.subTechnique}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default MitreTechnique;
