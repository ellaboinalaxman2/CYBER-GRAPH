from typing import Optional, List, Dict, Any
from .base_repository import BaseNeo4jRepository

class AttackGraphRepository(BaseNeo4jRepository):
    """Repository for attack path analysis"""
    
    def find_attack_paths(self, source_id: str, target_id: str, 
                         max_depth: int = 5) -> List[Dict[str, Any]]:
        """Find potential attack paths from source to target"""
        query = """
        MATCH (source:Node {id: $source_id})
        MATCH (target:Node {id: $target_id})
        MATCH path = (source)-[*1..$max_depth]-(target)
        WHERE ALL(n IN nodes(path) WHERE n.status <> 'inactive')
        RETURN 
            nodes(path) as path_nodes,
            relationships(path) as path_relationships,
            length(path) as path_length,
            [node IN nodes(path) | node.id] as node_ids,
            [node IN nodes(path) | node.type] as node_types,
            [node IN nodes(path) | node.hostname] as hostnames,
            [node IN nodes(path) | node.criticality] as criticalities,
            REDUCE(s = 0, n IN nodes(path) | s + n.criticality) as total_criticality
        ORDER BY length(path) ASC, total_criticality DESC
        """
        return self.execute_query(query, {
            "source_id": source_id,
            "target_id": target_id,
            "max_depth": max_depth
        })
    
    def find_suspicious_paths(self, min_anomaly_score: float = 0.7, 
                              max_depth: int = 5) -> List[Dict[str, Any]]:
        """Find suspicious paths with anomaly scores"""
        query = """
        MATCH path = (source)-[*1..$max_depth]-(target)
        WHERE ANY(n IN nodes(path) WHERE n.anomaly_score > $min_anomaly_score)
        RETURN 
            [node IN nodes(path) | node.id] as node_ids,
            [node IN nodes(path) | node.type] as node_types,
            [node IN nodes(path) | node.anomaly_score] as anomaly_scores,
            length(path) as path_length,
            REDUCE(s = 0, n IN nodes(path) | s + n.criticality) as total_criticality,
            REDUCE(s = 0, n IN nodes(path) | s + n.anomaly_score) as total_anomaly
        ORDER BY total_anomaly DESC, total_criticality DESC
        LIMIT 50
        """
        return self.execute_query(query, {
            "min_anomaly_score": min_anomaly_score,
            "max_depth": max_depth
        })
    
    def find_lateral_movement_paths(self, source_id: str, 
                                   min_connections: int = 2) -> List[Dict[str, Any]]:
        """Find lateral movement paths from a source"""
        query = """
        MATCH (source:Node {id: $source_id})
        MATCH path = (source)-[:CONNECTS_TO|:COMMUNICATES_WITH*]-(target)
        WHERE length(path) >= $min_connections
          AND ALL(n IN nodes(path) WHERE n.id <> source.id)
          AND ALL(n IN nodes(path) WHERE n.status <> 'inactive')
        RETURN 
            [node IN nodes(path) | node.id] as node_ids,
            [node IN nodes(path) | node.type] as node_types,
            [node IN nodes(path) | node.hostname] as hostnames,
            length(path) as hop_count,
            REDUCE(s = 0, n IN nodes(path) | s + n.criticality) as criticality_score
        ORDER BY hop_count ASC, criticality_score DESC
        LIMIT 50
        """
        return self.execute_query(query, {
            "source_id": source_id,
            "min_connections": min_connections
        })
    
    def find_compromised_node_paths(self, node_id: str, max_depth: int = 3) -> List[Dict[str, Any]]:
        """Find paths from a compromised node"""
        query = """
        MATCH (compromised:Node {id: $node_id})
        MATCH path = (compromised)-[*1..$max_depth]-(connected)
        WHERE connected.status <> 'inactive'
        RETURN 
            [node IN nodes(path) | node.id] as node_ids,
            [node IN nodes(path) | node.type] as node_types,
            [node IN nodes(path) | node.hostname] as hostnames,
            [node IN nodes(path) | node.criticality] as criticalities,
            [rel IN relationships(path) | type(rel)] as relationship_types,
            length(path) as depth
        ORDER BY depth ASC
        """
        return self.execute_query(query, {"node_id": node_id, "max_depth": max_depth})
    
    def find_attack_paths_by_mitre(self, technique_id: str) -> List[Dict[str, Any]]:
        """Find attack paths associated with MITRE technique"""
        query = """
        MATCH (technique:Node {type: 'MITRE_TECHNIQUE', technique_id: $technique_id})
        MATCH (technique)<-[:MITRE_TECHNIQUE]-(alert:Node {type: 'ALERT'})
        MATCH (alert)-[:RELATED_TO]-(source:Node)
        MATCH path = (source)-[*1..5]-(target)
        WHERE ANY(n IN nodes(path) WHERE n.id IN alert.affected_nodes)
        RETURN 
            alert.id as alert_id,
            alert.attack_type as attack_type,
            alert.risk_score as risk_score,
            [node IN nodes(path) | node.id] as node_ids,
            [node IN nodes(path) | node.hostname] as hostnames,
            [node IN nodes(path) | node.type] as node_types,
            [rel IN relationships(path) | type(rel)] as relationship_types
        LIMIT 20
        """
        return self.execute_query(query, {"technique_id": technique_id})
    
    def find_high_risk_attack_paths(self, min_risk_score: float = 60) -> List[Dict[str, Any]]:
        """Find attack paths with high risk scores"""
        query = """
        MATCH (alert:Node {type: 'ALERT'})
        WHERE alert.risk_score >= $min_risk_score
        MATCH (alert)-[:RELATED_TO]-(source:Node)
        MATCH path = (source)-[*1..5]-(target)
        RETURN 
            alert.id as alert_id,
            alert.risk_score as risk_score,
            alert.attack_type as attack_type,
            [node IN nodes(path) | node.id] as node_ids,
            [node IN nodes(path) | node.hostname] as hostnames,
            [node IN nodes(path) | node.type] as node_types,
            REDUCE(s = 0, n IN nodes(path) | s + n.criticality) as criticality_score,
            length(path) as path_length
        ORDER BY alert.risk_score DESC, criticality_score DESC
        LIMIT 20
        """
        return self.execute_query(query, {"min_risk_score": min_risk_score})
    
    def get_attack_statistics(self) -> Dict[str, Any]:
        """Get attack statistics from the graph"""
        query = """
        CALL {
            MATCH (alert:Node {type: 'ALERT'})
            RETURN COUNT(alert) as total_alerts
        }
        CALL {
            MATCH (alert:Node {type: 'ALERT', severity: 'CRITICAL'})
            RETURN COUNT(alert) as critical_alerts
        }
        CALL {
            MATCH (alert:Node {type: 'ALERT'})
            RETURN AVG(alert.risk_score) as avg_risk_score
        }
        CALL {
            MATCH (alert:Node {type: 'ALERT'})
            WHERE alert.risk_score >= 80
            RETURN COUNT(alert) as high_risk_alerts
        }
        CALL {
            MATCH (compromised:Node {status: 'compromised'})
            RETURN COUNT(compromised) as compromised_nodes
        }
        CALL {
            MATCH (alert:Node {type: 'ALERT'})
            RETURN alert.attack_type as attack_type, COUNT(alert) as count
            ORDER BY count DESC
            LIMIT 5
        }
        RETURN 
            total_alerts,
            critical_alerts,
            high_risk_alerts,
            avg_risk_score,
            compromised_nodes
        """
        return self.execute_query_single(query)
    
    def get_attack_path_by_alert(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """Get attack path for a specific alert"""
        query = """
        MATCH (alert:Node {id: $alert_id, type: 'ALERT'})
        MATCH (alert)-[:RELATED_TO]-(source:Node)
        MATCH path = shortestPath((source)-[*]-(target))
        WHERE ANY(n IN nodes(path) WHERE n.id IN alert.affected_nodes)
        RETURN 
            alert.id as alert_id,
            alert.attack_type as attack_type,
            alert.risk_score as risk_score,
            [node IN nodes(path) | node.id] as node_ids,
            [node IN nodes(path) | node.hostname] as hostnames,
            [node IN nodes(path) | node.type] as node_types,
            [rel IN relationships(path) | type(rel)] as relationship_types,
            length(path) as path_length
        LIMIT 1
        """
        result = self.execute_query_single(query, {"alert_id": alert_id})
        return result if result else None