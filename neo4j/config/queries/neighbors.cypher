// ============================================
// NEIGHBOR QUERIES
// ============================================

// Get direct neighbors of a node
// Parameters: { node_id, relationship_type?, direction? }
MATCH (n:Node {id: $node_id})
MATCH (n)-[r]-(neighbor)
WHERE $relationship_type IS NULL OR type(r) = $relationship_type
  AND ($direction IS NULL OR 
       ($direction = 'outgoing' AND startNode(r) = n) OR
       ($direction = 'incoming' AND endNode(r) = n))
RETURN 
    neighbor,
    type(r) as relationship_type,
    r as relationship,
    CASE WHEN startNode(r) = n THEN 'outgoing' ELSE 'incoming' END as direction

// Get neighbors with relationship count
// Parameters: { node_id, min_count? }
MATCH (n:Node {id: $node_id})
MATCH (n)-[r]-(neighbor)
WITH neighbor, COUNT(r) as relationship_count
WHERE $min_count IS NULL OR relationship_count >= $min_count
RETURN 
    neighbor,
    relationship_count
ORDER BY relationship_count DESC

// Get common neighbors between two nodes
// Parameters: { node1_id, node2_id }
MATCH (n1:Node {id: $node1_id})
MATCH (n2:Node {id: $node2_id})
MATCH (n1)-[:CONNECTS_TO]-(common)-[:CONNECTS_TO]-(n2)
RETURN common

// Get neighbors by degree
// Parameters: { node_id }
MATCH (n:Node {id: $node_id})
MATCH (n)-[r]-(neighbor)
WITH neighbor, COUNT(r) as degree
RETURN 
    neighbor,
    degree
ORDER BY degree DESC

// Get isolated nodes (no relationships)
MATCH (n:Node)
WHERE NOT (n)-[]-()
RETURN n

// Get neighbor count per node
// Parameters: { limit? }
MATCH (n:Node)
OPTIONAL MATCH (n)-[r]-()
RETURN 
    n.id as node_id,
    n.hostname as hostname,
    COUNT(DISTINCT r) as neighbor_count
ORDER BY neighbor_count DESC
LIMIT $limit

// Get neighbors with specific property
// Parameters: { node_id, property_key, property_value }
MATCH (n:Node {id: $node_id})
MATCH (n)-[r]-(neighbor)
WHERE neighbor[$property_key] = $property_value
RETURN neighbors