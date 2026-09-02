"""Tests for event models."""

import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from src.models import (
    RawEvent,
    NormalizedEvent,
    EnrichedEvent,
    Source,
    Destination,
    AssetInfo,
    GeoInfo,
    ThreatIntel,
    EventType,
    Protocol,
    Action,
    Severity,
)


class TestSource:
    """Tests for Source model."""
    
    def test_valid_source(self):
        """Test creating a valid source."""
        source = Source(
            ip="192.168.1.100",
            hostname="PC-01",
            port=45122,
            user="admin",
            mac="00:11:22:33:44:55",
        )
        assert source.ip == "192.168.1.100"
        assert source.hostname == "PC-01"
        assert source.port == 45122
        assert source.user == "admin"
        assert source.mac == "00:11:22:33:44:55"
    
    def test_invalid_ip(self):
        """Test invalid IP address."""
        with pytest.raises(ValidationError):
            Source(ip="999.999.999.999")
        
        with pytest.raises(ValidationError):
            Source(ip="invalid")
    
    def test_invalid_mac(self):
        """Test invalid MAC address."""
        with pytest.raises(ValidationError):
            Source(mac="invalid")
        
        with pytest.raises(ValidationError):
            Source(mac="00:11:22:33:44:ZZ")
    
    def test_invalid_port(self):
        """Test invalid port number."""
        with pytest.raises(ValidationError):
            Source(port=99999)
        
        with pytest.raises(ValidationError):
            Source(port=-1)


class TestDestination:
    """Tests for Destination model."""
    
    def test_valid_destination(self):
        """Test creating a valid destination."""
        dest = Destination(
            ip="192.168.1.200",
            hostname="SERVER-01",
            port=22,
            user="root",
        )
        assert dest.ip == "192.168.1.200"
        assert dest.hostname == "SERVER-01"
        assert dest.port == 22
        assert dest.user == "root"
    
    def test_invalid_ip(self):
        """Test invalid IP address."""
        with pytest.raises(ValidationError):
            Destination(ip="invalid")


class TestRawEvent:
    """Tests for RawEvent model."""
    
    def test_create_raw_event(self):
        """Test creating a raw event."""
        event = RawEvent(
            raw_source="syslog",
            raw_content="Test log message",
            source_host="firewall-01",
        )
        assert event.raw_source == "syslog"
        assert event.raw_content == "Test log message"
        assert event.source_host == "firewall-01"
        assert event.collected_at is not None
    
    def test_raw_event_with_json(self):
        """Test raw event with JSON content."""
        event = RawEvent(
            raw_source="firewall",
            raw_content='{"src": "1.1.1.1", "dst": "2.2.2.2"}',
            raw_json={"src": "1.1.1.1", "dst": "2.2.2.2"},
        )
        assert event.raw_json["src"] == "1.1.1.1"
        assert event.raw_json["dst"] == "2.2.2.2"


class TestNormalizedEvent:
    """Tests for NormalizedEvent model."""
    
    def test_create_normalized_event(self):
        """Test creating a normalized event."""
        event = NormalizedEvent(
            event_id="EVT-001",
            timestamp=datetime.now(timezone.utc),
            event_type="NETWORK_CONNECTION",
            raw_source="syslog",
            source=Source(ip="192.168.1.10", hostname="PC-01"),
            destination=Destination(ip="192.168.1.20", hostname="SERVER-01"),
            protocol="TCP",
            action="ALLOW",
            severity="INFO",
            tags=["network", "ssh"],
        )
        assert event.event_id == "EVT-001"
        assert event.source.ip == "192.168.1.10"
        assert event.destination.hostname == "SERVER-01"
        assert event.protocol == "TCP"
        assert event.action == "ALLOW"
        assert event.severity == "INFO"
        assert "network" in event.tags
    
    def test_normalized_event_with_warnings(self):
        """Test normalized event with warnings."""
        event = NormalizedEvent(
            event_id="EVT-002",
            timestamp=datetime.now(timezone.utc),
            event_type="LOGIN_FAILURE",
            raw_source="windows",
            source=Source(ip="192.168.1.10"),
            destination=Destination(hostname="DOMAIN-01"),
            normalization_warnings=["Ambiguous timestamp format"],
        )
        assert event.normalization_warnings is not None
        assert "Ambiguous timestamp format" in event.normalization_warnings


class TestEnrichedEvent:
    """Tests for EnrichedEvent model."""
    
    def test_create_enriched_event(self):
        """Test creating an enriched event."""
        normalized = NormalizedEvent(
            event_id="EVT-001",
            timestamp=datetime.now(timezone.utc),
            event_type="NETWORK_CONNECTION",
            raw_source="syslog",
            source=Source(ip="192.168.1.10"),
            destination=Destination(ip="192.168.1.20"),
        )
        
        enriched = EnrichedEvent(
            normalized=normalized,
            source_asset=AssetInfo(
                asset_type="workstation",
                owner="John Doe",
                criticality=5,
            ),
            destination_asset=AssetInfo(
                asset_type="server",
                criticality=9,
            ),
            application_name="SSH",
            enrichment_applied=["asset_info", "protocol_mapping"],
        )
        
        assert enriched.normalized.event_id == "EVT-001"
        assert enriched.source_asset.asset_type == "workstation"
        assert enriched.source_asset.criticality == 5
        assert enriched.destination_asset.criticality == 9
        assert enriched.application_name == "SSH"
        assert "asset_info" in enriched.enrichment_applied
    
    def test_geo_enrichment(self):
        """Test geographic enrichment."""
        normalized = NormalizedEvent(
            event_id="EVT-002",
            timestamp=datetime.now(timezone.utc),
            event_type="NETWORK_CONNECTION",
            raw_source="syslog",
            source=Source(ip="8.8.8.8"),
            destination=Destination(ip="192.168.1.10"),
        )
        
        enriched = EnrichedEvent(
            normalized=normalized,
            source_geo=GeoInfo(
                country="United States",
                country_code="US",
                city="Mountain View",
                latitude=37.4223,
                longitude=-122.0841,
                isp="Google LLC",
            ),
            enrichment_applied=["geo_ip"],
        )
        
        assert enriched.source_geo.country == "United States"
        assert enriched.source_geo.country_code == "US"
        assert enriched.source_geo.isp == "Google LLC"
    
    def test_threat_intel_enrichment(self):
        """Test threat intelligence enrichment."""
        normalized = NormalizedEvent(
            event_id="EVT-003",
            timestamp=datetime.now(timezone.utc),
            event_type="NETWORK_CONNECTION",
            raw_source="syslog",
            source=Source(ip="1.1.1.1"),
            destination=Destination(ip="192.168.1.10"),
        )
        
        enriched = EnrichedEvent(
            normalized=normalized,
            threat_intel=ThreatIntel(
                is_malicious=True,
                reputation_score=85,
                threat_feed="VirusTotal",
                threat_category="scanning",
                confidence=0.92,
            ),
            enrichment_applied=["threat_intel"],
        )
        
        assert enriched.threat_intel.is_malicious is True
        assert enriched.threat_intel.reputation_score == 85
        assert enriched.threat_intel.confidence == 0.92


class TestEventFlows:
    """Test the full flow from raw to enriched."""
    
    def test_full_pipeline(self):
        """Test the complete transformation pipeline."""
        # 1. Collect raw event
        raw = RawEvent(
            raw_source="syslog",
            raw_content="Aug 29 10:30:15 SRC=192.168.1.10 DST=192.168.1.20 PROTO=TCP DPORT=22 ACTION=ALLOW",
            source_host="firewall-01",
        )
        assert raw.raw_content is not None
        
        # 2. Normalize (simulated)
        normalized = NormalizedEvent(
            event_id="EVT-001",
            timestamp=datetime.now(timezone.utc),
            event_type="NETWORK_CONNECTION",
            raw_source=raw.raw_source,
            source=Source(ip="192.168.1.10"),
            destination=Destination(ip="192.168.1.20", port=22),
            protocol="TCP",
            action="ALLOW",
            normalized_fields=["source.ip", "destination.ip", "protocol", "action"],
            raw_message=raw.raw_content,
        )
        assert normalized.source.ip == "192.168.1.10"
        assert normalized.destination.port == 22
        
        # 3. Enrich (simulated)
        enriched = EnrichedEvent(
            normalized=normalized,
            source_asset=AssetInfo(
                asset_type="workstation",
                owner="John Doe",
                criticality=5,
            ),
            destination_asset=AssetInfo(
                asset_type="server",
                criticality=9,
            ),
            application_name="SSH",
            enrichment_applied=["asset_info", "protocol_mapping"],
        )
        assert enriched.source_asset.asset_type == "workstation"
        assert enriched.application_name == "SSH"
        assert len(enriched.enrichment_applied) == 2