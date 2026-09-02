let listeners = [];
let state = {
  alerts: [],
  selectedAlert: null,
  filters: {
    severity: 'ALL',
    status: 'ALL',
    search: '',
  },
  loading: false,
};

export const alertStore = {
  getState: () => state,
  setAlerts: (alerts) => {
    state = { ...state, alerts, loading: false };
    listeners.forEach((l) => l(state));
  },
  setSelectedAlert: (alert) => {
    state = { ...state, selectedAlert: alert };
    listeners.forEach((l) => l(state));
  },
  setFilters: (filters) => {
    state = { ...state, filters: { ...state.filters, ...filters } };
    listeners.forEach((l) => l(state));
  },
  updateAlertStatus: (id, status) => {
    state = {
      ...state,
      alerts: state.alerts.map((a) => (a.id === id ? { ...a, status } : a)),
      selectedAlert: state.selectedAlert?.id === id ? { ...state.selectedAlert, status } : state.selectedAlert,
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
