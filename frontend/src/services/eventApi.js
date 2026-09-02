import apiClient, { ENABLE_MOCK_FALLBACK } from './api';
import { MOCK_EVENTS } from './mockData';

export const eventApi = {
  getEvents: async (params = {}) => {
    try {
      const data = await apiClient.get('/events', { params });
      return data;
    } catch (error) {
      if (ENABLE_MOCK_FALLBACK) {
        let list = [...MOCK_EVENTS];
        if (params.status && params.status !== 'ALL') {
          list = list.filter((e) => e.status.toLowerCase() === params.status.toLowerCase());
        }
        if (params.search) {
          const s = params.search.toLowerCase();
          list = list.filter(
            (e) =>
              e.id.toLowerCase().includes(s) ||
              e.source.toLowerCase().includes(s) ||
              e.destination.toLowerCase().includes(s) ||
              e.event.toLowerCase().includes(s) ||
              e.sourceIp.includes(s) ||
              e.destIp.includes(s)
          );
        }
        return { events: list, total: list.length };
      }
      throw error;
    }
  },

  getEventById: async (id) => {
    try {
      const data = await apiClient.get(`/events/${id}`);
      return data;
    } catch (error) {
      if (ENABLE_MOCK_FALLBACK) {
        const found = MOCK_EVENTS.find((e) => e.id.toLowerCase() === id.toLowerCase());
        if (found) return found;
        return MOCK_EVENTS[0];
      }
      throw error;
    }
  },
};
