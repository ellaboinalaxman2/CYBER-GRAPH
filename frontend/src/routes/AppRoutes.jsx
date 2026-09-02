import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from './ProtectedRoute';
import PublicRoute from './PublicRoute';

// Page Imports
import Login from '../pages/Login';
import Register from '../pages/Register';
import Dashboard from '../pages/Dashboard';
import CyberGraphPage from '../pages/CyberGraph';
import Alerts from '../pages/Alerts';
import Attacks from '../pages/Attacks';
import AttackDetailsPage from '../pages/AttackDetails';
import Events from '../pages/Events';
import NodeDetailsPage from '../pages/NodeDetails';
import BlockchainAudit from '../pages/BlockchainAudit';
import Settings from '../pages/Settings';
import NotFound from '../pages/NotFound';

export const AppRoutes = () => {
  return (
    <Routes>
      {/* Public Routes */}
      <Route
        path="/login"
        element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        }
      />
      <Route
        path="/register"
        element={
          <PublicRoute>
            <Register />
          </PublicRoute>
        }
      />

      {/* Protected Operations Routes */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Navigate to="/dashboard" replace />
          </ProtectedRoute>
        }
      />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/graph"
        element={
          <ProtectedRoute>
            <CyberGraphPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/alerts"
        element={
          <ProtectedRoute>
            <Alerts />
          </ProtectedRoute>
        }
      />
      <Route
        path="/attacks"
        element={
          <ProtectedRoute>
            <Attacks />
          </ProtectedRoute>
        }
      />
      <Route
        path="/attacks/:id"
        element={
          <ProtectedRoute>
            <AttackDetailsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/events"
        element={
          <ProtectedRoute>
            <Events />
          </ProtectedRoute>
        }
      />
      <Route
        path="/nodes/:id"
        element={
          <ProtectedRoute>
            <NodeDetailsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/blockchain"
        element={
          <ProtectedRoute>
            <BlockchainAudit />
          </ProtectedRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <Settings />
          </ProtectedRoute>
        }
      />

      {/* Catch-all 404 */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
};

export default AppRoutes;
