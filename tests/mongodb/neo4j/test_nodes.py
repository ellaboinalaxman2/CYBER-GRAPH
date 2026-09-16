import unittest
from neo4j.repositories.node_repository import NodeRepository
from neo4j.models.node_types import NodeType

class TestNodeRepository(unittest.TestCase):
    """Test Node Repository"""
    
    def setUp(self):
        self.repo = NodeRepository()
        # Clear nodes before each test
        self.repo.execute_query("MATCH (n) DETACH DELETE n")
    
    def test_create_node(self):
        """Test creating a node"""
        node = self.repo.create_node(
            NodeType.SERVER,
            id="SRV-001",
            name="Test Server",
            hostname="test-server-01",
            ip_address="192.168.1.10",
            status="active",
            criticality=4
        )
        self.assertIsNotNone(node)
        self.assertEqual(node["id"], "SRV-001")
        self.assertEqual(node["type"], NodeType.SERVER.value)
    
    def test_get_node(self):
        """Test retrieving a node"""
        self.repo.create_node(
            NodeType.WORKSTATION,
            id="WS-001",
            name="Test Workstation",
            hostname="test-ws-01"
        )
        
        node = self.repo.get_node("WS-001")
        self.assertIsNotNone(node)
        self.assertEqual(node["id"], "WS-001")
    
    def test_update_node(self):
        """Test updating a node"""
        self.repo.create_node(
            NodeType.SERVER,
            id="SRV-001",
            name="Test Server",
            hostname="test-server-01"
        )
        
        updated = self.repo.update_node("SRV-001", {"status": "compromised"})
        self.assertIsNotNone(updated)
        
        node = self.repo.get_node("SRV-001")
        self.assertEqual(node["status"], "compromised")
    
    def test_get_nodes_by_type(self):
        """Test retrieving nodes by type"""
        self.repo.create_node(NodeType.SERVER, id="SRV-001", name="Server 1")
        self.repo.create_node(NodeType.SERVER, id="SRV-002", name="Server 2")
        self.repo.create_node(NodeType.WORKSTATION, id="WS-001", name="Workstation 1")
        
        servers = self.repo.get_nodes_by_type(NodeType.SERVER)
        self.assertEqual(len(servers), 2)
    
    def test_connected_nodes(self):
        """Test getting connected nodes"""
        self.repo.create_node(NodeType.WORKSTATION, id="WS-001", name="Workstation")
        self.repo.create_node(NodeType.SERVER, id="SRV-001", name="Server")
        
        # Create relationship using execute_query directly
        self.repo.execute_query("""
            MATCH (a:Node {id: 'WS-001'})
            MATCH (b:Node {id: 'SRV-001'})
            CREATE (a)-[:CONNECTS_TO]->(b)
        """)
        
        connected = self.repo.get_connected_nodes("WS-001")
        self.assertEqual(len(connected), 1)
        self.assertEqual(connected[0]["node"]["id"], "SRV-001")

if __name__ == '__main__':
    unittest.main()