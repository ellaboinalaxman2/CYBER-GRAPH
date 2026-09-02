import React, { createContext, useContext, useState, useEffect } from "react";
import { authApi } from "../services/authApi";
import { authStore } from "../store/authStore";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(authStore.getState().user);
  const [token, setToken] = useState(authStore.getState().token);
  const [isAuthenticated, setIsAuthenticated] = useState(
    authStore.getState().isAuthenticated,
  );
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = authStore.subscribe((state) => {
      setUser(state.user);
      setToken(state.token);
      setIsAuthenticated(state.isAuthenticated);
    });

    const currentToken = localStorage.getItem("cyber_token");
    if (!currentToken) {
      authStore.logout();
      setLoading(false);
      return () => unsubscribe();
    }

    // Check existing session
    authApi
      .getCurrentUser()
      .then((res) => {
        if (res?.user) {
          authStore.setUser(res.user, currentToken);
        } else {
          authStore.logout();
        }
      })
      .catch(() => {
        authStore.logout();
      })
      .finally(() => {
        setLoading(false);
      });

    return () => unsubscribe();
  }, []);

  const login = async (credentials) => {
    setLoading(true);
    try {
      const res = await authApi.login(credentials);
      if (res?.user && res?.token) {
        authStore.setUser(res.user, res.token);
        return res;
      }
      throw new Error("Invalid response");
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    setLoading(true);
    try {
      const res = await authApi.register(userData);
      if (res?.user && res?.token) {
        authStore.setUser(res.user, res.token);
        return res;
      }
      throw new Error("Registration failed");
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    await authApi.logout();
    authStore.logout();
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated,
        loading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuthContext = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuthContext must be used within an AuthProvider");
  }
  return context;
};

export default AuthContext;
