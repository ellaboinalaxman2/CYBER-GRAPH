import React from 'react';
import { Filter, RotateCcw } from 'lucide-react';
import { NODE_TYPES } from '../../constants/nodeTypes';
import { SEVERITY } from '../../constants/severity';

export const GraphFilters = ({
  filters,
  onFilterChange,
  onReset,
}) => {
  return (
    <div className="flex flex-wrap items-center gap-2.5 p-2 rounded-xl bg-slate-900/90 border border-slate-800 backdrop-blur-md text-xs font-mono">
      <div className="flex items-center gap-1.5 text-slate-400 pl-2">
        <Filter className="w-3.5 h-3.5 text-cyan-400" />
        <span className="font-semibold uppercase tracking-wider text-[10px]">Filter:</span>
      </div>

      {/* Node Type Filter */}
      <select
        value={filters.nodeType || 'ALL'}
        onChange={(e) => onFilterChange({ nodeType: e.target.value })}
        className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1 text-slate-200 focus:outline-none focus:border-cyan-500"
      >
        <option value="ALL">All Node Types</option>
        <option value="endpoint">Endpoint / PC</option>
        <option value="server">Server</option>
        <option value="database">Database</option>
        <option value="router">Router</option>
        <option value="firewall">Firewall</option>
        <option value="user">User</option>
      </select>

      {/* Severity Filter */}
      <select
        value={filters.severity || 'ALL'}
        onChange={(e) => onFilterChange({ severity: e.target.value })}
        className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1 text-slate-200 focus:outline-none focus:border-cyan-500"
      >
        <option value="ALL">All Threat Levels</option>
        <option value="CRITICAL">Critical Risk</option>
        <option value="HIGH">High Risk</option>
        <option value="MEDIUM">Medium Risk</option>
        <option value="LOW">Low Risk</option>
      </select>

      {/* Search Input */}
      <input
        type="text"
        placeholder="Filter by ID / IP..."
        value={filters.searchTerm || ''}
        onChange={(e) => onFilterChange({ searchTerm: e.target.value })}
        className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1 text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-cyan-500 w-36 sm:w-44"
      >
      </input>

      {/* Reset Filter Button */}
      <button
        onClick={onReset}
        className="p-1 text-slate-400 hover:text-cyan-400 hover:bg-slate-800 rounded-md transition-colors ml-auto"
        title="Reset all filters"
      >
        <RotateCcw className="w-3.5 h-3.5" />
      </button>
    </div>
  );
};

export default GraphFilters;
