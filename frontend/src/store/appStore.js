let listeners = [];
let state = {
  theme: 'dark',
  sidebarOpen: true,
  notifications: [],
  systemHealth: 'OPTIMAL',
  autoRefreshInterval: 5000,
};

export const appStore = {
  getState: () => state,
  toggleSidebar: () => {
    state = { ...state, sidebarOpen: !state.sidebarOpen };
    listeners.forEach((l) => l(state));
  },
  setSidebarOpen: (isOpen) => {
    state = { ...state, sidebarOpen: isOpen };
    listeners.forEach((l) => l(state));
  },
  addNotification: (notification) => {
    const item = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      ...notification,
    };
    state = { ...state, notifications: [item, ...state.notifications].slice(0, 20) };
    listeners.forEach((l) => l(state));
  },
  clearNotifications: () => {
    state = { ...state, notifications: [] };
    listeners.forEach((l) => l(state));
  },
  subscribe: (listener) => {
    listeners.push(listener);
    return () => {
      listeners = listeners.filter((l) => l !== listener);
    };
  },
};
