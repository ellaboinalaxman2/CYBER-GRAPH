import { useState, useEffect, useCallback } from 'react';
import { attackApi } from '../services/attackApi';

export function useAttacks() {
  const [attacks, setAttacks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchAttacks = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await attackApi.getAttacks();
      setAttacks(data || []);
    } catch (err) {
      setError(err.message || 'Failed to fetch attacks');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAttacks();
  }, [fetchAttacks]);

  return {
    attacks,
    loading,
    error,
    refetch: fetchAttacks,
  };
}

export default useAttacks;
