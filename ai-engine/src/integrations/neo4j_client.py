"""Neo4j client for Member 3 - AI Engine."""

from typing import Optional, Dict, Any, List
from neo4j import GraphDatabase, Driver, Session

from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import DataLoaderError


class Neo4jClient:
    """
    Client for Neo4j graph database (Member 4).
    
    Features:
    - Connect to Neo4j
    - Query graph data
    - Convert to ML format
    """
    
    def __init__(self):
        """Initialize the Neo4j client."""
        self.logger = get_logger("integrations.neo4j")
        self.driver: Optional[Driver] = None
        self._connected = False
    
    def connect(self) -> bool:
        """
        Connect to Neo4j.
        
        Returns:
            bool: True if connected
        """
        try:
            self.driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
            )
            self.driver.verify_connectivity()
            self._connected = True
            self.logger.info(f"Connected to Neo4j at {settings.neo4j_uri}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Neo4j: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from Neo4j."""
        if self.driver:
            self.driver.close()
            self._connected = False
            self.logger.info("Disconnected from Neo4j")
    
    def get_graph(self, query: Optional[str] = None) -> Dict[str, Any]:
        """
        Get graph data from Neo4j.
        
        Args:
            query: Custom Cypher query
            
        Returns:
            Dict[str, Any]: Graph data
        """
        if not self._connected:
            self.connect()
        
        if query is None:
            query = """
            MATCH (n)
            OPTIONAL MATCH (n)-[r]->(m)
            RETURN 
                n as node,
                {source_id: id(n), target_id: id(m), type: type(r)} as edge
            LIMIT 1000
            """
        
        nodes = []
        edges = []
        
        try:
            with self.driver.session() as session:
                result = session.run(query)
                
                for record in result:
                    if "node" in record:
                        node_data = record["node"]
                        nodes.append({
                            "node_id": str(node_data.get("id", len(nodes))),
                            "node_type": node_data.get("type", "device"),
                            "hostname": node_data.get("hostname"),
                            "ip_address": node_data.get("ip"),
                            "device_type": node_data.get("device_type"),
                            "criticality": node_data.get("criticality", 1),
                            "properties": dict(node_data.items()),
                        })
                    
                    if "edge" in record:
                        edge_data = record["edge"]
                        edges.append({
                            "source_id": str(edge_data.get("source_id")),
                            "target_id": str(edge_data.get("target_id")),
                            "relationship_type": edge_data.get("type", "CONNECTS_TO"),
                            "properties": edge_data.get("properties", {}),
                        })
            
            self.logger.info(f"Retrieved {len(nodes)} nodes and {len(edges)} edges from Neo4j")
            return {"nodes": nodes, "edges": edges}
            
        except Exception as e:
            self.logger.error(f"Failed to get graph from Neo4j: {e}")
            raise DataLoaderError(f"Neo4j query failed: {e}")