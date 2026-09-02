import { useState, useEffect, useCallback } from 'react';
import { aiApi } from '../services/aiApi';

export function useAI(nodeId = null) {
  const [prediction, setPrediction] = useState(null);
  const [modelStatus, setModelStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchPrediction = useCallback(async (id) => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const data = await aiApi.getNodePrediction(id);
      setPrediction(data);
    } catch (err) {
      setError(err.message || 'Failed to fetch AI prediction');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchModelStatus = useCallback(async () => {
    try {
      const status = await aiApi.getModelStatus();
      setModelStatus(status);
    } catch (err) {
      console.error('Failed to load AI model status', err);
    }
  }, []);

  useEffect(() => {
    fetchModelStatus();
  }, [fetchModelStatus]);

  useEffect(() => {
    if (nodeId) {
      fetchPrediction(nodeId);
    }
  }, [nodeId, fetchPrediction]);

  return {
    prediction,
    modelStatus,
    loading,
    error,
    fetchPrediction,
    fetchModelStatus,
  };
}

export default useAI;
