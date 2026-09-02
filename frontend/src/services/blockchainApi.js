import apiClient, { ENABLE_MOCK_FALLBACK } from './api';
import { MOCK_BLOCKCHAIN_AUDIT_TRAIL } from './mockData';

export const blockchainApi = {
  verifyEvent: async (eventId) => {
    try {
      const data = await apiClient.get(`/blockchain/verify/${eventId}`);
      return data;
    } catch (error) {
      if (ENABLE_MOCK_FALLBACK) {
        const found = MOCK_BLOCKCHAIN_AUDIT_TRAIL.find(
          (b) => b.eventId.toLowerCase() === eventId.toLowerCase()
        );
        if (found) {
          return {
            event_id: found.eventId,
            verified: true,
            status: 'VERIFIED',
            transaction_hash: found.txHash,
            block_number: found.blockNumber,
            timestamp: found.timestamp,
            raw_hash: found.hash,
            ledger_network: 'CyberGraph-Permissioned-PoA',
          };
        }
        return {
          event_id: eventId,
          verified: false,
          status: 'NOT_VERIFIED',
          transaction_hash: null,
          block_number: null,
          timestamp: null,
        };
      }
      throw error;
    }
  },

  getAuditTrail: async (params = {}) => {
    try {
      const data = await apiClient.get('/blockchain/audit-trail', { params });
      return data;
    } catch (error) {
      if (ENABLE_MOCK_FALLBACK) {
        let list = [...MOCK_BLOCKCHAIN_AUDIT_TRAIL];
        if (params.search) {
          const s = params.search.toLowerCase();
          list = list.filter(
            (item) =>
              item.eventId.toLowerCase().includes(s) ||
              item.txHash.toLowerCase().includes(s) ||
              item.hash.toLowerCase().includes(s)
          );
        }
        return { auditTrail: list, total: list.length };
      }
      throw error;
    }
  },

  getBlockchainStatus: async () => {
    try {
      const data = await apiClient.get('/blockchain/status');
      return data;
    } catch (error) {
      if (ENABLE_MOCK_FALLBACK) {
        return {
          network: 'CyberGraph Sovereign Chain',
          consensus: 'Proof of Authority (PoA)',
          currentBlock: 1849220,
          verifiedEventsTotal: 14248,
          integrityRate: '100%',
          avgConfirmationSec: 0.8,
          connectedTo: 'Member 6 (Blockchain)',
        };
      }
      throw error;
    }
  },
};
