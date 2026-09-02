"""Seed graph with sample data for testing."""

from typing import Dict, Any, List
from datetime import datetime

from src.core.logging import get_logger
from src.neo4j.connection import neo4j
from src.neo4j.repositories.node_repository import NodeRepository
from src.neo4j.repositories.graph_repository import GraphRepository
from src.neo4j.models.node_types import NodeType
from src.neo4j.models.relationship_types import RelationshipType


class GraphSeeder:
    """
    Seeds the Neo4j graph with sample data.
    
    Creates a sample network topology:
    PC-01 → Server-01 → Server-02 → DB-01
    PC-02 → Server-01
    PC-03 → Server-02
    """
    
    def __init__(self):
        """Initialize the graph seeder."""
        self.logger = get_logger("neo4j.seeder")
        self.node_repo = NodeRepository()
        self.graph_repo = GraphRepository()
    
    def seed(self) -> Dict[str, Any]:
        """
        Seed the graph with sample data.
        
        Returns:
            Dict[str, Any]: Seeding results
        """
        self.logger.info("Seeding Neo4j graph with sample data...")
        
        results = {
            "nodes_created": 0,
            "relationships_created": 0,
            "errors": [],
        }
        
        try:
            # Create nodes
            nodes = self._create_sample_nodes()
            results["nodes_created"] = len(nodes)
            
            # Create relationships
            relationships = self._create_sample_relationships()
            results["relationships_created"] = len(relationships)
            
            self.logger.info(
                f"Seed complete: {results['nodes_created']} nodes, "
                f"{results['relationships_created']} relationships"
            )
            
        except Exception as e:
            self.logger.error(f"Seeding failed: {e}")
            results["errors"].append(str(e))
        
        return results
    
    def _create_sample_nodes(self) -> List[Dict[str, Any]]:
        """Create sample nodes."""
        nodes = [
            {"id": "PC-01", "type": NodeType.WORKSTATION.value, "properties": {"hostname": "employee-pc-01", "ip": "192.168.1.10"}},
            {"id": "PC-02", "type": NodeType.WORKSTATION.value, "properties": {"hostname": "employee-pc-02", "ip": "192.168.1.11"}},
            {"id": "PC-03", "type": NodeType.WORKSTATION.value, "properties": {"hostname": "employee-pc-03", "ip": "192.168.1.12"}},
            {"id": "SERVER-01", "type": NodeType.SERVER.value, "properties": {"hostname": "web-server-01", "ip": "192.168.1.20", "criticality": 9}},
            {"id": "SERVER-02", "type": NodeType.SERVER.value, "properties": {"hostname": "app-server-01", "ip": "192.168.1.21", "criticality": 8}},
            {"id": "DB-01", "type": NodeType.DATABASE.value, "properties": {"hostname": "db-server-01", "ip": "192.168.1.30", "criticality": 10}},
            {"id": "FW-01", "type": NodeType.FIREWALL.value, "properties": {"hostname": "firewall-01", "ip": "192.168.1.1", "criticality": 10}},
        ]
        
        created_nodes = []
        for node in nodes:
            try:
                result = self.node_repo.create_node(
                    node["id"],
                    node["type"],
                    node["properties"],
                )
                created_nodes.append(result)
            except Exception as e:
                self.logger.warning(f"Failed to create node {node['id']}: {e}")
                # Continue with other nodes
        
        return created_nodes
    
    def _create_sample_relationships(self) -> List[Dict[str, Any]]:
        """Create sample relationships."""
        relationships = [
            ("PC-01", "SERVER-01", RelationshipType.CONNECTS_TO.value, {"protocol": "SSH", "port": 22}),
            ("PC-02", "SERVER-01", RelationshipType.CONNECTS_TO.value, {"protocol": "SSH", "port": 22}),
            ("PC-03", "SERVER-02", RelationshipType.CONNECTS_TO.value, {"protocol": "SSH", "port": 22}),
            ("SERVER-01", "SERVER-02", RelationshipType.CONNECTS_TO.value, {"protocol": "HTTP", "port": 80}),
            ("SERVER-02", "DB-01", RelationshipType.ACCESSES.value, {"protocol": "MySQL", "port": 3306}),
            ("SERVER-01", "DB-01", RelationshipType.ACCESSES.value, {"protocol": "MySQL", "port": 3306}),
            ("PC-01", "FW-01", RelationshipType.TALKS_TO.value, {"protocol": "Any"}),
            ("PC-02", "FW-01", RelationshipType.TALKS_TO.value, {"protocol": "Any"}),
        ]
        
        created_relationships = []
        for source, target, rel_type, props in relationships:
            try:
                result = self.graph_repo.create_relationship(
                    source,
                    target,
                    rel_type,
                    props,
                )
                created_relationships.append(result)
            except Exception as e:
                self.logger.warning(f"Failed to create relationship {source}->{target}: {e}")
                # Continue with other relationships
        
        return created_relationships
    
    def clear_graph(self) -> bool:
        """
        Clear all nodes and relationships from the graph.
        
        Returns:
            bool: True if successful
        """
        try:
            query = "MATCH (n) DETACH DELETE n"
            neo4j.execute_query(query)
            self.logger.info("Graph cleared")
            return True
        except Exception as e:
            self.logger.error(f"Failed to clear graph: {e}")
            return False


# Run seeder
if __name__ == "__main__":
    seeder = GraphSeeder()
    seeder.clear_graph()
    results = seeder.seed()
    print(f"Seeding results: {results}")