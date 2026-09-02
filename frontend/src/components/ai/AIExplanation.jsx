import React from 'react';
import { HelpCircle, AlertCircle, CheckCircle } from 'lucide-react';

export const AIExplanation = ({
  explanations = [],
  title = 'Why suspicious?',
  prediction = 'ATTACK',
}) => {
  const isAttack = prediction?.toUpperCase() === 'ATTACK';

  return (
    <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 font-mono text-xs">
      <div className="flex items-center gap-2 mb-3">
        {isAttack ? (
          <AlertCircle className="w-4 h-4 text-red-400" />
        ) : (
          <CheckCircle className="w-4 h-4 text-emerald-400" />
        )}
        <h4 className="font-bold text-slate-200 uppercase tracking-wider">{title}</h4>
      </div>

      {explanations && explanations.length > 0 ? (
        <ul className="space-y-2 text-slate-300 font-sans">
          {explanations.map((exp, idx) => (
            <li key={idx} className="flex items-start gap-2">
              <span className="text-cyan-400 font-mono font-bold">•</span>
              <span className="text-xs leading-relaxed">{exp}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-slate-500 font-sans italic">No explanation factors reported by AI engine.</p>
      )}
    </div>
  );
};

export default AIExplanation;
