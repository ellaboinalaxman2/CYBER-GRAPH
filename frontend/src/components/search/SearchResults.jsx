import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Server, Activity, ShieldAlert, Flame, ArrowRight } from 'lucide-react';
import Badge from '../common/Badge';

export const SearchResults = ({ results = {}, onSelect }) => {
  const navigate = useNavigate();

  const { nodes = [], events = [], alerts = [], attacks = [] } = results;
  const total = nodes.length + events.length + alerts.length + attacks.length;

  if (total === 0) {
    return (
      <div className="p-8 text-center text-xs font-mono text-slate-500">
        No matched entities found.
      </div>
    );
  }

  return (
    <div className="space-y-4 font-mono text-xs">
      {/* Nodes / Assets */}
      {nodes.length > 0 && (
        <div>
          <h4 className="text-[11px] text-slate-400 uppercase font-bold mb-2 flex items-center gap-1.5">
            <Server className="w-3.5 h-3.5 text-cyan-400" />
            <span>Assets & Nodes ({nodes.length})</span>
          </h4>
          <div className="space-y-1.5">
            {nodes.map((node) => (
              <div
                key={node.id}
                onClick={() => navigate(`/nodes/${node.id}`)}
                className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 hover:border-cyan-500/40 cursor-pointer flex items-center justify-between"
              >
                <div>
                  <span className="font-bold text-slate-200">{node.id}</span>
                  <span className="text-slate-500 ml-2">({node.ip})</span>
                </div>
                <Badge severity={node.risk || 'LOW'} size="sm">{node.type}</Badge>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Events */}
      {events.length > 0 && (
        <div>
          <h4 className="text-[11px] text-slate-400 uppercase font-bold mb-2 flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5 text-emerald-400" />
            <span>Security Events ({events.length})</span>
          </h4>
          <div className="space-y-1.5">
            {events.map((evt) => (
              <div
                key={evt.id}
                onClick={() => navigate(`/events?search=${evt.id}`)}
                className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 hover:border-cyan-500/40 cursor-pointer flex items-center justify-between"
              >
                <div>
                  <span className="font-bold text-cyan-400">{evt.id}</span>
                  <span className="text-slate-300 ml-2">{evt.source} &rarr; {evt.destination} ({evt.event})</span>
                </div>
                <span className="text-slate-400 text-[11px]">{evt.time}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Alerts */}
      {alerts.length > 0 && (
        <div>
          <h4 className="text-[11px] text-slate-400 uppercase font-bold mb-2 flex items-center gap-1.5">
            <ShieldAlert className="w-3.5 h-3.5 text-red-400" />
            <span>Security Alerts ({alerts.length})</span>
          </h4>
          <div className="space-y-1.5">
            {alerts.map((alt) => (
              <div
                key={alt.id}
                onClick={() => navigate('/alerts')}
                className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 hover:border-red-500/40 cursor-pointer flex items-center justify-between"
              >
                <div>
                  <span className="font-bold text-slate-200">{alt.title}</span>
                  <span className="text-slate-500 ml-2">({alt.source} &rarr; {alt.destination})</span>
                </div>
                <Badge severity={alt.severity} size="sm">{alt.severity}</Badge>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchResults;
