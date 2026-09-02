"""Tests for normalizers."""

import pytest
from datetime import datetime, timezone

from src.normalizers import (
    FieldMapper,
    TimestampNormalizer,
    IPNormalizer,
    ProtocolNormalizer,
    EventTypeMapper,
    EventNormalizer,
)


class TestFieldMapper:
    """Tests for FieldMapper."""
    
    def test_basic_mapping(self):
        """Test basic field mapping."""
        mapper = FieldMapper()
        data = {
            "src": "192.168.1.10",
            "dst": "192.168.1.20",
            "proto": "TCP",
            "action": "ALLOW",
        }
        
        result = mapper.normalize(data)
        assert result["source_ip"] == "192.168.1.10"
        assert result["destination_ip"] == "192.168.1.20"
        assert result["protocol"] == "TCP"
        assert result["action"] == "ALLOW"
    
    def test_custom_mapping(self):
        """Test custom field mapping."""
        mapper = FieldMapper()
        mapper.add_mapping("custom_field", "standard_field")
        
        data = {"custom_field": "test_value"}
        result = mapper.normalize(data)
        assert result["standard_field"] == "test_value"
    
    def test_keep_unknown(self):
        """Test keeping unknown fields."""
        mapper = FieldMapper(keep_unknown=True)
        data = {"known": "value", "unknown": "test"}
        
        result = mapper.normalize(data)
        assert "unknown" in result


class TestTimestampNormalizer:
    """Tests for TimestampNormalizer."""
    
    def test_normalize_iso_timestamp(self):
        """Test normalizing ISO timestamp."""
        normalizer = TimestampNormalizer()
        data = {"timestamp": "2026-08-29T10:30:15Z"}
        
        result = normalizer.normalize(data)
        assert "timestamp" in result
        assert "2026-08-29T10:30:15" in result["timestamp"]
    
    def test_normalize_rfc3164_timestamp(self):
        """Test normalizing RFC 3164 timestamp."""
        normalizer = TimestampNormalizer()
        data = {"timestamp": "Aug 29 10:30:15"}
        
        result = normalizer.normalize(data)
        assert "timestamp" in result
        assert result["_normalized_timestamp_from"] == "timestamp"
    
    def test_normalize_unix_timestamp(self):
        """Test normalizing Unix timestamp."""
        normalizer = TimestampNormalizer()
        data = {"timestamp": 1700000000}
        
        result = normalizer.normalize(data)
        assert "timestamp" in result


class TestIPNormalizer:
    """Tests for IPNormalizer."""
    
    def test_valid_ipv4(self):
        """Test valid IPv4 address."""
        normalizer = IPNormalizer()
        data = {"ip": "192.168.1.10"}
        
        result = normalizer.normalize(data)
        assert result["ip"] == "192.168.1.10"
        assert result["_ip_normalized"] is True
    
    def test_invalid_ip(self):
        """Test invalid IP address."""
        normalizer = IPNormalizer()
        data = {"ip": "invalid_ip"}
        
        result = normalizer.normalize(data)
        assert "_ip_normalization_error" in result
    
    def test_private_ip_detection(self):
        """Test private IP detection."""
        normalizer = IPNormalizer()
        assert normalizer.is_private_ip("192.168.1.10") is True
        assert normalizer.is_private_ip("10.0.0.1") is True
        assert normalizer.is_private_ip("8.8.8.8") is False


class TestProtocolNormalizer:
    """Tests for ProtocolNormalizer."""
    
    def test_protocol_mapping(self):
        """Test protocol name mapping."""
        normalizer = ProtocolNormalizer()
        
        # Test various protocol names
        test_cases = [
            ("tcp", "TCP"),
            ("TCP", "TCP"),
            ("udp", "UDP"),
            ("http", "HTTP"),
            ("ssh", "SSH"),
        ]
        
        for input_proto, expected in test_cases:
            data = {"protocol": input_proto}
            result = normalizer.normalize(data)
            assert result["protocol"] == expected
    
    def test_protocol_from_port(self):
        """Test protocol inference from port."""
        normalizer = ProtocolNormalizer(use_port_mapping=True)
        
        data = {"destination_port": 22}
        result = normalizer.normalize(data)
        assert result["protocol"] == "SSH"
        
        data = {"dport": 443}
        result = normalizer.normalize(data)
        assert result["protocol"] == "HTTPS"


class TestEventTypeMapper:
    """Tests for EventTypeMapper."""
    
    def test_event_type_mapping(self):
        """Test event type name mapping."""
        mapper = EventTypeMapper()
        
        test_cases = [
            ("login", "LOGIN_SUCCESS"),
            ("login_success", "LOGIN_SUCCESS"),
            ("login_failure", "LOGIN_FAILURE"),
            ("logout", "LOGOUT"),
            ("connection", "NETWORK_CONNECTION"),
            ("allow", "FIREWALL_ALLOW"),
            ("deny", "FIREWALL_DENY"),
        ]
        
        for input_type, expected in test_cases:
            data = {"event_type": input_type}
            result = mapper.normalize(data)
            assert result["event_type"] == expected
    
    def test_windows_event_id_mapping(self):
        """Test Windows Event ID mapping."""
        mapper = EventTypeMapper()
        
        data = {"event_id": 4624}
        result = mapper.normalize(data)
        assert result["event_type"] == "LOGIN_SUCCESS"
        
        data = {"event_id": 4625}
        result = mapper.normalize(data)
        assert result["event_type"] == "LOGIN_FAILURE"


class TestEventNormalizer:
    """Tests for EventNormalizer."""
    
    def test_full_normalization(self):
        """Test full event normalization."""
        normalizer = EventNormalizer()
        
        data = {
            "src": "192.168.1.10",
            "dst": "192.168.1.20",
            "sport": 45122,
            "dport": 22,
            "proto": "tcp",
            "action": "allow",
            "event_type": "login",
            "timestamp": "2026-08-29T10:30:15Z",
        }
        
        result = normalizer.normalize(data)
        
        # Check all normalized fields
        assert result["source_ip"] == "192.168.1.10"
        assert result["destination_ip"] == "192.168.1.20"
        assert result["source_port"] == 45122
        assert result["destination_port"] == 22
        assert result["protocol"] == "TCP"
        assert result["action"] == "allow"
        assert result["event_type"] == "LOGIN_SUCCESS"
        assert "timestamp" in result
        
        # Check normalization metadata
        assert "_normalization_steps" in result
        assert len(result["_normalization_steps"]) > 0
    
    def test_normalize_batch(self):
        """Test batch normalization."""
        normalizer = EventNormalizer()
        
        data_list = [
            {"src": "192.168.1.10", "dst": "192.168.1.20", "proto": "tcp"},
            {"src": "10.0.0.1", "dst": "10.0.0.2", "proto": "udp"},
        ]
        
        results = normalizer.normalize_batch(data_list)
        assert len(results) == 2
        for result in results:
            assert "source_ip" in result
            assert "destination_ip" in result
            assert "protocol" in result