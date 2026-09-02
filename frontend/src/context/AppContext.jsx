import React, { createContext, useContext, useState, useEffect } from 'react';
import { appStore } from '../store/appStore';

const AppContext = createContext(null);

export const AppProvider = ({ children }) => {
  const [appState, setAppState] = useState(appStore.getState());

  useEffect(() => {
    const unsubscribe = appStore.subscribe((state) => {
      setAppState(state);
    });
    return () => unsubscribe();
  }, []);

  const toggleSidebar = () => appStore.toggleSidebar();
  const setSidebarOpen = (open) => appStore.setSidebarOpen(open);
  const notify = (msg) => appStore.addNotification(msg);
  const clearNotifications = () => appStore.clearNotifications();

  return (
    <AppContext.Provider
      value={{
        ...appState,
        toggleSidebar,
        setSidebarOpen,
        notify,
        clearNotifications,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
};

export default AppContext;
