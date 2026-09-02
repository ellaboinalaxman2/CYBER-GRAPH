import apiClient, { ENABLE_MOCK_FALLBACK } from './api';
import { MOCK_ALERTS } from './mockData';

export const alertApi = {
  getAlerts: async (params = {}) => {
    try {
      const data = await apiClient.get('/alerts', { params });
      return data;
    } catch (error) {
      if (ENABLE_MOCK_FALLBACK) {
        let list = [...MOCK_ALERTS];
        if (params.severity && params.severity !== 'ALL') {
          list = list.filter((a) => a.severity.toUpperCase() === params.severity.toUpperCase());
        }
        if (params.status && params.status !== 'ALL') {
          list = list.filter((a) => a.status.toUpperCase() === params.status.toUpperCase());
        }
        if (params.search) {
          const s = params.search.toLowerCase();
          list = list.filter(
            (a) =>
              a.title.toLowerCase().includes(s) ||
              a.source.toLowerCase().includes(s) ||
              a.destination.toLowerCase().includes(s) ||
              a.technique.toLowerCase().includes(s)
          );
        }
        return { alerts: list, total: list.length };
      }
      throw error;
    }
  },

  getAlertById: async (id) => {
    try {
      const data = await apiClient.get(`/alerts/${id}`);
      return data;
    } catch (error) {
      if (ENABLE_MOCK_FALLBACK) {
        const alert = MOCK_ALERTS.find((a) => a.id.toLowerCase() === id.toLowerCase());
        return alert || MOCK_ALERTS[0];
      }
      throw error;
    }
  },

  updateAlertStatus: async (id, status) => {
    try {
      const data = await apiClient.put(`/alerts/${id}/status`, { status });
      return data;
    } catch (error) {
      if (ENABLE_MOCK_FALLBACK) {
        return { success: true, id, status };
      }
      throw error;
    }
  },
};
