import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { graphApi } from '../services/graphApi';
import { graphStore } from '../store/graphStore';

const GraphContext = createContext(null);

export const GraphProvider = ({ children }) => {
  const [graphState, setGraphState] = useState(graphStore.getState());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const unsubscribe = graphStore.subscribe((state) => {
      setGraphState(state);
    });
    return () => unsubscribe();
  }, []);

  const fetchGraph = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await graphApi.getGraph();
      graphStore.setState({
        nodes: data.nodes || [],
        edges: data.edges || [],
        loading: false,
      });
    } catch (err) {
      setError(err.message || 'Failed to load cyber graph data');
    } finally {
      setLoading(false);
    }
  }, []);

  const selectNode = (node) => {
    graphStore.setSelectedNode(node);
  };

  const setAttackPath = (path) => {
    graphStore.setActiveAttackPath(path);
  };

  const updateFilters = (filters) => {
    graphStore.setFilters(filters);
  };

  const resetAllFilters = () => {
    graphStore.resetFilters();
  };

  return (
    <GraphContext.Provider
      value={{
        ...graphState,
        loading,
        error,
        fetchGraph,
        selectNode,
        setAttackPath,
        updateFilters,
        resetAllFilters,
      }}
    >
      {children}
    </GraphContext.Provider>
  );
};

export const useGraphContext = () => {
  const context = useContext(GraphContext);
  if (!context) {
    throw new Error('useGraphContext must be used within a GraphProvider');
  }
  return context;
};

export default GraphContext;
