from typing import Optional, List, Dict, Any
from datetime import datetime
from ..models.relationship_types import RelationshipType, RelationshipFactory
from .base_repository import BaseNeo4jRepository

class RelationshipRepository(BaseNeo4jRepository):
    """Repository for relationship operations"""
    
    def create_relationship(self, source_id: str, target_id: str, 
                           rel_type: RelationshipType, **kwargs) -> Optional[Dict[str, Any]]:
        """Create a new relationship between two nodes"""
        rel_data = RelationshipFactory.create_relationship(rel_type, **kwargs)
        
        query = """
        MATCH (source:Node {id: $source_id})
        MATCH (target:Node {id: $target_id})
        CREATE (source)-[r:RELATIONSHIP {
            type: $type,
            protocol: $protocol,
            port: $port,
            timestamp: $timestamp,
            direction: $direction,
            frequency: $frequency,
            confidence: $confidence,
            description: $description,
            weight: $weight,
            bytes_sent: $bytes_sent,
            bytes_received: $bytes_received,
            duration: $duration,
            packets: $packets,
            bandwidth: $bandwidth,
            risk_score: $risk_score,
            severity: $severity,
            detection_method: $detection_method,
            confidence_score: $confidence_score,
            evidence: $evidence,
            metadata: $metadata,
            created_at: datetime()
        }]->(target)
        RETURN r
        """
        
        result = self.execute_query_single(query, {
            "source_id": source_id,
            "target_id": target_id,
            **rel_data
        })
        return result.get("r") if result else None
    
    def get_relationships_for_node(self, node_id: str, 
                                   relationship_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all relationships for a node"""
        type_filter = f"AND type(r) = '{relationship_type}'" if relationship_type else ""
        
        query = f"""
        MATCH (n:Node {{id: $node_id}})-[r]-()
        {type_filter}
        RETURN r, startNode(r).id as source_id, endNode(r).id as target_id
        """
        results = self.execute_query(query, {"node_id": node_id})
        
        relationships = []
        for record in results:
            rel = record.get("r")
            if rel:
                relationships.append({
                    "relationship": rel,
                    "source_id": record.get("source_id"),
                    "target_id": record.get("target_id"),
                    "type": rel.get("type") if hasattr(rel, "get") else None
                })
        return relationships
    
    def get_relationship_between_nodes(self, source_id: str, target_id: str,
                                       relationship_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get relationship between two nodes"""
        type_filter = f"AND type(r) = '{relationship_type}'" if relationship_type else ""
        
        query = f"""
        MATCH (source:Node {{id: $source_id}})-[r]-(target:Node {{id: $target_id}})
        {type_filter}
        RETURN r
        """
        result = self.execute_query_single(query, {"source_id": source_id, "target_id": target_id})
        return result.get("r") if result else None
    
    def update_relationship(self, source_id: str, target_id: str, 
                           updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a relationship"""
        query = """
        MATCH (source:Node {id: $source_id})-[r]-(target:Node {id: $target_id})
        SET r += $updates
        RETURN r
        """
        result = self.execute_query_single(query, {
            "source_id": source_id,
            "target_id": target_id,
            "updates": updates
        })
        return result.get("r") if result else None
    
    def delete_relationship(self, source_id: str, target_id: str) -> bool:
        """Delete relationship between two nodes"""
        query = """
        MATCH (source:Node {id: $source_id})-[r]-(target:Node {id: $target_id})
        DELETE r
        RETURN count(r) as deleted
        """
        result = self.execute_query_single(query, {"source_id": source_id, "target_id": target_id})
        return result.get("deleted", 0) > 0 if result else False
    
    def get_relationship_statistics(self) -> Dict[str, Any]:
        """Get relationship statistics"""
        query = """
        MATCH ()-[r]-()
        RETURN 
            COUNT(r) as total_relationships,
            type(r) as relationship_type,
            COUNT(r) as count,
            AVG(r.confidence) as avg_confidence,
            AVG(r.weight) as avg_weight
        """
        results = self.execute_query(query)
        return results[0] if results else {}
    
    def get_path_between_nodes(self, source_id: str, target_id: str, 
                              max_depth: int = 5) -> List[Dict[str, Any]]:
        """Find path between two nodes"""
        query = """
        MATCH (source:Node {id: $source_id})
        MATCH (target:Node {id: $target_id})
        MATCH path = shortestPath((source)-[*1..$max_depth]-(target))
        RETURN 
            nodes(path) as path_nodes,
            relationships(path) as path_relationships,
            length(path) as path_length
        """
        results = self.execute_query(query, {
            "source_id": source_id,
            "target_id": target_id,
            "max_depth": max_depth
        })
        
        paths = []
        for record in results:
            paths.append({
                "nodes": record.get("path_nodes"),
                "relationships": record.get("path_relationships"),
                "length": record.get("path_length")
            })
        return paths
    
    def get_all_paths(self, source_id: str, target_id: str, 
                      max_depth: int = 5) -> List[Dict[str, Any]]:
        """Get all paths between two nodes"""
        query = """
        MATCH (source:Node {id: $source_id})
        MATCH (target:Node {id: $target_id})
        MATCH path = (source)-[*1..$max_depth]-(target)
        RETURN 
            nodes(path) as path_nodes,
            relationships(path) as path_relationships,
            length(path) as path_length
        ORDER BY length(path) ASC
        """
        results = self.execute_query(query, {
            "source_id": source_id,
            "target_id": target_id,
            "max_depth": max_depth
        })
        
        paths = []
        for record in results:
            paths.append({
                "nodes": record.get("path_nodes"),
                "relationships": record.get("path_relationships"),
                "length": record.get("path_length")
            })
        return paths
    
    def get_relationship_frequency(self, node_id: str) -> Dict[str, int]:
        """Get frequency of relationship types for a node"""
        query = """
        MATCH (n:Node {id: $node_id})-[r]-()
        RETURN type(r) as relationship_type, COUNT(r) as count
        ORDER BY count DESC
        """
        results = self.execute_query(query, {"node_id": node_id})
        
        frequency = {}
        for record in results:
            frequency[record.get("relationship_type")] = record.get("count")
        return frequency