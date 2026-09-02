import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldAlert, ArrowRight, Clock } from 'lucide-react';
import Badge from '../common/Badge';
import { formatTimestamp } from '../../utils/dateUtils';

export const RecentAlerts = ({ alerts = [] }) => {
  const navigate = useNavigate();

  return (
    <div className="space-y-3">
      {alerts.length === 0 ? (
        <p className="text-xs text-slate-500 font-mono py-4 text-center">No active alerts</p>
      ) : (
        alerts.map((alert) => (
          <div
            key={alert.id}
            onClick={() => navigate('/alerts')}
            className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-cyan-500/40 cursor-pointer transition-all duration-150 flex items-center justify-between gap-3 group"
          >
            <div className="flex items-start gap-3 min-w-0">
              <div className="mt-0.5">
                <span
                  className={`w-2.5 h-2.5 rounded-full inline-block ${
                    alert.severity === 'CRITICAL'
                      ? 'bg-red-500 animate-pulse'
                      : alert.severity === 'HIGH'
                      ? 'bg-orange-500'
                      : alert.severity === 'MEDIUM'
                      ? 'bg-yellow-500'
                      : 'bg-blue-500'
                  }`}
                />
              </div>
              <div className="min-w-0">
                <h5 className="text-xs font-semibold text-slate-200 group-hover:text-cyan-400 transition-colors truncate">
                  {alert.title}
                </h5>
                <div className="flex items-center gap-2 mt-1 text-[11px] text-slate-400 font-mono">
                  <span>{alert.source} &rarr; {alert.destination}</span>
                  <span>•</span>
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {formatTimestamp(alert.timestamp)}
                  </span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2 flex-shrink-0">
              <Badge severity={alert.severity} size="sm">
                {alert.severity}
              </Badge>
              <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-cyan-400 group-hover:translate-x-0.5 transition-all" />
            </div>
          </div>
        ))
      )}
    </div>
  );
};

export default RecentAlerts;
