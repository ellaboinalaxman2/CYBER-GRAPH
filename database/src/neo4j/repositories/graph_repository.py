"""Graph repository for Neo4j operations."""

from typing import Optional, List, Dict, Any
from datetime import datetime

from src.core.logging import get_logger
from src.core.exceptions import Neo4jError
from src.neo4j.connection import neo4j
from src.neo4j.repositories.node_repository import NodeRepository


class GraphRepository:
    """
    Repository for graph operations in Neo4j.
    
    Features:
    - Create relationships
    - Find paths between nodes
    - Get neighbors
    - Graph statistics
    - Attack path reconstruction
    """
    
    def __init__(self):
        """Initialize the graph repository."""
        self.logger = get_logger("neo4j.graph_repository")
        self.node_repo = NodeRepository()
        if neo4j.is_connected():
            self._ensure_indexes()
    
    def _ensure_indexes(self) -> None:
        """Create indexes for performance."""
        try:
            neo4j.execute_query(
                "CREATE INDEX IF NOT EXISTS FOR ()-[r]-() ON (r.type)"
            )
            self.logger.info("Neo4j relationship indexes created")
        except Exception as e:
            self.logger.warning(f"Failed to create indexes: {e}")
    
    def create_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a relationship between two nodes."""
        if not neo4j.is_connected():
            self.logger.warning("Neo4j not connected, returning empty relationship")
            return {"status": "offline"}
        
        # First verify nodes exist
        try:
            self.node_repo.get_node(source_id)
            self.node_repo.get_node(target_id)
        except Exception as e:
            raise Neo4jError(f"Node not found: {e}")
        
        query = """
        MATCH (a:Node {id: $source_id})
        MATCH (b:Node {id: $target_id})
        CREATE (a)-[r:$rel_type {created_at: $created_at}]->(b)
        SET r += $properties
        RETURN a, b, r
        """
        
        params = {
            "source_id": source_id,
            "target_id": target_id,
            "rel_type": relationship_type,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "properties": properties or {},
        }
        
        try:
            result = neo4j.execute_query(query, params)
            self.logger.info(f"Created relationship: {source_id} -> {target_id} ({relationship_type})")
            return {
                "source": result[0].get("a", {}),
                "target": result[0].get("b", {}),
                "relationship": result[0].get("r", {}),
            } if result else {}
        except Exception as e:
            self.logger.error(f"Failed to create relationship: {e}")
            return {"error": str(e)}
    
    def find_path(
        self,
        source_id: str,
        target_id: str,
        max_depth: int = 10,
    ) -> List[Dict[str, Any]]:
        """Find paths between two nodes."""
        if not neo4j.is_connected():
            self.logger.warning("Neo4j not connected, returning empty paths")
            return []
        
        query = """
        MATCH path = shortestPath(
            (a:Node {id: $source_id})-[*..$max_depth]-(b:Node {id: $target_id})
        )
        RETURN path
        """
        
        params = {
            "source_id": source_id,
            "target_id": target_id,
            "max_depth": max_depth,
        }
        
        try:
            result = neo4j.execute_query(query, params)
            
            paths = []
            for record in result:
                path = record.get("path")
                if path:
                    nodes = [node.get("id") for node in path.nodes]
                    relationships = [
                        {
                            "from": rel.start_node.get("id"),
                            "to": rel.end_node.get("id"),
                            "type": rel.type,
                        }
                        for rel in path.relationships
                    ]
                    paths.append({
                        "nodes": nodes,
                        "relationships": relationships,
                        "length": len(nodes) - 1,
                    })
            
            return paths
            
        except Exception as e:
            self.logger.error(f"Failed to find path: {e}")
            return []
    
    def get_neighbors(
        self,
        node_id: str,
        relationship_type: Optional[str] = None,
        depth: int = 1,
    ) -> List[Dict[str, Any]]:
        """Get neighbors of a node."""
        if not neo4j.is_connected():
            self.logger.warning("Neo4j not connected, returning empty neighbors")
            return []
        
        if depth == 1:
            query = """
            MATCH (n:Node {id: $node_id})
            OPTIONAL MATCH (n)-[r]-(neighbor:Node)
            """
            
            if relationship_type:
                query += f" WHERE type(r) = $rel_type"
            
            query += """
            RETURN neighbor.id as id, neighbor.type as type, 
                   neighbor.properties as properties,
                   collect(type(r)) as relationship_types
            """
        else:
            query = f"""
            MATCH (n:Node {{id: $node_id}})
            OPTIONAL MATCH (n)-[*1..{depth}]-(neighbor:Node)
            WHERE n <> neighbor
            """
            
            if relationship_type:
                query += f" AND type(relationships)[0] = $rel_type"
            
            query += """
            RETURN DISTINCT neighbor.id as id, neighbor.type as type,
                   neighbor.properties as properties
            """
        
        params = {
            "node_id": node_id,
            "rel_type": relationship_type,
        }
        
        try:
            result = neo4j.execute_query(query, params)
            return [
                {
                    "id": r.get("id"),
                    "type": r.get("type"),
                    "properties": r.get("properties", {}),
                    "relationship_types": r.get("relationship_types", []),
                }
                for r in result
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to get neighbors: {e}")
            return []
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """Get graph statistics."""
        if not neo4j.is_connected():
            return {"status": "offline", "message": "Neo4j not connected"}
        
        queries = {
            "total_nodes": "MATCH (n:Node) RETURN count(n) as count",
            "total_relationships": "MATCH ()-[r]-() RETURN count(r) as count",
            "node_types": """
                MATCH (n:Node)
                RETURN n.type as type, count(n) as count
                ORDER BY count DESC
            """,
            "relationship_types": """
                MATCH ()-[r]-()
                RETURN type(r) as type, count(r) as count
                ORDER BY count DESC
            """,
            "most_connected": """
                MATCH (n:Node)-[]-()
                RETURN n.id as id, n.type as type, count(*) as degree
                ORDER BY degree DESC
                LIMIT 10
            """,
        }
        
        stats = {}
        
        try:
            for key, query in queries.items():
                result = neo4j.execute_query(query)
                if key == "total_nodes":
                    stats[key] = result[0].get("count", 0) if result else 0
                elif key == "total_relationships":
                    stats[key] = result[0].get("count", 0) if result else 0
                elif key == "node_types":
                    stats[key] = [
                        {"type": r.get("type"), "count": r.get("count")}
                        for r in result
                    ]
                elif key == "relationship_types":
                    stats[key] = [
                        {"type": r.get("type"), "count": r.get("count")}
                        for r in result
                    ]
                elif key == "most_connected":
                    stats[key] = [
                        {
                            "id": r.get("id"),
                            "type": r.get("type"),
                            "degree": r.get("degree"),
                        }
                        for r in result
                    ]
            
            stats["timestamp"] = datetime.utcnow().isoformat() + "Z"
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get graph statistics: {e}")
            return {"error": str(e)}
    
    def get_attack_paths(
        self,
        source_id: str,
        max_depth: int = 5,
    ) -> List[Dict[str, Any]]:
        """Get all attack paths from a source."""
        if not neo4j.is_connected():
            self.logger.warning("Neo4j not connected, returning empty attack paths")
            return []
        
        query = """
        MATCH path = (a:Node {id: $source_id})-[*1..$max_depth]-(target:Node)
        WHERE a <> target
        RETURN path, length(path) as length
        ORDER BY length ASC
        """
        
        params = {
            "source_id": source_id,
            "max_depth": max_depth,
        }
        
        try:
            result = neo4j.execute_query(query, params)
            
            paths = []
            for record in result:
                path = record.get("path")
                if path:
                    paths.append({
                        "nodes": [node.get("id") for node in path.nodes],
                        "relationships": [
                            {
                                "from": rel.start_node.get("id"),
                                "to": rel.end_node.get("id"),
                                "type": rel.type,
                            }
                            for rel in path.relationships
                        ],
                        "length": record.get("length", 0),
                    })
            
            return paths
            
        except Exception as e:
            self.logger.error(f"Failed to get attack paths: {e}")
            return []