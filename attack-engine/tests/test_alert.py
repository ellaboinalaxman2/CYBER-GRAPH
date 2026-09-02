"""Tests for alert module."""

import pytest
from datetime import datetime

from src.alert.alert_classifier import AlertClassifier, AlertStatus
from src.alert.alert_formatter import AlertFormatter
from src.alert.alert_generator import AlertGenerator


class TestAlertClassifier:
    """Tests for AlertClassifier."""
    
    def test_classify_critical(self):
        """Test classifying critical alert."""
        classifier = AlertClassifier()
        
        result = classifier.classify(
            risk_score=90,
            attack_type="lateral_movement",
            affected_nodes=["db-01", "server-01"],
        )
        
        assert result["severity"] == "CRITICAL"
        assert result["priority"] >= 4
        assert result["needs_immediate_action"] is True
    
    def test_classify_low(self):
        """Test classifying low alert."""
        classifier = AlertClassifier()
        
        result = classifier.classify(
            risk_score=20,
            attack_type="reconnaissance",
        )
        
        assert result["severity"] == "LOW"
        assert result["priority"] >= 1
        assert result["needs_immediate_action"] is False


class TestAlertFormatter:
    """Tests for AlertFormatter."""
    
    def test_format_json(self):
        """Test JSON formatting."""
        formatter = AlertFormatter()
        
        alert = {
            "alert_id": "ALT-001",
            "title": "Test Alert",
            "severity": "HIGH",
            "risk_score": 75.0,
        }
        
        result = formatter.format_json(alert)
        
        assert result["alert_id"] == "ALT-001"
        assert result["severity"] == "HIGH"
        assert "timestamp" in result
    
    def test_format_human_readable(self):
        """Test human-readable formatting."""
        formatter = AlertFormatter()
        
        alert = {
            "alert_id": "ALT-001",
            "title": "Test Alert",
            "severity": "CRITICAL",
            "risk_score": 90.0,
            "attack_type": "Lateral Movement",
            "mitre_techniques": ["T1021"],
            "recommendations": ["Action 1", "Action 2"],
        }
        
        result = formatter.format_human_readable(alert)
        
        assert "Security Alert" in result
        assert "Test Alert" in result
        assert "CRITICAL" in result
        assert "Action 1" in result
    
    def test_format_slack(self):
        """Test Slack formatting."""
        formatter = AlertFormatter()
        
        alert = {
            "alert_id": "ALT-001",
            "title": "Test Alert",
            "severity": "HIGH",
            "risk_score": 75.0,
            "attack_type": "Brute Force",
            "mitre_techniques": ["T1110"],
            "recommendations": ["Action 1"],
            "affected_nodes": ["node-1", "node-2"],
        }
        
        result = formatter.format_slack(alert)
        
        assert "text" in result
        assert "attachments" in result
        assert len(result["attachments"]) > 0


class TestAlertGenerator:
    """Tests for AlertGenerator."""
    
    def test_generate_alert(self):
        """Test generating an alert."""
        generator = AlertGenerator()
        
        incident = {
            "incident_id": "INC-001",
            "attack_type": "lateral_movement",
            "confidence": 0.9,
        }
        
        events = [
            {"event_id": "EVT-001", "event_type": "LOGIN_FAILURE"},
            {"event_id": "EVT-002", "event_type": "LOGIN_SUCCESS"},
        ]
        
        risk_assessment = {
            "risk_score": 85.0,
            "affected_nodes": ["node-1", "node-2"],
        }
        
        mitre_mapping = {
            "technique_ids": ["T1021", "T1110"],
            "tactic_ids": ["Lateral Movement"],
        }
        
        alert = generator.generate(incident, events, risk_assessment, mitre_mapping)
        
        assert alert["alert_id"].startswith("ALT-")
        assert alert["incident_id"] == "INC-001"
        assert alert["severity"] == "CRITICAL"
        assert alert["risk_score"] == 85.0
    
    def test_update_status(self):
        """Test updating alert status."""
        generator = AlertGenerator()
        
        # Generate an alert first
        incident = {"incident_id": "INC-002", "attack_type": "test"}
        events = []
        risk = {"risk_score": 50, "affected_nodes": []}
        mitre = {"technique_ids": [], "tactic_ids": []}
        
        alert = generator.generate(incident, events, risk, mitre)
        alert_id = alert["alert_id"]
        
        # Update status
        updated = generator.update_status(alert_id, "INVESTIGATING", "Started investigation", "analyst")
        
        assert updated["status"] == "INVESTIGATING"
        assert len(updated["investigation_notes"]) > 0
    
    def test_get_statistics(self):
        """Test getting statistics."""
        generator = AlertGenerator()
        
        # Generate multiple alerts
        for i in range(3):
            incident = {"incident_id": f"INC-00{i}", "attack_type": "test"}
            events = []
            risk = {"risk_score": 50 + i * 20, "affected_nodes": []}
            mitre = {"technique_ids": [], "tactic_ids": []}
            generator.generate(incident, events, risk, mitre)
        
        stats = generator.get_statistics()
        
        assert stats["total"] == 3
        assert "by_severity" in stats
        assert "by_status" in stats