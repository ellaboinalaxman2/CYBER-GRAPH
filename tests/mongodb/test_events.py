import unittest
from datetime import datetime, timedelta
from mongodb.repositories.event_repository import EventRepository
from mongodb.models.event import EventType

class TestEventRepository(unittest.TestCase):
    """Test Event Repository"""
    
    def setUp(self):
        self.repo = EventRepository()
        self.repo.delete_many({})  # Clear events before each test
    
    def test_create_event(self):
        """Test creating an event"""
        event = {
            "event_id": "EVT-001",
            "timestamp": datetime.utcnow(),
            "source": "192.168.1.5",
            "destination": "192.168.1.10",
            "protocol": "TCP",
            "event_type": EventType.NETWORK_CONNECTION,
            "message": "Test event",
            "raw_log": "RAW: Test event"
        }
        result = self.repo.create_event(event)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.inserted_id)
        
        # Verify retrieval
        retrieved = self.repo.get_event_by_id("EVT-001")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["source"], "192.168.1.5")
    
    def test_get_events(self):
        """Test retrieving events"""
        # Create multiple events
        for i in range(10):
            event = {
                "event_id": f"EVT-{i+1:03d}",
                "timestamp": datetime.utcnow(),
                "source": "192.168.1.5",
                "destination": "192.168.1.10",
                "protocol": "TCP",
                "event_type": EventType.NETWORK_CONNECTION,
                "message": f"Test event {i+1}",
                "raw_log": f"RAW: Test event {i+1}"
            }
            self.repo.create_event(event)
        
        events = self.repo.get_events(limit=5)
        self.assertEqual(len(events), 5)
    
    def test_get_events_by_source(self):
        """Test retrieving events by source"""
        event = {
            "event_id": "EVT-001",
            "timestamp": datetime.utcnow(),
            "source": "192.168.1.100",
            "destination": "192.168.1.200",
            "protocol": "TCP",
            "event_type": EventType.NETWORK_CONNECTION,
            "message": "Test event",
            "raw_log": "RAW: Test event"
        }
        self.repo.create_event(event)
        
        events = self.repo.get_events_by_source("192.168.1.100")
        self.assertEqual(len(events), 1)
    
    def test_update_event_anomaly(self):
        """Test updating event anomaly status"""
        event = {
            "event_id": "EVT-001",
            "timestamp": datetime.utcnow(),
            "source": "192.168.1.5",
            "destination": "192.168.1.10",
            "protocol": "TCP",
            "event_type": EventType.NETWORK_CONNECTION,
            "message": "Test event",
            "raw_log": "RAW: Test event"
        }
        self.repo.create_event(event)
        
        result = self.repo.update_event_anomaly("EVT-001", True, 0.95)
        self.assertIsNotNone(result)
        
        updated = self.repo.get_event_by_id("EVT-001")
        self.assertTrue(updated["is_anomaly"])
        self.assertEqual(updated["anomaly_score"], 0.95)

if __name__ == '__main__':
    unittest.main()