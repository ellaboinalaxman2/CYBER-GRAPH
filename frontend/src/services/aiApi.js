import apiClient, { ENABLE_MOCK_FALLBACK } from './api';
import { MOCK_ATTACKS } from './mockData';

export const aiApi = {
  getNodePrediction: async (nodeId) => {
    try {
      const data = await apiClient.get(`/ai/prediction/${nodeId}`);
      return data;
    } catch (error) {
      if (ENABLE_MOCK_FALLBACK) {
        if (nodeId === 'SERVER-01' || nodeId === 'PC-01' || nodeId === 'DB-01') {
          return {
            nodeId,
            prediction: 'ATTACK',
            anomaly_score: nodeId === 'SERVER-01' ? 0.94 : 0.88,
            confidence: 0.93,
            model: 'GraphSAGE v2.4 (Member 3 AI Engine)',
            explanations: [
              'Unusual login activity (Spike in failed auth within 60s)',
              'Abnormal connection pattern (Direct leap to internal database)',
              'Suspicious neighboring node compromise cascade',
            ],
            features: {
              degreeCentrality: 0.82,
              inDegree: 14,
              outDegree: 9,
              entropyScore: 3.84,
            },
          };
        }
        return {
          nodeId,
          prediction: 'BENIGN',
          anomaly_score: 0.08,
          confidence: 0.97,
          model: 'GraphSAGE v2.4 (Member 3 AI Engine)',
          explanations: ['Normal baseline network interaction observed.'],
          features: {
            degreeCentrality: 0.15,
            inDegree: 2,
            outDegree: 1,
            entropyScore: 0.42,
          },
        };
      }
      throw error;
    }
  },

  getModelStatus: async () => {
    try {
      const data = await apiClient.get('/ai/model-status');
      return data;
    } catch (error) {
      if (ENABLE_MOCK_FALLBACK) {
        return {
          status: 'ACTIVE_INFERENCE',
          modelName: 'GraphSAGE-CyberGNN',
          version: '2.4.1',
          lastTrained: '2026-08-30T18:00:00Z',
          accuracy: 0.984,
          f1Score: 0.962,
          latencyMs: 14,
          connectedTo: 'Member 3 (AI Engine)',
        };
      }
      throw error;
    }
  },
};
