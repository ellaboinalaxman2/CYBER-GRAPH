import unittest
from neo4j.config.connection import neo4j_connection

class TestNeo4jConnection(unittest.TestCase):
    """Test Neo4j connection"""
    
    def test_connection(self):
        """Test connection to Neo4j"""
        self.assertTrue(neo4j_connection.health_check())
    
    def test_session(self):
        """Test getting a session"""
        with neo4j_connection.get_session() as session:
            self.assertIsNotNone(session)
            result = session.run("RETURN 1 as test")
            record = result.single()
            self.assertIsNotNone(record)
            self.assertEqual(record["test"], 1)
    
    def test_stats(self):
        """Test getting stats"""
        stats = neo4j_connection.get_stats()
        self.assertIn('connected', stats)
        self.assertTrue(stats['connected'])
        self.assertIn('database', stats)
        self.assertIn('nodes', stats)

if __name__ == '__main__':
    unittest.main()