"""Tests for parsers."""

import pytest
from datetime import datetime

from src.parsers import (
    SyslogParser,
    FirewallParser,
    WindowsParser,
    LinuxParser,
    JSONParser,
)
from src.models.raw_event import RawEvent


class TestSyslogParser:
    """Tests for SyslogParser."""
    
    def test_supports(self):
        """Test parser support check."""
        assert SyslogParser.supports("syslog") is True
        assert SyslogParser.supports("syslog-ng") is True
        assert SyslogParser.supports("firewall") is False
    
    def test_parse_rfc3164(self):
        """Test parsing RFC 3164 syslog format."""
        parser = SyslogParser()
        raw = RawEvent(
            raw_source="syslog",
            raw_content='<34>Aug 29 10:30:15 firewall sshd[1234]: Failed password for admin from 192.168.1.50',
            source_host="firewall-01",
        )
        
        result = parser.parse(raw)
        assert result is not None
        assert result["format"] == "rfc3164"
        assert result["tag"] == "sshd"
        assert "Failed password" in result["message"]
    
    def test_parse_rfc5424(self):
        """Test parsing RFC 5424 syslog format."""
        parser = SyslogParser()
        raw = RawEvent(
            raw_source="syslog",
            raw_content='<34>1 2026-08-29T10:30:15Z firewall sshd 1234 ID47 [origin host="firewall-01"] Failed password for admin',
            source_host="firewall-01",
        )
        
        result = parser.parse(raw)
        assert result is not None
        assert result["format"] == "rfc5424"
        assert result["application"] == "sshd"
        assert "Failed password" in result["message"]
    
    def test_parse_fallback(self):
        """Test fallback parsing."""
        parser = SyslogParser()
        raw = RawEvent(
            raw_source="syslog",
            raw_content='SRC=192.168.1.10 DST=192.168.1.20 PROTO=TCP ACTION=ALLOW',
            source_host="firewall-01",
        )
        
        result = parser.parse(raw)
        assert result is not None
        assert result.get("src") == "192.168.1.10"
        assert result.get("dst") == "192.168.1.20"


class TestFirewallParser:
    """Tests for FirewallParser."""
    
    def test_supports(self):
        """Test parser support check."""
        assert FirewallParser.supports("firewall") is True
        assert FirewallParser.supports("asa") is True
        assert FirewallParser.supports("syslog") is False
    
    def test_parse_json(self):
        """Test parsing JSON firewall log."""
        parser = FirewallParser()
        raw = RawEvent(
            raw_source="firewall",
            raw_content='{"timestamp":"2026-08-29T10:30:15Z","src":"192.168.1.10","dst":"192.168.1.20","proto":"TCP","dport":22,"action":"ALLOW"}',
            source_host="firewall-01",
        )
        
        result = parser.parse(raw)
        assert result is not None
        assert result["format"] == "json"
        assert result["source_ip"] == "192.168.1.10"
        assert result["destination_ip"] == "192.168.1.20"
        assert result["protocol"] == "TCP"
    
    def test_parse_text_kv(self):
        """Test parsing text key-value firewall log."""
        parser = FirewallParser()
        raw = RawEvent(
            raw_source="firewall",
            raw_content='SRC=192.168.1.10 DST=192.168.1.20 PROTO=TCP DPORT=22 ACTION=ALLOW',
            source_host="firewall-01",
        )
        
        result = parser.parse(raw)
        assert result is not None
        assert result["format"] == "text_kv"
        assert result["source_ip"] == "192.168.1.10"
        assert result["destination_ip"] == "192.168.1.20"
        assert result["action"] == "ALLOW"
    
    def test_parse_cisco_asa(self):
        """Test parsing Cisco ASA format."""
        parser = FirewallParser()
        raw = RawEvent(
            raw_source="firewall",
            raw_content='%ASA-6-302013: Built outbound TCP connection 12345 from 192.168.1.10/45122 to 192.168.1.20/22',
            source_host="firewall-01",
        )
        
        result = parser.parse(raw)
        assert result is not None
        assert result["format"] == "cisco_asa"
        assert result["source_ip"] == "192.168.1.10"
        assert result["destination_ip"] == "192.168.1.20"
        assert result["action"] == "ALLOW"


class TestWindowsParser:
    """Tests for WindowsParser."""
    
    def test_supports(self):
        """Test parser support check."""
        assert WindowsParser.supports("windows") is True
        assert WindowsParser.supports("winlog") is True
        assert WindowsParser.supports("syslog") is False
    
    def test_parse_json(self):
        """Test parsing JSON Windows event."""
        parser = WindowsParser()
        raw = RawEvent(
            raw_source="windows",
            raw_content='{"timestamp":"2026-08-29T10:30:15Z","event_id":4624,"log_name":"Security","message":"An account was successfully logged on.","account_name":"john.doe","source_ip":"192.168.1.10"}',
            source_host="windows-host",
        )
        
        result = parser.parse(raw)
        assert result is not None
        assert result["format"] == "json"
        assert result["event_id"] == 4624
        assert result["event_type"] == "LOGIN_SUCCESS"
        assert result["account_name"] == "john.doe"
    
    def test_parse_text(self):
        """Test parsing text Windows event."""
        parser = WindowsParser()
        raw = RawEvent(
            raw_source="windows",
            raw_content='Log Name: Security, Source: Microsoft-Windows-Security-Auditing, Event ID: 4625, Account Name: admin, Source IP: 192.168.1.50',
            source_host="windows-host",
        )
        
        result = parser.parse(raw)
        assert result is not None
        assert result["format"] == "text"
        assert result["event_id"] == "4625"
        assert result["event_type"] == "LOGIN_FAILURE"


class TestLinuxParser:
    """Tests for LinuxParser."""
    
    def test_supports(self):
        """Test parser support check."""
        assert LinuxParser.supports("linux") is True
        assert LinuxParser.supports("auth") is True
        assert LinuxParser.supports("windows") is False
    
    def test_parse_auth_log(self):
        """Test parsing authentication log."""
        parser = LinuxParser()
        raw = RawEvent(
            raw_source="linux",
            raw_content='Aug 29 10:30:15 server01 sshd[1234]: Failed password for invalid user admin from 192.168.1.50 port 45122 ssh2',
            source_host="linux-host",
        )
        
        result = parser.parse(raw)
        assert result is not None
        assert result["format"] == "auth_log"
        assert result["event_type"] == "LOGIN_FAILURE"
        assert result["user"] == "admin"
        assert result["source_ip"] == "192.168.1.50"
    
    def test_parse_syslog(self):
        """Test parsing system log."""
        parser = LinuxParser()
        raw = RawEvent(
            raw_source="linux",
            raw_content='Aug 29 10:30:15 server01 kernel: [12345.678] Firewall: *TCP_IN Blocked* SRC=192.168.1.10 DST=192.168.1.20',
            source_host="linux-host",
        )
        
        result = parser.parse(raw)
        assert result is not None
        assert result["format"] == "syslog"
        assert result["tag"] == "kernel"


class TestJSONParser:
    """Tests for JSONParser."""
    
    def test_supports(self):
        """Test parser support check."""
        assert JSONParser.supports("json") is True
        assert JSONParser.supports("application") is True
    
    def test_parse_json(self):
        """Test parsing generic JSON."""
        parser = JSONParser()
        raw = RawEvent(
            raw_source="application",
            raw_content='{"timestamp":"2026-08-29T10:30:15Z","user":"john.doe","action":"login","ip":"192.168.1.10"}',
            source_host="app-host",
        )
        
        result = parser.parse(raw)
        assert result is not None
        assert result["format"] == "json"
        assert result["user"] == "john.doe"
        assert result["action"] == "login"
    
    def test_custom_mappings(self):
        """Test custom field mappings."""
        mappings = {
            "user": "username",
            "ip": "source_ip",
        }
        parser = JSONParser(field_mappings=mappings)
        raw = RawEvent(
            raw_source="application",
            raw_content='{"user":"john.doe","ip":"192.168.1.10"}',
            source_host="app-host",
        )
        
        result = parser.parse(raw)
        assert result is not None
        assert result["username"] == "john.doe"
        assert result["source_ip"] == "192.168.1.10"
    
    def test_extract_json_from_text(self):
        """Test extracting JSON from text."""
        parser = JSONParser()
        raw = RawEvent(
            raw_source="application",
            raw_content='Log: {"timestamp":"2026-08-29T10:30:15Z","user":"john.doe"}',
            source_host="app-host",
        )
        
        result = parser.parse(raw)
        assert result is not None
        assert result["user"] == "john.doe"