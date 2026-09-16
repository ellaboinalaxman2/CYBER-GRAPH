import unittest
from neo4j.repositories.attack_graph_repository import AttackGraphRepository
from neo4j.repositories.node_repository import NodeRepository
from neo4j.models.node_types import NodeType

class TestIntegration(unittest.TestCase):
    """Integration tests for attack path reconstruction"""
    
    def setUp(self):
        self.node_repo = NodeRepository()
        self.attack_repo = AttackGraphRepository()
        
        # Clear graph
        self.node_repo.execute_query("MATCH (n) DETACH DELETE n")
        
        # Create full test graph
        self._create_test_graph()
    
    def _create_test_graph(self):
        """Create a realistic test graph"""
        # Create nodes
        nodes = [
            ("PC-01", NodeType.WORKSTATION, {"id": "PC-01", "name": "PC-01", "criticality": 2}),
            ("PC-02", NodeType.WORKSTATION, {"id": "PC-02", "name": "PC-02", "criticality": 2}),
            ("SRV-01", NodeType.SERVER, {"id": "SRV-01", "name": "App Server", "criticality": 4}),
            ("SRV-02", NodeType.SERVER, {"id": "SRV-02", "name": "Web Server", "criticality": 3}),
            ("DB-01", NodeType.DATABASE, {"id": "DB-01", "name": "Database", "criticality": 5}),
            ("FW-01", NodeType.FIREWALL, {"id": "FW-01", "name": "Firewall", "criticality": 5})
        ]
        
        for node_id, node_type, props in nodes:
            self.node_repo.create_node(node_type, **props)
        
        # Create relationships
        relationships = [
            ("PC-01", "SRV-01", "CONNECTS_TO"),
            ("PC-02", "SRV-02", "CONNECTS_TO"),
            ("SRV-01", "SRV-02", "CONNECTS_TO"),
            ("SRV-02", "DB-01", "ACCESSES"),
            ("FW-01", "SRV-01", "CONNECTS_TO"),
            ("FW-01", "SRV-02", "CONNECTS_TO")
        ]
        
        for source, target, rel_type in relationships:
            self.node_repo.execute_query(f"""
                MATCH (a:Node {{id: '{source}'}})
                MATCH (b:Node {{id: '{target}'}})
                CREATE (a)-[:{rel_type}]->(b)
            """)
    
    def test_attack_path_reconstruction(self):
        """Test attack path reconstruction"""
        # Find path from PC-01 to DB-01
        paths = self.attack_repo.find_attack_paths("PC-01", "DB-01")
        
        self.assertGreater(len(paths), 0)
        
        if paths:
            path = paths[0]
            self.assertIn("node_ids", path)
            self.assertIn("path_length", path)
            self.assertEqual(path["path_length"], 3)
            self.assertEqual(path["node_ids"][0], "PC-01")
            self.assertEqual(path["node_ids"][-1], "DB-01")
    
    def test_lateral_movement(self):
        """Test lateral movement detection"""
        paths = self.attack_repo.find_lateral_movement_paths("PC-01", min_connections=2)
        
        self.assertGreater(len(paths), 0)
        
        if paths:
            path = paths[0]
            self.assertGreaterEqual(path["hop_count"], 2)
    
    def test_high_risk_paths(self):
        """Test finding high risk paths"""
        # Add a high risk alert
        self.node_repo.execute_query("""
            CREATE (a:Alert:Node {
                id: 'ALT-001',
                type: 'ALERT',
                risk_score: 95,
                attack_type: 'Lateral Movement'
            })
        """)
        
        self.node_repo.execute_query("""
            MATCH (a:Alert {id: 'ALT-001'})
            MATCH (n:Node {id: 'PC-01'})
            CREATE (a)-[:RELATED_TO]->(n)
        """)
        
        paths = self.attack_repo.find_high_risk_attack_paths(min_risk_score=80)
        
        self.assertGreater(len(paths), 0)
        
        if paths:
            path = paths[0]
            self.assertGreaterEqual(path["risk_score"], 80)

if __name__ == '__main__':
    unittest.main()