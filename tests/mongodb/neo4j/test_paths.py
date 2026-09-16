import unittest
from neo4j.repositories.relationship_repository import RelationshipRepository
from neo4j.repositories.node_repository import NodeRepository
from neo4j.models.node_types import NodeType

class TestPathQueries(unittest.TestCase):
    """Test Path Finding"""
    
    def setUp(self):
        self.node_repo = NodeRepository()
        self.rel_repo = RelationshipRepository()
        
        # Clear graph
        self.node_repo.execute_query("MATCH (n) DETACH DELETE n")
        
        # Create test graph: PC-01 -> Server-01 -> Server-02 -> DB-01
        self.node_repo.create_node(NodeType.WORKSTATION, id="PC-01", name="PC-01")
        self.node_repo.create_node(NodeType.SERVER, id="SRV-01", name="Server-01")
        self.node_repo.create_node(NodeType.SERVER, id="SRV-02", name="Server-02")
        self.node_repo.create_node(NodeType.DATABASE, id="DB-01", name="DB-01")
        
        # Create relationships
        self.rel_repo.execute_query("""
            MATCH (a:Node {id: 'PC-01'})
            MATCH (b:Node {id: 'SRV-01'})
            CREATE (a)-[:CONNECTS_TO]->(b)
        """)
        self.rel_repo.execute_query("""
            MATCH (a:Node {id: 'SRV-01'})
            MATCH (b:Node {id: 'SRV-02'})
            CREATE (a)-[:CONNECTS_TO]->(b)
        """)
        self.rel_repo.execute_query("""
            MATCH (a:Node {id: 'SRV-02'})
            MATCH (b:Node {id: 'DB-01'})
            CREATE (a)-[:CONNECTS_TO]->(b)
        """)
    
    def test_find_path(self):
        """Test finding a path between nodes"""
        paths = self.rel_repo.get_path_between_nodes("PC-01", "DB-01")
        self.assertGreater(len(paths), 0)
        
        if paths:
            path = paths[0]
            self.assertEqual(path["length"], 3)
            self.assertEqual(len(path["nodes"]), 4)
    
    def test_all_paths(self):
        """Test finding all paths between nodes"""
        # Add alternative path
        self.rel_repo.execute_query("""
            MATCH (a:Node {id: 'PC-01'})
            MATCH (c:Node {id: 'SRV-02'})
            CREATE (a)-[:ALTERNATE]->(c)
        """)
        
        paths = self.rel_repo.get_all_paths("PC-01", "DB-01")
        self.assertGreater(len(paths), 1)
    
    def test_shortest_path(self):
        """Test finding shortest path"""
        paths = self.rel_repo.get_path_between_nodes("PC-01", "DB-01")
        self.assertGreater(len(paths), 0)
        
        if paths:
            path = paths[0]
            self.assertEqual(path["length"], 3)

if __name__ == '__main__':
    unittest.main()