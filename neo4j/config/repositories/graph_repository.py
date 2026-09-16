from typing import Optional, List, Dict, Any
from .base_repository import BaseNeo4jRepository

class GraphRepository(BaseNeo4jRepository):
    """Repository for graph-level operations"""
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """Get comprehensive graph statistics"""
        query = """
        CALL {
            MATCH (n) RETURN COUNT(n) as total_nodes
        }
        CALL {
            MATCH ()-[r]->() RETURN COUNT(r) as total_relationships
        }
        CALL {
            MATCH (n) WITH n, COUNT { (n)-[]-() } as degree
            RETURN AVG(degree) as avg_degree
        }
        CALL {
            MATCH (n) RETURN MIN(n.criticality) as min_criticality
        }
        CALL {
            MATCH (n) RETURN MAX(n.criticality) as max_criticality
        }
        CALL {
            MATCH (n) RETURN AVG(n.criticality) as avg_criticality
        }
        RETURN 
            total_nodes,
            total_relationships,
            avg_degree,
            min_criticality,
            max_criticality,
            avg_criticality
        """
        result = self.execute_query_single(query)
        return result if result else {}
    
    def get_node_type_distribution(self) -> List[Dict[str, Any]]:
        """Get distribution of node types"""
        query = """
        MATCH (n:Node)
        RETURN 
            n.type as node_type,
            COUNT(n) as count,
            AVG(n.criticality) as avg_criticality,
            SUM(CASE WHEN n.status = 'active' THEN 1 ELSE 0 END) as active_count
        ORDER BY count DESC
        """
        return self.execute_query(query)
    
    def get_relationship_type_distribution(self) -> List[Dict[str, Any]]:
        """Get distribution of relationship types"""
        query = """
        MATCH ()-[r]->()
        RETURN 
            type(r) as relationship_type,
            COUNT(r) as count,
            AVG(r.confidence) as avg_confidence,
            AVG(r.weight) as avg_weight
        ORDER BY count DESC
        """
        return self.execute_query(query)
    
    def get_degree_distribution(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get degree distribution for nodes"""
        query = """
        MATCH (n:Node)
        WITH n, COUNT { (n)-[]-() } as degree
        RETURN 
            n.id as node_id,
            n.hostname as hostname,
            n.type as node_type,
            degree
        ORDER BY degree DESC
        LIMIT $limit
        """
        return self.execute_query(query, {"limit": limit})
    
    def get_top_connected_nodes(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get top connected nodes"""
        query = """
        MATCH (n:Node)
        WITH n, COUNT { (n)-[]-() } as connection_count
        WHERE connection_count > 0
        RETURN 
            n.id as node_id,
            n.hostname as hostname,
            n.type as node_type,
            n.criticality as criticality,
            connection_count,
            n.criticality * connection_count as vulnerability_score
        ORDER BY vulnerability_score DESC
        LIMIT $limit
        """
        return self.execute_query(query, {"limit": limit})
    
    def get_graph_density(self) -> float:
        """Get graph density"""
        query = """
        MATCH (n:Node)
        WITH COUNT(n) as node_count
        MATCH ()-[r]->()
        WITH node_count, COUNT(r) as relationship_count
        RETURN 
            CASE 
                WHEN node_count > 1 THEN 
                    (2.0 * relationship_count) / (node_count * (node_count - 1))
                ELSE 0 
            END as density
        """
        result = self.execute_query_single(query)
        return result.get("density", 0.0) if result else 0.0
    
    def get_suspicious_subgraphs(self, min_risk: float = 0.5, max_depth: int = 3) -> List[Dict[str, Any]]:
        """Get suspicious subgraphs based on risk score"""
        query = """
        MATCH path = (n)-[*1..$max_depth]-(m)
        WHERE ANY(n IN nodes(path) WHERE n.risk_score > $min_risk)
        WITH COLLECT(path) as paths
        UNWIND paths as path
        RETURN 
            [node IN nodes(path) | node.id] as path_nodes,
            length(path) as path_length,
            REDUCE(s = 0, n IN nodes(path) | s + n.risk_score) as total_risk
        ORDER BY total_risk DESC
        LIMIT 10
        """
        return self.execute_query(query, {"min_risk": min_risk, "max_depth": max_depth})
    
    def get_isolated_nodes(self) -> List[Dict[str, Any]]:
        """Get isolated nodes (no relationships)"""
        query = """
        MATCH (n:Node)
        WHERE NOT (n)-[]-()
        RETURN n
        """
        results = self.execute_query(query)
        return [record.get("n") for record in results if record.get("n")]
    
    def clear_graph(self) -> bool:
        """Clear all nodes and relationships"""
        query = """
        MATCH (n)
        DETACH DELETE n
        RETURN COUNT(n) as deleted
        """
        result = self.execute_query_single(query)
        return result.get("deleted", 0) > 0 if result else False