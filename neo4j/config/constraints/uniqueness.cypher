// ============================================
// UNIQUENESS CONSTRAINTS
// ============================================

// Ensure node IDs are unique
CREATE CONSTRAINT node_id_unique IF NOT EXISTS
FOR (n:Node)
REQUIRE n.id IS UNIQUE;

// Ensure hostnames are unique (if they exist)
CREATE CONSTRAINT node_hostname_unique IF NOT EXISTS
FOR (n:Node)
REQUIRE n.hostname IS UNIQUE;

// Ensure IP addresses are unique (if they exist)
CREATE CONSTRAINT node_ip_unique IF NOT EXISTS
FOR (n:Node)
REQUIRE n.ip_address IS UNIQUE;

// Ensure unique relationship between nodes
// This prevents duplicate relationships
CREATE CONSTRAINT relationship_unique IF NOT EXISTS
FOR ()-[r:RELATIONSHIP]-()
REQUIRE (startNode(r).id, endNode(r).id, type(r)) IS UNIQUE;

// Ensure MITRE technique IDs are unique
CREATE CONSTRAINT mitre_technique_id_unique IF NOT EXISTS
FOR (n:Node {type: 'MITRE_TECHNIQUE'})
REQUIRE n.technique_id IS UNIQUE;

// Ensure alert IDs are unique
CREATE CONSTRAINT alert_id_unique IF NOT EXISTS
FOR (n:Node {type: 'ALERT'})
REQUIRE n.id IS UNIQUE;

// Ensure incident IDs are unique
CREATE CONSTRAINT incident_id_unique IF NOT EXISTS
FOR (n:Node {type: 'INCIDENT'})
REQUIRE n.id IS UNIQUE;

// Ensure node names are unique
CREATE CONSTRAINT node_name_unique IF NOT EXISTS
FOR (n:Node)
REQUIRE n.name IS UNIQUE;

// Ensure node IDs with type have proper constraints
CREATE CONSTRAINT node_type_id_unique IF NOT EXISTS
FOR (n:Node)
REQUIRE (n.id, n.type) IS UNIQUE;