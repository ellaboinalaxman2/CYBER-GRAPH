import React from 'react';
import { Search, Filter, RotateCcw } from 'lucide-react';
import { SEVERITY } from '../../constants/severity';

export const AlertFilters = ({
  filters,
  onFilterChange,
  onReset,
}) => {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 p-4 rounded-xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm text-xs font-mono">
      <div className="flex flex-wrap items-center gap-3">
        {/* Search */}
        <div className="relative">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search alerts, techniques, IPs..."
            value={filters.search || ''}
            onChange={(e) => onFilterChange({ search: e.target.value })}
            className="bg-slate-950 border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-cyan-500 w-56 sm:w-64"
          />
        </div>

        {/* Severity Selector */}
        <div className="flex items-center gap-1.5">
          <span className="text-slate-400 text-[11px] uppercase">Severity:</span>
          <select
            value={filters.severity || 'ALL'}
            onChange={(e) => onFilterChange({ severity: e.target.value })}
            className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">Critical Only</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
            <option value="INFO">Info</option>
          </select>
        </div>

        {/* Status Selector */}
        <div className="flex items-center gap-1.5">
          <span className="text-slate-400 text-[11px] uppercase">Status:</span>
          <select
            value={filters.status || 'ALL'}
            onChange={(e) => onFilterChange({ status: e.target.value })}
            className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">All Statuses</option>
            <option value="ACTIVE">Active</option>
            <option value="INVESTIGATING">Investigating</option>
            <option value="RESOLVED">Resolved</option>
          </select>
        </div>
      </div>

      {onReset && (
        <button
          onClick={onReset}
          className="flex items-center gap-1 text-slate-400 hover:text-cyan-400 text-xs px-2.5 py-1.5 rounded-lg hover:bg-slate-800 transition-colors"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset</span>
        </button>
      )}
    </div>
  );
};

export default AlertFilters;
