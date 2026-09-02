import { useState, useEffect, useCallback } from 'react';
import { alertApi } from '../services/alertApi';
import { alertStore } from '../store/alertStore';

export function useAlerts(initialFilters = {}) {
  const [alerts, setAlerts] = useState(alertStore.getState().alerts);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState(initialFilters);

  useEffect(() => {
    const unsub = alertStore.subscribe((state) => {
      setAlerts(state.alerts);
    });
    return () => unsub();
  }, []);

  const fetchAlerts = useCallback(async (customParams) => {
    setLoading(true);
    setError(null);
    try {
      const res = await alertApi.getAlerts(customParams || filters);
      alertStore.setAlerts(res.alerts || []);
      setTotal(res.total || 0);
    } catch (err) {
      setError(err.message || 'Failed to fetch alerts');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  const updateStatus = async (id, status) => {
    try {
      await alertApi.updateAlertStatus(id, status);
      alertStore.updateAlertStatus(id, status);
    } catch (err) {
      console.error('Failed to update alert status', err);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [fetchAlerts]);

  return {
    alerts,
    total,
    loading,
    error,
    filters,
    setFilters,
    updateStatus,
    refetch: fetchAlerts,
  };
}

export default useAlerts;
