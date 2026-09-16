import unittest
from mongodb.config.connection import mongodb_connection

class TestMongoDBConnection(unittest.TestCase):
    """Test MongoDB connection"""
    
    def test_connection(self):
        """Test connection to MongoDB"""
        self.assertTrue(mongodb_connection.health_check())
    
    def test_database(self):
        """Test database access"""
        db = mongodb_connection.database
        self.assertIsNotNone(db)
        self.assertEqual(db.name, mongodb_connection.settings.database)
    
    def test_collections(self):
        """Test collection access"""
        collections = mongodb_connection.database.list_collection_names()
        self.assertIsInstance(collections, list)
    
    def test_stats(self):
        """Test getting stats"""
        stats = mongodb_connection.get_stats()
        self.assertIn('connected', stats)
        self.assertTrue(stats['connected'])

if __name__ == '__main__':
    unittest.main()