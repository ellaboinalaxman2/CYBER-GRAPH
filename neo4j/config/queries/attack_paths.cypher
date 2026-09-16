// ============================================
// ATTACK PATH RECONSTRUCTION QUERIES
// ============================================

// Find potential attack paths from source to target
// Parameters: { source_id, target_id, max_depth? }
MATCH (source:Node {id: $source_id})
MATCH (target:Node {id: $target_id})
MATCH path = (source)-[*1..$max_depth]-(target)
WHERE $max_depth IS NULL OR length(path) <= $max_depth
  AND ALL(n IN nodes(path) WHERE n.status <> 'inactive')
RETURN 
    nodes(path) as path_nodes,
    relationships(path) as path_relationships,
    length(path) as path_length,
    [node IN nodes(path) | node.id] as node_ids,
    [node IN nodes(path) | node.type] as node_types
ORDER BY length(path) ASC

// Find all suspicious paths (using anomaly score)
// Parameters: { min_anomaly_score, max_depth? }
MATCH path = (source)-[*1..$max_depth]-(target)
WHERE $max_depth IS NULL OR length(path) <= $max_depth
  AND ANY(n IN nodes(path) WHERE n.anomaly_score > $min_anomaly_score)
RETURN 
    path,
    [node IN nodes(path) | node.id] as node_ids,
    [node IN nodes(path) | node.anomaly_score] as anomaly_scores,
    length(path) as path_length,
    REDUCE(s = 0, n IN nodes(path) | s + n.criticality) as total_criticality
ORDER BY total_criticality DESC

// Find lateral movement paths
// Parameters: { source_id, min_connections? }
MATCH (source:Node {id: $source_id})
MATCH path = (source)-[:CONNECTS_TO|:COMMUNICATES_WITH*]-(target)
WHERE $min_connections IS NULL OR length(path) >= $min_connections
  AND ALL(n IN nodes(path) WHERE n.id <> source.id)
  AND ALL(n IN nodes(path) WHERE n.status <> 'inactive')
RETURN 
    path,
    [node IN nodes(path) | node.id] as node_ids,
    [node IN nodes(path) | node.type] as node_types,
    length(path) as hop_count,
    REDUCE(s = 0, n IN nodes(path) | s + n.criticality) as criticality_score
ORDER BY criticality_score DESC
LIMIT 50

// Find compromised nodes and their connections
// Parameters: { node_id, max_depth? }
MATCH (compromised:Node {id: $node_id})
MATCH path = (compromised)-[*1..$max_depth]-(connected)
WHERE $max_depth IS NULL OR length(path) <= $max_depth
  AND connected.status <> 'inactive'
RETURN 
    path,
    [node IN nodes(path) | node.id] as node_ids,
    [node IN nodes(path) | node.type] as node_types,
    [node IN nodes(path) | node.hostname] as hostnames,
    [rel IN relationships(path) | type(rel)] as relationship_types,
    [rel IN relationships(path) | rel.timestamp] as timestamps
ORDER BY length(path) ASC

// Find attack paths with MITRE techniques
// Parameters: { technique_id }
MATCH (technique:Node {type: 'MITRE_TECHNIQUE', technique_id: $technique_id})
MATCH (technique)<-[:MITRE_TECHNIQUE]-(alert:Node {type: 'ALERT'})
MATCH (alert)-[:RELATED_TO]-(source:Node)
MATCH path = (source)-[*1..5]-(target)
WHERE ANY(n IN nodes(path) WHERE n.id IN alert.affected_nodes)
RETURN 
    path,
    alert.id as alert_id,
    alert.attack_type as attack_type,
    [node IN nodes(path) | node.id] as node_ids,
    [node IN nodes(path) | node.hostname] as hostnames
LIMIT 20

// Find attack paths with risk score
// Parameters: { min_risk_score }
MATCH (alert:Node {type: 'ALERT'})
WHERE alert.risk_score >= $min_risk_score
MATCH (alert)-[:RELATED_TO]-(source:Node)
MATCH path = (source)-[*1..5]-(target)
RETURN 
    path,
    alert.id as alert_id,
    alert.risk_score as risk_score,
    alert.attack_type as attack_type,
    [node IN nodes(path) | node.id] as node_ids,
    [node IN nodes(path) | node.hostname] as hostnames,
    REDUCE(s = 0, n IN nodes(path) | s + n.criticality) as criticality_score
ORDER BY alert.risk_score DESC

// Find all paths from a suspicious node
// Parameters: { node_id, max_depth? }
MATCH (suspicious:Node {id: $node_id})
MATCH path = (suspicious)-[*1..$max_depth]-(target)
WHERE $max_depth IS NULL OR length(path) <= $max_depth
  AND ALL(n IN nodes(path) WHERE n.id <> suspicious.id)
RETURN 
    path,
    [node IN nodes(path) | node.id] as node_ids,
    [node IN nodes(path) | node.hostname] as hostnames,
    [node IN nodes(path) | node.type] as node_types,
    length(path) as depth,
    REDUCE(s = 0, n IN nodes(path) | s + n.criticality) as risk_score
ORDER BY depth ASC