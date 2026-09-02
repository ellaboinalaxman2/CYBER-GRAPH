"""Tests for enrichers."""

import pytest
from datetime import datetime, timezone

from src.enrichers import (
    AssetEnricher,
    GeoEnricher,
    ThreatIntelEnricher,
    ProtocolEnricher,
    ContextEnricher,
    EnrichmentPipeline,
)


class TestAssetEnricher:
    """Tests for AssetEnricher."""
    
    def test_asset_enrichment(self):
        """Test asset enrichment."""
        enricher = AssetEnricher()
        
        event = {
            "source_ip": "192.168.1.10",
            "destination_ip": "192.168.1.20",
            "timestamp": "2026-08-29T10:30:15.000Z",
        }
        
        result = enricher.enrich(event)
        
        assert "source_asset" in result
        assert "destination_asset" in result
        assert result["source_asset"]["asset_type"] == "workstation"
        assert result["destination_asset"]["asset_type"] == "server"
        assert "enrichment_applied" in result
        assert "source_asset" in result["enrichment_applied"]
    
    def test_unknown_asset(self):
        """Test enrichment with unknown asset."""
        enricher = AssetEnricher()
        
        event = {
            "source_ip": "192.168.1.999",
            "timestamp": "2026-08-29T10:30:15.000Z",
        }
        
        result = enricher.enrich(event)
        assert "source_asset" not in result
    
    def test_add_asset(self):
        """Test adding an asset."""
        enricher = AssetEnricher()
        enricher.add_asset("192.168.1.100", {
            "asset_type": "workstation",
            "owner": "Test User",
            "criticality": 3,
        })
        
        assert "192.168.1.100" in enricher.assets


class TestGeoEnricher:
    """Tests for GeoEnricher."""
    
    def test_geo_enrichment_public_ip(self):
        """Test geographic enrichment for public IP."""
        enricher = GeoEnricher()
        
        event = {
            "source_ip": "8.8.8.8",
            "timestamp": "2026-08-29T10:30:15.000Z",
        }
        
        result = enricher.enrich(event)
        
        assert "source_geo" in result
        assert result["source_geo"]["country"] == "United States"
        assert result["source_geo"]["city"] == "Mountain View"
    
    def test_geo_enrichment_private_ip(self):
        """Test geographic enrichment for private IP."""
        enricher = GeoEnricher()
        
        event = {
            "source_ip": "192.168.1.10",
            "timestamp": "2026-08-29T10:30:15.000Z",
        }
        
        result = enricher.enrich(event)
        
        assert "source_geo" not in result
    
    def test_add_geo_data(self):
        """Test adding GeoIP data."""
        enricher = GeoEnricher()
        enricher.add_geo_data("192.168.1.100", {
            "country": "Test",
            "country_code": "TT",
            "city": "Test City",
        })
        
        assert "192.168.1.100" in enricher.geo_data


class TestThreatIntelEnricher:
    """Tests for ThreatIntelEnricher."""
    
    def test_threat_intel_enrichment(self):
        """Test threat intelligence enrichment."""
        enricher = ThreatIntelEnricher()
        
        event = {
            "source_ip": "192.168.1.50",
            "timestamp": "2026-08-29T10:30:15.000Z",
        }
        
        result = enricher.enrich(event)
        
        assert "threat_intel" in result
        assert result["threat_intel"]["is_malicious"] is True
        assert result["threat_intel"]["threat_category"] == "brute_force"
    
    def test_unknown_ip(self):
        """Test threat intelligence for unknown IP."""
        enricher = ThreatIntelEnricher()
        
        event = {
            "source_ip": "192.168.1.100",
            "timestamp": "2026-08-29T10:30:15.000Z",
        }
        
        result = enricher.enrich(event)
        assert "threat_intel" not in result
    
    def test_add_threat_intel(self):
        """Test adding threat intelligence."""
        enricher = ThreatIntelEnricher()
        enricher.add_threat_intel("192.168.1.100", {
            "is_malicious": True,
            "reputation_score": 90,
            "threat_category": "malware",
        })
        
        assert "192.168.1.100" in enricher.threat_data


class TestProtocolEnricher:
    """Tests for ProtocolEnricher."""
    
    def test_protocol_from_port(self):
        """Test protocol mapping from port."""
        enricher = ProtocolEnricher()
        
        event = {
            "destination_port": 22,
            "timestamp": "2026-08-29T10:30:15.000Z",
        }
        
        result = enricher.enrich(event)
        
        assert result["protocol"] == "SSH"
        assert result["application_name"] == "SSH"
        assert "protocol_mapping" in result["enrichment_applied"]
    
    def test_protocol_aliases(self):
        """Test protocol alias normalization."""
        enricher = ProtocolEnricher()
        
        event = {
            "protocol": "tcp",
            "timestamp": "2026-08-29T10:30:15.000Z",
        }
        
        result = enricher.enrich(event)
        
        assert result["protocol"] == "TCP"


class TestEnrichmentPipeline:
    """Tests for EnrichmentPipeline."""
    
    def test_full_enrichment(self):
        """Test full enrichment pipeline."""
        pipeline = EnrichmentPipeline()
        
        event = {
            "source_ip": "192.168.1.10",
            "destination_ip": "192.168.1.20",
            "destination_port": 22,
            "timestamp": "2026-08-29T10:30:15.000Z",
            "event_type": "NETWORK_CONNECTION",
        }
        
        result = pipeline.enrich(event)
        
        # Check all enrichments
        assert "source_asset" in result
        assert "destination_asset" in result
        assert "protocol" in result
        assert "application_name" in result
        assert "temporal_context" in result
        assert "event_type_context" in result
        assert len(result["enrichment_applied"]) > 0
    
    def test_pipeline_stats(self):
        """Test pipeline statistics."""
        pipeline = EnrichmentPipeline()
        
        event = {
            "source_ip": "192.168.1.10",
            "timestamp": "2026-08-29T10:30:15.000Z",
        }
        
        pipeline.enrich(event)
        stats = pipeline.get_stats()
        
        assert "pipeline" in stats
        assert stats["pipeline"]["events_enriched"] >= 1
    
    def test_disable_enricher(self):
        """Test disabling an enricher."""
        pipeline = EnrichmentPipeline()
        pipeline.disable_enricher("geo")
        
        event = {
            "source_ip": "8.8.8.8",
            "timestamp": "2026-08-29T10:30:15.000Z",
        }
        
        result = pipeline.enrich(event)
        assert "source_geo" not in result