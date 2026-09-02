import { useState, useEffect, useCallback } from 'react';
import { eventApi } from '../services/eventApi';

export function useEvents(initialFilters = {}) {
  const [events, setEvents] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState(initialFilters);

  const fetchEvents = useCallback(async (customParams) => {
    setLoading(true);
    setError(null);
    try {
      const res = await eventApi.getEvents(customParams || filters);
      setEvents(res.events || []);
      setTotal(res.total || 0);
    } catch (err) {
      setError(err.message || 'Failed to fetch events');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  return {
    events,
    total,
    loading,
    error,
    filters,
    setFilters,
    refetch: fetchEvents,
  };
}

export default useEvents;
