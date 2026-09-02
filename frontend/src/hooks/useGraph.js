import { useEffect } from 'react';
import { useGraphContext } from '../context/GraphContext';

export function useGraph(autoFetch = true) {
  const context = useGraphContext();

  useEffect(() => {
    if (autoFetch && context.nodes.length === 0 && !context.loading) {
      context.fetchGraph();
    }
  }, [autoFetch, context]);

  return context;
}

export default useGraph;
