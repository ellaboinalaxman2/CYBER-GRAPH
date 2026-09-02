"""Tests for MITRE module."""

import pytest
from datetime import datetime

from src.mitre.mitre_data import MitreData
from src.mitre.technique_mapper import TechniqueMapper
from src.mitre.tactic_mapper import TacticMapper
from src.mitre.attack_mapper import AttackMapper


class TestMitreData:
    """Tests for MitreData."""
    
    def test_get_technique(self):
        """Test getting a technique."""
        data = MitreData()
        
        tech = data.get_technique("T1110")
        assert tech is not None
        assert tech.get("id") == "T1110"
        assert "Brute Force" in tech.get("name", "")
    
    def test_get_techniques_by_tactic(self):
        """Test getting techniques by tactic."""
        data = MitreData()
        
        techniques = data.get_techniques_by_tactic("Lateral Movement")
        assert len(techniques) > 0
        assert any("T1021" in t.get("id", "") for t in techniques)
    
    def test_search_techniques(self):
        """Test searching techniques."""
        data = MitreData()
        
        results = data.search_techniques("brute")
        assert len(results) > 0


class TestTechniqueMapper:
    """Tests for TechniqueMapper."""
    
    def test_map_event(self):
        """Test mapping an event."""
        mapper = TechniqueMapper()
        
        event = {"event_type": "LOGIN_FAILURE"}
        techniques = mapper.map_event(event)
        
        assert len(techniques) > 0
        assert "T1110" in techniques
    
    def test_map_attack_type(self):
        """Test mapping an attack type."""
        mapper = TechniqueMapper()
        
        techniques = mapper.map_attack_type("lateral_movement")
        assert len(techniques) > 0
    
    def test_get_techniques_for_incident(self):
        """Test getting techniques for an incident."""
        mapper = TechniqueMapper()
        
        events = [
            {"event_type": "LOGIN_FAILURE"},
            {"event_type": "LOGIN_SUCCESS"},
            {"event_type": "NETWORK_CONNECTION"},
        ]
        
        techniques = mapper.get_techniques_for_incident(events, "lateral_movement")
        assert len(techniques) > 0


class TestTacticMapper:
    """Tests for TacticMapper."""
    
    def test_get_tactics_for_technique(self):
        """Test getting tactics for a technique."""
        mapper = TacticMapper()
        
        tactics = mapper.get_tactics_for_technique("T1110")
        assert "Credential Access" in tactics
    
    def test_get_tactics_for_incident(self):
        """Test getting tactics for an incident."""
        mapper = TacticMapper()
        
        events = [
            {"event_type": "LOGIN_FAILURE"},
            {"event_type": "LOGIN_SUCCESS"},
        ]
        
        result = mapper.get_tactics_for_incident(events, "brute_force")
        assert "tactics" in result
        assert "tactic_coverage" in result


class TestAttackMapper:
    """Tests for AttackMapper."""
    
    def test_map_attack(self):
        """Test mapping an attack."""
        mapper = AttackMapper()
        
        events = [
            {"event_type": "LOGIN_FAILURE", "message": "Failed password"},
            {"event_type": "LOGIN_FAILURE", "message": "Failed password"},
            {"event_type": "LOGIN_SUCCESS", "message": "Successful login"},
            {"event_type": "NETWORK_CONNECTION", "protocol": "SSH"},
        ]
        
        result = mapper.map_attack(events, "lateral_movement")
        
        assert result["status"] == "success"
        assert "techniques" in result
        assert "tactics" in result
        assert "confidence" in result
    
    def test_generate_report(self):
        """Test generating a report."""
        mapper = AttackMapper()
        
        events = [
            {"event_type": "LOGIN_FAILURE"},
            {"event_type": "LOGIN_SUCCESS"},
        ]
        
        result = mapper.map_attack(events, "brute_force")
        report = mapper.generate_report(result)
        
        assert "summary" in report
        assert "techniques" in report
        assert "tactics" in report
        assert "recommendations" in report