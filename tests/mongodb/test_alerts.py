import unittest
from datetime import datetime
from mongodb.repositories.alert_repository import AlertRepository
from mongodb.models.alert import AlertSeverity, AlertStatus

class TestAlertRepository(unittest.TestCase):
    """Test Alert Repository"""
    
    def setUp(self):
        self.repo = AlertRepository()
        self.repo.delete_many({})  # Clear alerts before each test
    
    def test_create_alert(self):
        """Test creating an alert"""
        alert = {
            "alert_id": "ALT-001",
            "timestamp": datetime.utcnow(),
            "severity": AlertSeverity.CRITICAL,
            "status": AlertStatus.OPEN,
            "risk_score": 94,
            "confidence": 0.93,
            "attack_type": "Lateral Movement",
            "source": "192.168.1.5",
            "target": "192.168.1.10",
            "description": "Test alert",
            "events": ["EVT-001"]
        }
        result = self.repo.create_alert(alert)
        self.assertIsNotNone(result)
        
        # Verify retrieval
        retrieved = self.repo.get_alert_by_id("ALT-001")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["risk_score"], 94)
    
    def test_get_open_alerts(self):
        """Test retrieving open alerts"""
        # Create alerts
        alerts = [
            {
                "alert_id": "ALT-001",
                "timestamp": datetime.utcnow(),
                "severity": AlertSeverity.CRITICAL,
                "status": AlertStatus.OPEN,
                "risk_score": 94,
                "confidence": 0.93,
                "attack_type": "Lateral Movement",
                "source": "192.168.1.5",
                "target": "192.168.1.10",
                "description": "Test alert 1"
            },
            {
                "alert_id": "ALT-002",
                "timestamp": datetime.utcnow(),
                "severity": AlertSeverity.CRITICAL,
                "status": AlertStatus.RESOLVED,
                "risk_score": 92,
                "confidence": 0.90,
                "attack_type": "Data Exfiltration",
                "source": "192.168.1.10",
                "target": "192.168.1.20",
                "description": "Test alert 2"
            }
        ]
        
        for alert in alerts:
            self.repo.create_alert(alert)
        
        open_alerts = self.repo.get_open_alerts()
        self.assertEqual(len(open_alerts), 1)
    
    def test_update_alert_status(self):
        """Test updating alert status"""
        alert = {
            "alert_id": "ALT-001",
            "timestamp": datetime.utcnow(),
            "severity": AlertSeverity.CRITICAL,
            "status": AlertStatus.OPEN,
            "risk_score": 94,
            "confidence": 0.93,
            "attack_type": "Lateral Movement",
            "source": "192.168.1.5",
            "target": "192.168.1.10",
            "description": "Test alert"
        }
        self.repo.create_alert(alert)
        
        result = self.repo.update_alert_status("ALT-001", AlertStatus.CONFIRMED)
        self.assertIsNotNone(result)
        
        updated = self.repo.get_alert_by_id("ALT-001")
        self.assertEqual(updated["status"], AlertStatus.CONFIRMED)

if __name__ == '__main__':
    unittest.main()