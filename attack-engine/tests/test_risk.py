"""Tests for risk module."""

import pytest
from datetime import datetime

from src.risk.risk_scoring import RiskScorer
from src.risk.severity import SeverityCalculator, SeverityLevel
from src.risk.asset_criticality import AssetCriticalityManager
from src.risk.risk_rules import RiskRulesEngine
from src.risk.risk_engine import RiskEngine


class TestAssetCriticality:
    """Tests for AssetCriticalityManager."""
    
    def test_get_criticality(self):
        """Test getting criticality."""
        manager = AssetCriticalityManager()
        
        score = manager.get_criticality_score("database")
        assert score >= 90
        
        score = manager.get_criticality_score("workstation")
        assert score < 50
    
    def test_get_max_criticality(self):
        """Test getting max criticality."""
        manager = AssetCriticalityManager()
        
        nodes = ["database-01", "pc-01", "server-01"]
        max_score = manager.get_max_criticality(nodes)
        
        assert max_score >= 90


class TestSeverityCalculator:
    """Tests for SeverityCalculator."""
    
    def test_calculate_severity(self):
        """Test severity calculation."""
        calculator = SeverityCalculator()
        
        assert calculator.calculate(10) == SeverityLevel.LOW
        assert calculator.calculate(30) == SeverityLevel.MEDIUM
        assert calculator.calculate(60) == SeverityLevel.HIGH
        assert calculator.calculate(80) == SeverityLevel.CRITICAL
    
    def test_get_color(self):
        """Test getting severity color."""
        calculator = SeverityCalculator()
        
        assert calculator.get_severity_color(SeverityLevel.LOW) is not None
        assert calculator.get_severity_color(SeverityLevel.CRITICAL) is not None


class TestRiskScorer:
    """Tests for RiskScorer."""
    
    def test_calculate_risk(self):
        """Test risk calculation."""
        scorer = RiskScorer()
        
        result = scorer.calculate(
            anomaly_score=0.85,
            nodes=["database-01", "server-01"],
            attack_type="lateral_movement",
            event_severity="HIGH",
        )
        
        assert "risk_score" in result
        assert result["risk_score"] > 50
        assert "components" in result
    
    def test_get_risk_level(self):
        """Test getting risk level."""
        scorer = RiskScorer()
        
        assert scorer.get_risk_level(90)["level"] == "CRITICAL"
        assert scorer.get_risk_level(75)["level"] == "HIGH"
        assert scorer.get_risk_level(50)["level"] == "MEDIUM"
        assert scorer.get_risk_level(20)["level"] == "LOW"


class TestRiskRules:
    """Tests for RiskRulesEngine."""
    
    def test_apply_rules(self):
        """Test applying risk rules."""
        engine = RiskRulesEngine()
        
        context = {
            "anomaly_score": 0.85,
            "asset_criticality": 90,
            "attack_type": "lateral_movement",
            "failed_logins": 10,
            "file_access": True,
            "network_connection": True,
        }
        
        result = engine.apply_rules(context)
        
        assert "applied_rules" in result
        assert "total_modifier" in result


class TestRiskEngine:
    """Tests for RiskEngine."""
    
    def test_assess(self):
        """Test risk assessment."""
        engine = RiskEngine()
        
        incident = {
            "incident_id": "INC-001",
            "attack_type": "lateral_movement",
            "severity": "HIGH",
            "nodes": ["server-01", "db-01"],
        }
        
        events = [
            {"event_id": "EVT-001", "event_type": "LOGIN_FAILURE", "source_ip": "192.168.1.50"},
            {"event_id": "EVT-002", "event_type": "LOGIN_SUCCESS", "source_ip": "192.168.1.50"},
            {"event_id": "EVT-003", "event_type": "NETWORK_CONNECTION", "source_ip": "192.168.1.20"},
        ]
        
        predictions = [
            {"node_id": "server-01", "anomaly_score": 0.85},
            {"node_id": "db-01", "anomaly_score": 0.95},
        ]
        
        result = engine.assess(incident, events, predictions)
        
        assert "risk_score" in result
        assert "severity" in result
        assert "recommendations" in result