"""Tests for correlation module."""

import pytest
from datetime import datetime, timedelta

from src.correlation.event_correlator import EventCorrelator
from src.models.event import EventModel
from src.models.incident import IncidentModel


class TestEventCorrelator:
    """Tests for EventCorrelator."""
    
    def test_correlate_brute_force(self):
        """Test brute force correlation."""
        correlator = EventCorrelator()
        
        now = datetime.utcnow()
        events = []
        
        # Create 5 login failures from same source
        for i in range(5):
            events.append({
                "event_id": f"EVT-{i:03d}",
                "timestamp": (now + timedelta(seconds=i * 10)).isoformat() + "Z",
                "event_type": "LOGIN_FAILURE",
                "source_ip": "192.168.1.50",
                "destination_ip": "192.168.1.20",
                "raw_source": "firewall",
                "user": "admin",
            })
        
        incidents = correlator.correlate(events)
        
        assert len(incidents) > 0
        assert incidents[0].attack_type == "Brute Force"
        assert len(incidents[0].event_ids) >= 5
    
    def test_correlate_lateral_movement(self):
        """Test lateral movement correlation."""
        correlator = EventCorrelator()
        
        now = datetime.utcnow()
        events = [
            {
                "event_id": "EVT-001",
                "timestamp": now.isoformat() + "Z",
                "event_type": "LOGIN_SUCCESS",
                "source_ip": "192.168.1.10",
                "destination_ip": "192.168.1.20",
                "raw_source": "windows",
                "user": "admin",
            },
            {
                "event_id": "EVT-002",
                "timestamp": (now + timedelta(seconds=30)).isoformat() + "Z",
                "event_type": "NETWORK_CONNECTION",
                "source_ip": "192.168.1.20",
                "destination_ip": "192.168.1.30",
                "raw_source": "network",
                "protocol": "SSH",
            },
        ]
        
        incidents = correlator.correlate(events)
        
        assert len(incidents) > 0
        assert "lateral_movement" in incidents[0].attack_type.lower()
    
    def test_correlate_time_burst(self):
        """Test time-based correlation."""
        correlator = EventCorrelator()
        
        now = datetime.utcnow()
        events = []
        
        # Create 5 events in quick succession
        for i in range(5):
            events.append({
                "event_id": f"EVT-{i:03d}",
                "timestamp": (now + timedelta(seconds=i * 5)).isoformat() + "Z",
                "event_type": "SYSTEM_EVENT",
                "source_ip": f"192.168.1.{i+10}",
                "destination_ip": "192.168.1.100",
                "raw_source": "system",
            })
        
        incidents = correlator.correlate(events)
        
        assert len(incidents) > 0
        assert "Activity burst" in incidents[0].title