let listeners = [];
let state = {
  nodes: [],
  edges: [],
  selectedNode: null,
  selectedEdge: null,
  activeAttackPath: null,
  filters: {
    nodeType: 'ALL',
    severity: 'ALL',
    protocol: 'ALL',
    searchTerm: '',
  },
  loading: false,
  error: null,
};

export const graphStore = {
  getState: () => state,
  setState: (updater) => {
    state = typeof updater === 'function' ? updater(state) : { ...state, ...updater };
    listeners.forEach((l) => l(state));
  },
  setSelectedNode: (node) => {
    state = { ...state, selectedNode: node };
    listeners.forEach((l) => l(state));
  },
  setActiveAttackPath: (attackPath) => {
    state = { ...state, activeAttackPath: attackPath };
    listeners.forEach((l) => l(state));
  },
  setFilters: (filters) => {
    state = { ...state, filters: { ...state.filters, ...filters } };
    listeners.forEach((l) => l(state));
  },
  resetFilters: () => {
    state = {
      ...state,
      filters: { nodeType: 'ALL', severity: 'ALL', protocol: 'ALL', searchTerm: '' },
      activeAttackPath: null,
      selectedNode: null,
    };
    listeners.forEach((l) => l(state));
  },
  subscribe: (listener) => {
    listeners.push(listener);
    return () => {
      listeners = listeners.filter((l) => l !== listener);
    };
  },
};
