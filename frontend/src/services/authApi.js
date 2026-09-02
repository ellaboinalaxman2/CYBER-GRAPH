import apiClient, { ENABLE_MOCK_FALLBACK } from "./api";
import { MOCK_USER } from "./mockData";

export const authApi = {
  login: async (credentials) => {
    try {
      const response = await apiClient.post("/auth/login", credentials);
      return response;
    } catch (error) {
      if (ENABLE_MOCK_FALLBACK) {
        // Mock successful login
        const user = {
          ...MOCK_USER,
          email: credentials.email || credentials.username || MOCK_USER.email,
        };
        localStorage.setItem("cyber_token", user.token);
        localStorage.setItem("cyber_user", JSON.stringify(user));
        return { success: true, token: user.token, user };
      }
      throw error;
    }
  },

  register: async (userData) => {
    try {
      const response = await apiClient.post("/auth/register", userData);
      return response;
    } catch (error) {
      if (ENABLE_MOCK_FALLBACK) {
        const user = {
          id: `usr_${Date.now()}`,
          name: userData.name || "Security Analyst",
          email: userData.email,
          role: userData.role || "Security Analyst",
          token: `mock-jwt-${Date.now()}`,
        };
        localStorage.setItem("cyber_token", user.token);
        localStorage.setItem("cyber_user", JSON.stringify(user));
        return { success: true, token: user.token, user };
      }
      throw error;
    }
  },

  getCurrentUser: async () => {
    const token = localStorage.getItem("cyber_token");
    if (!token) {
      return { success: false, user: null };
    }

    try {
      const response = await apiClient.get("/auth/me");
      return response;
    } catch (error) {
      if (ENABLE_MOCK_FALLBACK) {
        const storedUser = localStorage.getItem("cyber_user");
        if (storedUser) {
          return { success: true, user: JSON.parse(storedUser) };
        }
        return { success: true, user: MOCK_USER };
      }
      throw error;
    }
  },

  logout: async () => {
    try {
      await apiClient.post("/auth/logout");
    } catch (e) {
      // ignore in mock mode
    } finally {
      localStorage.removeItem("cyber_token");
      localStorage.removeItem("cyber_user");
    }
  },
};
