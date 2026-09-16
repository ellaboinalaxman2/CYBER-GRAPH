// ============================================
// RELATIONSHIP OPERATIONS
// ============================================

// Create a relationship
// Parameters: { source_id, target_id, type, properties }
MATCH (source:Node {id: $source_id})
MATCH (target:Node {id: $target_id})
CREATE (source)-[r:RELATIONSHIP {
    type: $type,
    protocol: $protocol,
    port: $port,
    timestamp: $timestamp,
    metadata: $metadata,
    created_at: datetime()
}]->(target)
SET r += $properties
RETURN r

// Find relationships for a node
// Parameters: { node_id, direction? }
MATCH (n:Node {id: $node_id})
MATCH (n)-[r]-(connected)
RETURN n, r, connected
WHERE $direction IS NULL OR type(r) = $direction

// Find specific relationship
// Parameters: { source_id, target_id, type? }
MATCH (source:Node {id: $source_id})-[r]-(target:Node {id: $target_id})
WHERE $type IS NULL OR type(r) = $type
RETURN r

// Update relationship
// Parameters: { source_id, target_id, updates }
MATCH (source:Node {id: $source_id})-[r]-(target:Node {id: $target_id})
SET r += $updates
RETURN r

// Delete relationship
// Parameters: { source_id, target_id }
MATCH (source:Node {id: $source_id})-[r]-(target:Node {id: $target_id})
DELETE r

// Get relationship types
// Parameters: { node_id? }
MATCH (n:Node)-[r]->()
WHERE $node_id IS NULL OR n.id = $node_id
RETURN DISTINCT type(r) as relationship_type, COUNT(r) as count
ORDER BY count DESC

// Get relationship frequency
// Parameters: { node_id }
MATCH (n:Node {id: $node_id})-[r]-()
RETURN type(r) as relationship_type, COUNT(r) as count
ORDER BY count DESC

// Find shortest path between two nodes
// Parameters: { source_id, target_id }
MATCH (source:Node {id: $source_id})
MATCH (target:Node {id: $target_id})
MATCH path = shortestPath((source)-[*]-(target))
RETURN path

// Find all paths between two nodes
// Parameters: { source_id, target_id, max_depth? }
MATCH (source:Node {id: $source_id})
MATCH (target:Node {id: $target_id})
MATCH path = (source)-[*1..$max_depth]-(target)
WHERE $max_depth IS NULL OR length(path) <= $max_depth
RETURN path
ORDER BY length(path) ASC