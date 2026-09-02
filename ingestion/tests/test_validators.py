"""Tests for validators."""

import pytest
from datetime import datetime, timezone

from src.validators import (
    SchemaValidator,
    FieldValidator,
    RuleValidator,
    ValidatorPipeline,
    ValidationSeverity,
)


class TestSchemaValidator:
    """Tests for SchemaValidator."""
    
    def test_valid_event(self):
        """Test validation of a valid event."""
        validator = SchemaValidator()
        data = {
            "event_id": "EVT-12345678",
            "timestamp": "2026-08-29T10:30:15.000Z",
            "event_type": "NETWORK_CONNECTION",
            "raw_source": "firewall",
            "source": {"ip": "192.168.1.10"},
            "destination": {"ip": "192.168.1.20", "port": 22},
            "protocol": "TCP",
            "action": "ALLOW",
        }
        
        result = validator.validate(data)
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_missing_required_field(self):
        """Test validation with missing required field."""
        validator = SchemaValidator()
        data = {
            "event_id": "EVT-12345678",
            "timestamp": "2026-08-29T10:30:15.000Z",
            "event_type": "NETWORK_CONNECTION",
            "source": {"ip": "192.168.1.10"},
            "destination": {"ip": "192.168.1.20"},
        }
        
        result = validator.validate(data)
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("raw_source" in str(e) for e in result.errors)
    
    def test_invalid_event_type(self):
        """Test validation with invalid event type."""
        validator = SchemaValidator()
        data = {
            "event_id": "EVT-12345678",
            "timestamp": "2026-08-29T10:30:15.000Z",
            "event_type": "INVALID_TYPE",
            "raw_source": "firewall",
            "source": {"ip": "192.168.1.10"},
            "destination": {"ip": "192.168.1.20"},
        }
        
        result = validator.validate(data)
        # Should have warning for invalid event type
        assert len(result.warnings) > 0


class TestFieldValidator:
    """Tests for FieldValidator."""
    
    def test_valid_string_fields(self):
        """Test validation of string fields."""
        validator = FieldValidator()
        data = {
            "event_id": "EVT-12345678",
            "event_type": "NETWORK_CONNECTION",
            "raw_source": "firewall",
            "message": "Test message",
        }
        
        result = validator.validate(data)
        assert result.is_valid is True
    
    def test_empty_string(self):
        """Test validation with empty string."""
        validator = FieldValidator()
        data = {"event_id": ""}
        
        result = validator.validate(data)
        assert len(result.errors) > 0
        assert any("empty" in str(e).lower() for e in result.errors)
    
    def test_invalid_port(self):
        """Test validation with invalid port."""
        validator = FieldValidator()
        data = {"source_port": 99999}
        
        result = validator.validate(data)
        assert len(result.errors) > 0
        assert any("port" in str(e).lower() for e in result.errors)
    
    def test_invalid_timestamp(self):
        """Test validation with invalid timestamp."""
        validator = FieldValidator()
        data = {"timestamp": "invalid_timestamp"}
        
        result = validator.validate(data)
        assert len(result.errors) > 0
        assert any("timestamp" in str(e).lower() for e in result.errors)


class TestRuleValidator:
    """Tests for RuleValidator."""
    
    def test_dependency_validation(self):
        """Test field dependency validation."""
        validator = RuleValidator()
        data = {
            "destination_port": 22,
            "source": {"ip": "192.168.1.10"},
            # Missing destination
        }
        
        result = validator.validate(data)
        assert len(result.errors) > 0
        assert any("destination" in str(e) for e in result.errors)
    
    def test_severity_warning(self):
        """Test severity warning for DENY action."""
        validator = RuleValidator()
        data = {
            "action": "DENY",
            "severity": "INFO",
            "event_type": "FIREWALL_DENY",
        }
        
        result = validator.validate(data)
        assert len(result.warnings) > 0
        assert any("severity" in str(w).lower() for w in result.warnings)


class TestValidatorPipeline:
    """Tests for ValidatorPipeline."""
    
    def test_valid_event(self):
        """Test validation of a valid event through pipeline."""
        pipeline = ValidatorPipeline()
        data = {
            "event_id": "EVT-12345678",
            "timestamp": "2026-08-29T10:30:15.000Z",
            "event_type": "NETWORK_CONNECTION",
            "raw_source": "firewall",
            "source": {"ip": "192.168.1.10"},
            "destination": {"ip": "192.168.1.20", "port": 22},
            "protocol": "TCP",
            "action": "ALLOW",
        }
        
        result = pipeline.validate(data)
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_invalid_event(self):
        """Test validation of an invalid event."""
        pipeline = ValidatorPipeline()
        data = {
            "event_id": "EVT-12345678",
            "timestamp": "2026-08-29T10:30:15.000Z",
            # Missing required fields
            "source": {"ip": "192.168.1.10"},
        }
        
        result = pipeline.validate(data)
        assert result.is_valid is False
        assert len(result.errors) > 0
    
    def test_get_stats(self):
        """Test getting validation statistics."""
        pipeline = ValidatorPipeline()
        
        # Validate some events
        valid_data = {
            "event_id": "EVT-12345678",
            "timestamp": "2026-08-29T10:30:15.000Z",
            "event_type": "NETWORK_CONNECTION",
            "raw_source": "firewall",
            "source": {"ip": "192.168.1.10"},
            "destination": {"ip": "192.168.1.20"},
        }
        
        pipeline.validate(valid_data)
        stats = pipeline.get_stats()
        
        assert "pipeline" in stats
        assert stats["pipeline"]["events_validated"] >= 1