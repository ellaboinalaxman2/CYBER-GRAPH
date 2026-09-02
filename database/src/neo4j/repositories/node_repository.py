"""Node repository for Neo4j operations."""

from typing import Optional, Dict, Any, List
from datetime import datetime

from src.core.logging import get_logger
from src.core.exceptions import Neo4jError, NodeNotFoundError
from src.neo4j.connection import neo4j
from src.neo4j.models.node_types import NodeType


class NodeRepository:
    """
    Repository for node operations in Neo4j.
    
    Features:
    - Create, read, update, delete nodes
    - Node properties management
    - Node type management
    - Constraints
    """
    
    def __init__(self):
        """Initialize the node repository."""
        self.logger = get_logger("neo4j.node_repository")
        if neo4j.is_connected():
            self._ensure_constraints()
            self._ensure_indexes()
        else:
            self.logger.warning("Neo4j not connected, skipping constraints and indexes")
    
    def _ensure_constraints(self) -> None:
        """Create constraints for data integrity."""
        try:
            neo4j.execute_query(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Node) REQUIRE n.id IS UNIQUE"
            )
            self.logger.info("Neo4j node constraints created")
        except Exception as e:
            self.logger.warning(f"Failed to create constraints: {e}")
    
    def _ensure_indexes(self) -> None:
        """Create indexes for performance."""
        try:
            neo4j.execute_query(
                "CREATE INDEX IF NOT EXISTS FOR (n:Node) ON (n.type)"
            )
            neo4j.execute_query(
                "CREATE INDEX IF NOT EXISTS FOR (n:Node) ON (n.created_at)"
            )
            self.logger.info("Neo4j node indexes created")
        except Exception as e:
            self.logger.warning(f"Failed to create indexes: {e}")
    
    def create_node(
        self,
        node_id: str,
        node_type: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new node.
        
        Args:
            node_id: Node identifier
            node_type: Node type
            properties: Additional properties
            
        Returns:
            Dict[str, Any]: Created node
        """
        if not neo4j.is_connected():
            self.logger.warning("Neo4j not connected, returning empty node")
            return {"id": node_id, "type": node_type, "status": "offline"}
        
        query = """
        CREATE (n:Node {id: $id, type: $type, created_at: $created_at})
        SET n += $properties
        RETURN n
        """
        
        params = {
            "id": node_id,
            "type": node_type,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "properties": properties or {},
        }
        
        try:
            result = neo4j.execute_query(query, params)
            if result:
                node_data = result[0].get("n", {})
                self.logger.info(f"Created node: {node_id} (type: {node_type})")
                return node_data
            return {}
        except Exception as e:
            self.logger.error(f"Failed to create node {node_id}: {e}")
            return {"id": node_id, "type": node_type, "error": str(e)}
    
    def get_node(self, node_id: str) -> Dict[str, Any]:
        """
        Get a node by ID.
        
        Args:
            node_id: Node ID
            
        Returns:
            Dict[str, Any]: Node data
        """
        if not neo4j.is_connected():
            self.logger.warning("Neo4j not connected, returning empty node")
            return {"id": node_id, "status": "offline"}
        
        query = """
        MATCH (n:Node {id: $id})
        RETURN n
        """
        
        try:
            result = neo4j.execute_query(query, {"id": node_id})
            if not result:
                raise NodeNotFoundError(f"Node {node_id} not found")
            return result[0].get("n", {})
        except NodeNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to get node {node_id}: {e}")
            return {"id": node_id, "error": str(e)}
    
    def update_node(
        self,
        node_id: str,
        properties: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Update a node's properties.
        
        Args:
            node_id: Node ID
            properties: Properties to update
            
        Returns:
            Dict[str, Any]: Updated node
        """
        if not neo4j.is_connected():
            self.logger.warning("Neo4j not connected, returning empty node")
            return {"id": node_id, "status": "offline"}
        
        query = """
        MATCH (n:Node {id: $id})
        SET n += $properties
        SET n.updated_at = $updated_at
        RETURN n
        """
        
        params = {
            "id": node_id,
            "properties": properties,
            "updated_at": datetime.utcnow().isoformat() + "Z",
        }
        
        try:
            result = neo4j.execute_query(query, params)
            if not result:
                raise NodeNotFoundError(f"Node {node_id} not found")
            
            self.logger.info(f"Updated node: {node_id}")
            return result[0].get("n", {})
            
        except NodeNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to update node {node_id}: {e}")
            return {"id": node_id, "error": str(e)}
    
    def delete_node(self, node_id: str) -> bool:
        """
        Delete a node.
        
        Args:
            node_id: Node ID
            
        Returns:
            bool: True if deleted
        """
        if not neo4j.is_connected():
            self.logger.warning("Neo4j not connected, cannot delete node")
            return False
        
        query = """
        MATCH (n:Node {id: $id})
        DETACH DELETE n
        RETURN count(n) as deleted
        """
        
        try:
            result = neo4j.execute_query(query, {"id": node_id})
            deleted = result[0].get("deleted", 0) if result else 0
            
            if deleted == 0:
                raise NodeNotFoundError(f"Node {node_id} not found")
            
            self.logger.info(f"Deleted node: {node_id}")
            return True
            
        except NodeNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to delete node {node_id}: {e}")
            return False
    
    def get_all_nodes(
        self,
        node_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get all nodes.
        
        Args:
            node_type: Filter by node type
            limit: Maximum number of nodes
            
        Returns:
            List[Dict[str, Any]]: List of nodes
        """
        if not neo4j.is_connected():
            self.logger.warning("Neo4j not connected, returning empty list")
            return []
        
        query = "MATCH (n:Node)"
        params = {}
        
        if node_type:
            query += " WHERE n.type = $type"
            params["type"] = node_type
        
        query += f" RETURN n LIMIT {limit}"
        
        try:
            result = neo4j.execute_query(query, params)
            return [r.get("n", {}) for r in result]
        except Exception as e:
            self.logger.error(f"Failed to get nodes: {e}")
            return []
    
    def get_node_types(self) -> List[str]:
        """
        Get all node types.
        
        Returns:
            List[str]: List of node types
        """
        if not neo4j.is_connected():
            return []
        
        query = """
        MATCH (n:Node)
        RETURN DISTINCT n.type as type
        ORDER BY type
        """
        
        try:
            result = neo4j.execute_query(query)
            return [r.get("type") for r in result if r.get("type")]
        except Exception as e:
            self.logger.error(f"Failed to get node types: {e}")
            return []
    
    def get_nodes_by_property(
        self,
        property_name: str,
        property_value: Any,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get nodes by property value.
        
        Args:
            property_name: Property name
            property_value: Property value
            limit: Maximum number of nodes
            
        Returns:
            List[Dict[str, Any]]: List of nodes
        """
        if not neo4j.is_connected():
            return []
        
        query = f"""
        MATCH (n:Node)
        WHERE n.$property_name = $property_value
        RETURN n
        LIMIT {limit}
        """
        
        params = {
            "property_name": property_name,
            "property_value": property_value,
        }
        
        try:
            result = neo4j.execute_query(query, params)
            return [r.get("n", {}) for r in result]
        except Exception as e:
            self.logger.error(f"Failed to get nodes by property: {e}")
            return []