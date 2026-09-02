import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { GraphProvider } from './context/GraphContext';
import { AppProvider } from './context/AppContext';
import AppRoutes from './routes/AppRoutes';

export function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <GraphProvider>
          <AppProvider>
            <AppRoutes />
          </AppProvider>
        </GraphProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
