// Simple reactive auth state container

let listeners = [];
let state = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,
};

// Initialize from localStorage
const storedToken = localStorage.getItem('cyber_token');
const storedUser = localStorage.getItem('cyber_user');
if (storedToken && storedUser) {
  try {
    state = {
      user: JSON.parse(storedUser),
      token: storedToken,
      isAuthenticated: true,
      isLoading: false,
    };
  } catch (e) {
    localStorage.removeItem('cyber_token');
    localStorage.removeItem('cyber_user');
  }
} else {
  state.isLoading = false;
}

export const authStore = {
  getState: () => state,
  setUser: (user, token) => {
    state = {
      ...state,
      user,
      token,
      isAuthenticated: !!user,
      isLoading: false,
    };
    if (token) localStorage.setItem('cyber_token', token);
    if (user) localStorage.setItem('cyber_user', JSON.stringify(user));
    listeners.forEach((l) => l(state));
  },
  logout: () => {
    localStorage.removeItem('cyber_token');
    localStorage.removeItem('cyber_user');
    state = {
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
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
