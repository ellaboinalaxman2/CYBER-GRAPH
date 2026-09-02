/**
 * Transform backend graph nodes and edges into Cytoscape-compatible format
 */
export function transformToCytoscapeElements(nodes = [], edges = [], activeAttackPath = null) {
  const cyNodes = nodes.map((n) => {
    const isSuspicious = n.anomaly_score > 0.7 || n.status === 'Suspicious' || n.status === 'Compromised';
    const isInAttackPath = activeAttackPath?.nodeIds?.includes(n.id);

    return {
      group: 'nodes',
      data: {
        id: n.id,
        label: n.label || n.id,
        type: n.type || 'endpoint',
        ip: n.ip || '192.168.1.x',
        status: n.status || 'Normal',
        anomalyScore: n.anomaly_score !== undefined ? n.anomaly_score : 0,
        risk: n.risk || 'LOW',
        isSuspicious,
        isInAttackPath,
      },
    };
  });

  const cyEdges = edges.map((e, index) => {
    const edgeId = e.id || `edge-${e.source}-${e.target}-${index}`;
    const isInAttackPath =
      activeAttackPath?.edgeIds?.includes(edgeId) ||
      (activeAttackPath?.nodeIds &&
        activeAttackPath.nodeIds.includes(e.source) &&
        activeAttackPath.nodeIds.includes(e.target));

    return {
      group: 'edges',
      data: {
        id: edgeId,
        source: e.source,
        target: e.target,
        type: e.type || 'CONNECTS_TO',
        label: e.type || e.label || 'CONNECTS_TO',
        protocol: e.protocol || 'TCP',
        isInAttackPath,
      },
    };
  });

  return [...cyNodes, ...cyEdges];
}

/**
 * Filter nodes and edges based on filter criteria
 */
export function filterGraphElements(nodes, edges, filters) {
  const { nodeType, severity, searchTerm } = filters || {};

  let filteredNodes = nodes;

  if (nodeType && nodeType !== 'ALL') {
    filteredNodes = filteredNodes.filter((n) => n.type.toLowerCase() === nodeType.toLowerCase());
  }

  if (severity && severity !== 'ALL') {
    filteredNodes = filteredNodes.filter((n) => (n.risk || 'LOW').toUpperCase() === severity.toUpperCase());
  }

  if (searchTerm && searchTerm.trim() !== '') {
    const term = searchTerm.toLowerCase();
    filteredNodes = filteredNodes.filter(
      (n) => n.id.toLowerCase().includes(term) || (n.ip && n.ip.toLowerCase().includes(term))
    );
  }

  const validNodeIds = new Set(filteredNodes.map((n) => n.id));
  const filteredEdges = edges.filter((e) => validNodeIds.has(e.source) && validNodeIds.has(e.target));

  return { nodes: filteredNodes, edges: filteredEdges };
}
