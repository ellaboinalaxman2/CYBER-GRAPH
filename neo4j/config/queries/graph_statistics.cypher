// ============================================
// GRAPH STATISTICS QUERIES
// ============================================

// Get basic graph statistics
CALL {
    MATCH (n) RETURN COUNT(n) as total_nodes
}
CALL {
    MATCH ()-[r]->() RETURN COUNT(r) as total_relationships
}
CALL {
    MATCH (n) RETURN AVG(COUNT { (n)-[]-() }) as avg_degree
}
RETURN 
    total_nodes,
    total_relationships,
    avg_degree

// Get node statistics by type
MATCH (n:Node)
RETURN 
    n.type as node_type,
    COUNT(n) as count,
    AVG(n.criticality) as avg_criticality,
    SUM(CASE WHEN n.status = 'active' THEN 1 ELSE 0 END) as active_count,
    SUM(CASE WHEN n.status = 'inactive' THEN 1 ELSE 0 END) as inactive_count
ORDER BY count DESC

// Get relationship statistics by type
MATCH ()-[r]->()
RETURN 
    type(r) as relationship_type,
    COUNT(r) as count,
    COUNT(DISTINCT startNode(r)) as source_nodes,
    COUNT(DISTINCT endNode(r)) as target_nodes,
    MIN(r.confidence) as min_confidence,
    MAX(r.confidence) as max_confidence,
    AVG(r.confidence) as avg_confidence
ORDER BY count DESC

// Get degree distribution
MATCH (n:Node)
WITH n, COUNT { (n)-[]-() } as degree
RETURN 
    degree,
    COUNT(n) as node_count
ORDER BY degree DESC

// Get network diameter (approximate)
MATCH (n:Node)
MATCH path = shortestPath((n)-[*]-(m))
WHERE n.id <> m.id
RETURN MAX(length(path)) as diameter

// Get connected components
CALL gds.graph.project('graph', 'Node', 'RELATIONSHIP')
CALL gds.wcc.stats('graph')
YIELD componentCount, componentDistribution
RETURN componentCount, componentDistribution
// Note: Requires Graph Data Science plugin

// Get top connected nodes
MATCH (n:Node)
WITH n, COUNT { (n)-[]-() } as degree
WHERE degree > 0
RETURN 
    n.id as node_id,
    n.hostname as hostname,
    n.type as node_type,
    degree as connection_count
ORDER BY degree DESC
LIMIT 20

// Get vulnerability score (high criticality + high connections)
MATCH (n:Node)
WITH n, 
    n.criticality as criticality,
    COUNT { (n)-[]-() } as connection_count
WHERE criticality > 3
RETURN 
    n.id as node_id,
    n.hostname as hostname,
    criticality,
    connection_count,
    criticality * connection_count as vulnerability_score
ORDER BY vulnerability_score DESC
LIMIT 20

// Get graph density
MATCH (n:Node)
WITH COUNT(n) as node_count
MATCH ()-[r]->()
WITH node_count, COUNT(r) as relationship_count
RETURN 
    node_count,
    relationship_count,
    CASE 
        WHEN node_count > 1 THEN 
            (2.0 * relationship_count) / (node_count * (node_count - 1))
        ELSE 0 
    END as density

// Get suspicious subgraphs
// Parameters: { min_risk, max_depth? }
MATCH path = (n)-[*1..$max_depth]-(m)
WHERE ANY(n IN nodes(path) WHERE n.risk_score > $min_risk)
  AND $max_depth IS NULL OR length(path) <= $max_depth
WITH COLLECT(path) as paths
UNWIND paths as path
RETURN 
    [node IN nodes(path) | node.id] as path_nodes,
    length(path) as path_length,
    REDUCE(s = 0, n IN nodes(path) | s + n.risk_score) as total_risk
ORDER BY total_risk DESC
LIMIT 10