// ============================================
// INDEXES FOR PERFORMANCE
// ============================================

// Index on node type for faster filtering
CREATE INDEX node_type_idx IF NOT EXISTS
FOR (n:Node)
ON (n.type);

// Index on node status
CREATE INDEX node_status_idx IF NOT EXISTS
FOR (n:Node)
ON (n.status);

// Index on node criticality
CREATE INDEX node_criticality_idx IF NOT EXISTS
FOR (n:Node)
ON (n.criticality);

// Index on node hostname
CREATE INDEX node_hostname_idx IF NOT EXISTS
FOR (n:Node)
ON (n.hostname);

// Index on node IP address
CREATE INDEX node_ip_idx IF NOT EXISTS
FOR (n:Node)
ON (n.ip_address);

// Index on relationship type
CREATE INDEX relationship_type_idx IF NOT EXISTS
FOR ()-[r:RELATIONSHIP]-()
ON (r.type);

// Index on relationship timestamp
CREATE INDEX relationship_timestamp_idx IF NOT EXISTS
FOR ()-[r:RELATIONSHIP]-()
ON (r.timestamp);

// Index on relationship protocol
CREATE INDEX relationship_protocol_idx IF NOT EXISTS
FOR ()-[r:RELATIONSHIP]-()
ON (r.protocol);

// Index on alert risk score
CREATE INDEX alert_risk_score_idx IF NOT EXISTS
FOR (n:Node {type: 'ALERT'})
ON (n.risk_score);

// Index on alert severity
CREATE INDEX alert_severity_idx IF NOT EXISTS
FOR (n:Node {type: 'ALERT'})
ON (n.severity);

// Composite index for node type and status
CREATE INDEX node_type_status_idx IF NOT EXISTS
FOR (n:Node)
ON (n.type, n.status);

// Composite index for relationship type and confidence
CREATE INDEX relationship_type_confidence_idx IF NOT EXISTS
FOR ()-[r:RELATIONSHIP]-()
ON (r.type, r.confidence);

// Index on node created_at for time-based queries
CREATE INDEX node_created_at_idx IF NOT EXISTS
FOR (n:Node)
ON (n.created_at);

// Index on node updated_at for time-based queries
CREATE INDEX node_updated_at_idx IF NOT EXISTS
FOR (n:Node)
ON (n.updated_at);

// Index on relationship created_at
CREATE INDEX relationship_created_at_idx IF NOT EXISTS
FOR ()-[r:RELATIONSHIP]-()
ON (r.created_at);

// Index on node metadata (if using JSON)
CREATE INDEX node_metadata_idx IF NOT EXISTS
FOR (n:Node)
ON (n.metadata);

// Index for full-text search on node properties
CREATE FULLTEXT INDEX node_fulltext_idx IF NOT EXISTS
FOR (n:Node)
ON EACH [n.name, n.hostname, n.ip_address, n.description];