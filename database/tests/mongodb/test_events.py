"""Tests for event operations."""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


class TestEventEndpoints:
    """Test event CRUD endpoints."""
    
    def test_create_event(self):
        """Test creating an event."""
        event_data = {
            "event_id": "EVT-TEST-001",
            "timestamp": "2026-08-29T10:30:15.000Z",
            "source_ip": "192.168.1.10",
            "destination_ip": "192.168.1.20",
            "event_type": "NETWORK_CONNECTION",
            "raw_source": "firewall",
            "severity": "INFO",
        }
        
        response = client.post("/api/v1/events/", json=event_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "created"
        assert data["event"]["event_id"] == "EVT-TEST-001"
    
    def test_get_event(self):
        """Test getting an event."""
        # First create an event
        event_data = {
            "event_id": "EVT-TEST-002",
            "timestamp": "2026-08-29T10:30:15.000Z",
            "source_ip": "192.168.1.10",
            "destination_ip": "192.168.1.20",
            "event_type": "LOGIN_FAILURE",
            "raw_source": "syslog",
        }
        client.post("/api/v1/events/", json=event_data)
        
        # Then get it
        response = client.get("/api/v1/events/EVT-TEST-002")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["event"]["event_id"] == "EVT-TEST-002"
        assert data["event"]["event_type"] == "LOGIN_FAILURE"
    
    def test_get_events(self):
        """Test listing events."""
        # Create multiple events
        for i in range(3):
            event_data = {
                "event_id": f"EVT-TEST-00{i}",
                "timestamp": "2026-08-29T10:30:15.000Z",
                "source_ip": f"192.168.1.{i+10}",
                "destination_ip": "192.168.1.20",
                "event_type": "NETWORK_CONNECTION",
                "raw_source": "firewall",
            }
            client.post("/api/v1/events/", json=event_data)
        
        response = client.get("/api/v1/events/?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "events" in data
        assert "pagination" in data
    
    def test_get_event_stats(self):
        """Test getting event statistics."""
        response = client.get("/api/v1/events/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "stats" in data
        assert "total_events" in data["stats"]
    
    def test_update_event(self):
        """Test updating an event."""
        # First create an event
        event_data = {
            "event_id": "EVT-TEST-003",
            "timestamp": "2026-08-29T10:30:15.000Z",
            "source_ip": "192.168.1.10",
            "destination_ip": "192.168.1.20",
            "event_type": "NETWORK_CONNECTION",
            "raw_source": "firewall",
        }
        client.post("/api/v1/events/", json=event_data)
        
        # Update it
        update_data = {
            "severity": "HIGH",
            "message": "Updated event",
        }
        response = client.put("/api/v1/events/EVT-TEST-003", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "updated"
        assert data["event"]["severity"] == "HIGH"
        assert data["event"]["message"] == "Updated event"
    
    def test_delete_event(self):
        """Test deleting an event."""
        # First create an event
        event_data = {
            "event_id": "EVT-TEST-004",
            "timestamp": "2026-08-29T10:30:15.000Z",
            "source_ip": "192.168.1.10",
            "destination_ip": "192.168.1.20",
            "event_type": "NETWORK_CONNECTION",
            "raw_source": "firewall",
        }
        client.post("/api/v1/events/", json=event_data)
        
        # Delete it
        response = client.delete("/api/v1/events/EVT-TEST-004")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "deleted"
        assert data["event_id"] == "EVT-TEST-004"
        
        # Verify it's gone
        response = client.get("/api/v1/events/EVT-TEST-004")
        assert response.status_code == 404