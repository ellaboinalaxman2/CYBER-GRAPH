import React from 'react';

export const SearchFilters = ({
  category = 'ALL',
  onCategoryChange,
}) => {
  const categories = [
    { id: 'ALL', label: 'All Results' },
    { id: 'NODES', label: 'Nodes & Assets' },
    { id: 'EVENTS', label: 'Security Events' },
    { id: 'ALERTS', label: 'Alerts' },
    { id: 'ATTACKS', label: 'Attacks' },
  ];

  return (
    <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs font-mono">
      {categories.map((cat) => (
        <button
          key={cat.id}
          onClick={() => onCategoryChange(cat.id)}
          className={`px-3 py-1.5 rounded-lg whitespace-nowrap transition-all ${
            category === cat.id
              ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 font-bold'
              : 'bg-slate-900 text-slate-400 border border-slate-800 hover:text-slate-200'
          }`}
        >
          {cat.label}
        </button>
      ))}
    </div>
  );
};

export default SearchFilters;
