from typing import Optional, List, Dict, Any, Union
from neo4j import Session
from ..config.connection import neo4j_connection

class BaseNeo4jRepository:
    """Base repository for Neo4j operations"""
    
    def __init__(self):
        self.connection = neo4j_connection
    
    def get_session(self) -> Session:
        """Get a session for database operations"""
        return self.connection.get_session()
    
    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a Cypher query and return results"""
        with self.get_session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
    
    def execute_query_single(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Execute a Cypher query and return single result"""
        with self.get_session() as session:
            result = session.run(query, parameters or {})
            record = result.single()
            return record.data() if record else None
    
    def execute_write(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a write transaction"""
        with self.get_session() as session:
            return session.execute_write(lambda tx: tx.run(query, parameters or {}).single())
    
    def execute_write_batch(self, query: str, parameters_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple write operations in a transaction"""
        def _execute_batch(tx):
            results = []
            for params in parameters_list:
                result = tx.run(query, params)
                results.append(result.single())
            return results
        
        with self.get_session() as session:
            return session.execute_write(_execute_batch)
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get a node by ID"""
        query = """
        MATCH (n:Node {id: $id})
        RETURN n
        """
        result = self.execute_query_single(query, {"id": node_id})
        return result.get("n") if result else None
    
    def get_node_by_property(self, property_name: str, property_value: Any) -> Optional[Dict[str, Any]]:
        """Get a node by property"""
        query = f"""
        MATCH (n:Node {{`{property_name}`: $value}})
        RETURN n
        """
        result = self.execute_query_single(query, {"value": property_value})
        return result.get("n") if result else None
    
    def get_all_nodes(self, limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
        """Get all nodes with pagination"""
        query = """
        MATCH (n:Node)
        RETURN n
        SKIP $skip
        LIMIT $limit
        """
        results = self.execute_query(query, {"skip": skip, "limit": limit})
        return [record.get("n") for record in results if record.get("n")]
    
    def delete_node(self, node_id: str) -> bool:
        """Delete a node by ID"""
        query = """
        MATCH (n:Node {id: $id})
        DETACH DELETE n
        RETURN count(n) as deleted
        """
        result = self.execute_query_single(query, {"id": node_id})
        return result.get("deleted", 0) > 0 if result else False
    
    def count_nodes(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count nodes with optional filters"""
        where_clause = ""
        params = {}
        
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f"n.{key} = ${key}")
                params[key] = value
            if conditions:
                where_clause = "WHERE " + " AND ".join(conditions)
        
        query = f"""
        MATCH (n:Node)
        {where_clause}
        RETURN COUNT(n) as count
        """
        result = self.execute_query_single(query, params)
        return result.get("count", 0) if result else 0