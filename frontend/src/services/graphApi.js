import apiClient, { ENABLE_MOCK_FALLBACK } from './api';
import { MOCK_GRAPH_DATA } from './mockData';

export const graphApi = {
  getGraph: async () => {
    try {
      const data = await apiClient.get('/graph');
      return data;
    } catch (error) {
      if (ENABLE_MOCK_FALLBACK) {
        return MOCK_GRAPH_DATA;
      }
      throw error;
    }
  },

  getNodes: async () => {
    try {
      const data = await apiClient.get('/graph/nodes');
      return data;
    } catch (error) {
      if (ENABLE_MOCK_FALLBACK) {
        return MOCK_GRAPH_DATA.nodes;
      }
      throw error;
    }
  },

  getEdges: async () => {
    try {
      const data = await apiClient.get('/graph/edges');
      return data;
    } catch (error) {
      if (ENABLE_MOCK_FALLBACK) {
        return MOCK_GRAPH_DATA.edges;
      }
      throw error;
    }
  },

  getNodeById: async (id) => {
    try {
      const data = await apiClient.get(`/graph/node/${id}`);
      return data;
    } catch (error) {
      if (ENABLE_MOCK_FALLBACK) {
        const node = MOCK_GRAPH_DATA.nodes.find((n) => n.id.toLowerCase() === id.toLowerCase());
        if (node) return node;
        return {
          id,
          label: id,
          type: 'server',
          ip: '192.168.1.50',
          status: 'Normal',
          risk: 'LOW',
          anomaly_score: 0.15,
          connections: 5,
          alerts: 0,
          os: 'Linux Enterprise',
          mac: '00:50:56:C0:00:08',
          zone: 'General Internal',
        };
      }
      throw error;
    }
  },
};
