import { useState, useEffect, useCallback } from 'react';
import { blockchainApi } from '../services/blockchainApi';

export function useBlockchain() {
  const [auditTrail, setAuditTrail] = useState([]);
  const [blockchainStatus, setBlockchainStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchAuditTrail = useCallback(async (params) => {
    setLoading(true);
    setError(null);
    try {
      const data = await blockchainApi.getAuditTrail(params);
      setAuditTrail(data.auditTrail || []);
    } catch (err) {
      setError(err.message || 'Failed to load blockchain audit trail');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchStatus = useCallback(async () => {
    try {
      const status = await blockchainApi.getBlockchainStatus();
      setBlockchainStatus(status);
    } catch (err) {
      console.error('Failed to get blockchain status', err);
    }
  }, []);

  const verifyEvent = async (eventId) => {
    try {
      return await blockchainApi.verifyEvent(eventId);
    } catch (err) {
      console.error('Event verification error', err);
      return { event_id: eventId, verified: false, status: 'VERIFICATION_FAILED' };
    }
  };

  useEffect(() => {
    fetchAuditTrail();
    fetchStatus();
  }, [fetchAuditTrail, fetchStatus]);

  return {
    auditTrail,
    blockchainStatus,
    loading,
    error,
    verifyEvent,
    refetch: fetchAuditTrail,
  };
}

export default useBlockchain;
