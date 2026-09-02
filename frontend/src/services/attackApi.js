import apiClient, { ENABLE_MOCK_FALLBACK } from './api';
import { MOCK_ATTACKS } from './mockData';

export const attackApi = {
  getAttacks: async () => {
    try {
      const data = await apiClient.get('/attacks');
      return data;
    } catch (error) {
      if (ENABLE_MOCK_FALLBACK) {
        return MOCK_ATTACKS;
      }
      throw error;
    }
  },

  getAttackById: async (id) => {
    try {
      const data = await apiClient.get(`/attacks/${id}`);
      return data;
    } catch (error) {
      if (ENABLE_MOCK_FALLBACK) {
        const found = MOCK_ATTACKS.find((a) => a.id.toLowerCase() === id.toLowerCase());
        return found || MOCK_ATTACKS[0];
      }
      throw error;
    }
  },

  getAttackTimeline: async (id) => {
    try {
      const data = await apiClient.get(`/attacks/${id}/timeline`);
      return data;
    } catch (error) {
      if (ENABLE_MOCK_FALLBACK) {
        const found = MOCK_ATTACKS.find((a) => a.id.toLowerCase() === id.toLowerCase()) || MOCK_ATTACKS[0];
        return found.timeline;
      }
      throw error;
    }
  },

  getAttackPath: async (id) => {
    try {
      const data = await apiClient.get(`/attacks/${id}/path`);
      return data;
    } catch (error) {
      if (ENABLE_MOCK_FALLBACK) {
        const found = MOCK_ATTACKS.find((a) => a.id.toLowerCase() === id.toLowerCase()) || MOCK_ATTACKS[0];
        return {
          path: found.path,
          nodeIds: found.nodeIds,
          edgeIds: found.edgeIds,
        };
      }
      throw error;
    }
  },
};
