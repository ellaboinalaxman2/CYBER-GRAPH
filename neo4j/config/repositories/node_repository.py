from typing import Optional, List, Dict, Any
from datetime import datetime
from ..models.node_types import NodeType, NodeFactory
from .base_repository import BaseNeo4jRepository

class NodeRepository(BaseNeo4jRepository):
    """Repository for node operations"""
    
    def create_node(self, node_type: NodeType, **kwargs) -> Optional[Dict[str, Any]]:
        """Create a new node"""
        node_data = NodeFactory.create_node(node_type, **kwargs)
        
        query = """
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
            server_role: $server_role,
            services: $services,
            ports: $ports,
            cpu_cores: $cpu_cores,
            memory_gb: $memory_gb,
            storage_gb: $storage_gb,
            db_type: $db_type,
            db_version: $db_version,
            tables: $tables,
            size_gb: $size_gb,
            sensitive_data: $sensitive_data,
            user: $user,
            department: $department,
            last_login: $last_login,
            software: $software,
            metadata: $metadata,
            created_at: datetime(),
            updated_at: datetime()
        })
        RETURN n
        """
        
        result = self.execute_query_single(query, node_data)
        return result.get("n") if result else None
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get a node by ID"""
        return super().get_node(node_id)
    
    def get_node_by_hostname(self, hostname: str) -> Optional[Dict[str, Any]]:
        """Get a node by hostname"""
        return self.get_node_by_property("hostname", hostname)
    
    def get_node_by_ip(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """Get a node by IP address"""
        return self.get_node_by_property("ip_address", ip_address)
    
    def get_nodes_by_type(self, node_type: NodeType, limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
        """Get nodes by type"""
        query = """
        MATCH (n:Node {type: $type})
        RETURN n
        SKIP $skip
        LIMIT $limit
        """
        results = self.execute_query(query, {"type": node_type.value, "skip": skip, "limit": limit})
        return [record.get("n") for record in results if record.get("n")]
    
    def get_nodes_by_criticality(self, min_criticality: int = 1, max_criticality: int = 5) -> List[Dict[str, Any]]:
        """Get nodes by criticality range"""
        query = """
        MATCH (n:Node)
        WHERE n.criticality >= $min_criticality
          AND n.criticality <= $max_criticality
        RETURN n
        ORDER BY n.criticality DESC
        """
        results = self.execute_query(query, {"min_criticality": min_criticality, "max_criticality": max_criticality})
        return [record.get("n") for record in results if record.get("n")]
    
    def update_node(self, node_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a node"""
        updates["updated_at"] = datetime.utcnow().isoformat()
        
        query = """
        MATCH (n:Node {id: $id})
        SET n += $updates
        RETURN n
        """
        result = self.execute_query_single(query, {"id": node_id, "updates": updates})
        return result.get("n") if result else None
    
    def update_node_status(self, node_id: str, status: str) -> Optional[Dict[str, Any]]:
        """Update a node's status"""
        return self.update_node(node_id, {"status": status})
    
    def get_connected_nodes(self, node_id: str) -> List[Dict[str, Any]]:
        """Get all nodes connected to a node"""
        query = """
        MATCH (n:Node {id: $id})-[r]-(connected)
        RETURN connected, type(r) as relationship_type
        """
        results = self.execute_query(query, {"id": node_id})
        return [{"node": record.get("connected"), "relationship_type": record.get("relationship_type")} 
                for record in results]
    
    def search_nodes(self, search_term: str) -> List[Dict[str, Any]]:
        """Search nodes by various fields"""
        query = """
        MATCH (n:Node)
        WHERE n.name CONTAINS $term
           OR n.hostname CONTAINS $term
           OR n.ip_address CONTAINS $term
           OR n.description CONTAINS $term
        RETURN n
        LIMIT 50
        """
        results = self.execute_query(query, {"term": search_term})
        return [record.get("n") for record in results if record.get("n")]
    
    def get_node_statistics(self) -> Dict[str, Any]:
        """Get node statistics"""
        query = """
        MATCH (n:Node)
        RETURN 
            COUNT(n) as total_nodes,
            n.type as node_type,
            COUNT(n) as count,
            AVG(n.criticality) as avg_criticality,
            SUM(CASE WHEN n.status = 'active' THEN 1 ELSE 0 END) as active_count,
            SUM(CASE WHEN n.status = 'inactive' THEN 1 ELSE 0 END) as inactive_count,
            SUM(CASE WHEN n.status = 'compromised' THEN 1 ELSE 0 END) as compromised_count
        """
        results = self.execute_query(query)
        return results[0] if results else {}