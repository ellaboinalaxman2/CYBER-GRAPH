// ============================================
// NODE OPERATIONS
// ============================================

// Create a node
// Parameters: { id, type, name, hostname, ip_address, ... }
CREATE (n:Node {
    id: $id,
    type: $type,
    name: $name,
    hostname: $hostname,
    ip_address: $ip_address,
    os: $os,
    os_version: $os_version,
    status: $status,
    criticality: $criticality,
    description: $description,
    metadata: $metadata,
    created_at: datetime(),
    updated_at: datetime()
})
RETURN n

// Find a node by ID
// Parameters: { id }
MATCH (n:Node {id: $id})
RETURN n

// Find a node by hostname
// Parameters: { hostname }
MATCH (n:Node {hostname: $hostname})
RETURN n

// Find a node by IP address
// Parameters: { ip_address }
MATCH (n:Node {ip_address: $ip_address})
RETURN n

// Find nodes by type
// Parameters: { type, limit, skip }
MATCH (n:Node {type: $type})
RETURN n
SKIP $skip
LIMIT $limit

// Find all nodes
// Parameters: { limit, skip }
MATCH (n:Node)
RETURN n
SKIP $skip
LIMIT $limit

// Update a node
// Parameters: { id, updates }
MATCH (n:Node {id: $id})
SET n += $updates,
    n.updated_at = datetime()
RETURN n

// Delete a node
// Parameters: { id }
MATCH (n:Node {id: $id})
DETACH DELETE n

// Find connected nodes
// Parameters: { id }
MATCH (n:Node {id: $id})-[r]-(connected)
RETURN n, connected, type(r) as relationship_type

// Get node count
// Parameters: { type? }
MATCH (n:Node)
WHERE $type IS NULL OR n.type = $type
RETURN COUNT(n) as count

// Get node by criticality
// Parameters: { min_criticality, max_criticality }
MATCH (n:Node)
WHERE n.criticality >= $min_criticality
  AND n.criticality <= $max_criticality
RETURN n
ORDER BY n.criticality DESC