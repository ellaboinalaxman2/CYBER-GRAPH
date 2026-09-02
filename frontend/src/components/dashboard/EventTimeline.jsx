import React from 'react';
import { Clock, CheckCircle2, XCircle, AlertTriangle } from 'lucide-react';
import { formatTimestamp } from '../../utils/dateUtils';

export const EventTimeline = ({ events = [] }) => {
  const getStatusIcon = (status) => {
    switch (status?.toLowerCase()) {
      case 'allowed':
      case 'success':
        return <CheckCircle2 className="w-4 h-4 text-emerald-400" />;
      case 'failed':
      case 'blocked':
        return <XCircle className="w-4 h-4 text-red-400" />;
      default:
        return <AlertTriangle className="w-4 h-4 text-yellow-400" />;
    }
  };

  return (
    <div className="relative pl-6 space-y-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
      {events.map((evt, idx) => (
        <div key={evt.id || idx} className="relative group">
          <div className="absolute -left-6 top-1 p-0.5 bg-slate-950 rounded-full border border-slate-700">
            {getStatusIcon(evt.status)}
          </div>
          <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800/80 group-hover:border-slate-700 transition-colors">
            <div className="flex items-center justify-between text-xs font-mono">
              <span className="font-bold text-slate-200">{evt.event}</span>
              <span className="text-slate-400 flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {evt.time || formatTimestamp(evt.timestamp)}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1 font-mono">
              {evt.source} &rarr; {evt.destination}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default EventTimeline;
