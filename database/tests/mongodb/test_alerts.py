"""Tests for alert operations."""

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


class TestAlertEndpoints:
    """Test alert CRUD endpoints."""
    
    def test_create_alert(self):
        """Test creating an alert."""
        alert_data = {
            "alert_id": "ALT-TEST-001",
            "severity": "HIGH",
            "risk_score": 85.0,
            "confidence": 0.92,
            "attack_type": "Brute Force",
        }
        
        response = client.post("/api/v1/alerts/", json=alert_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "created"
        assert data["alert"]["alert_id"] == "ALT-TEST-001"
    
    def test_get_alerts(self):
        """Test getting alerts."""
        response = client.get("/api/v1/alerts/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "alerts" in data
    
    def test_update_alert_status(self):
        """Test updating alert status."""
        # First create
        alert_data = {
            "alert_id": "ALT-TEST-002",
            "severity": "MEDIUM",
            "risk_score": 65.0,
            "confidence": 0.85,
        }
        client.post("/api/v1/alerts/", json=alert_data)
        
        # Then update status
        response = client.patch(
            "/api/v1/alerts/ALT-TEST-002/status?status=INVESTIGATING"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "updated"
        assert data["alert"]["status"] == "INVESTIGATING"