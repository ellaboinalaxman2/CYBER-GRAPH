"""Enriched event model - after adding additional context."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from src.models.normalized_event import NormalizedEvent


class AssetInfo(BaseModel):
    """
    Asset enrichment information.
    
    Adds context about the devices involved in the event.
    """
    
    asset_id: Optional[str] = Field(
        None,
        description="Internal asset ID from CMDB",
        examples=["ASSET-001", "SRV-WEB-01"],
    )
    asset_type: Optional[str] = Field(
        None,
        description="Type of asset",
        examples=["workstation", "server", "database", "firewall", "router"],
    )
    owner: Optional[str] = Field(
        None,
        description="Asset owner or responsible person",
        examples=["John Doe", "IT Team"],
    )
    department: Optional[str] = Field(
        None,
        description="Department that owns the asset",
        examples=["Engineering", "Finance", "HR"],
    )
    criticality: Optional[int] = Field(
        None,
        ge=1,
        le=10,
        description="Criticality score (1=lowest, 10=highest)",
        examples=[8, 5, 3],
    )
    business_unit: Optional[str] = Field(
        None,
        description="Business unit",
        examples=["North America", "EMEA"],
    )
    location: Optional[str] = Field(
        None,
        description="Physical location",
        examples=["Data Center A", "Floor 3"],
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Asset tags",
        examples=[["production", "critical"]],
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "asset_id": "ASSET-001",
                "asset_type": "server",
                "owner": "IT Team",
                "department": "Engineering",
                "criticality": 9,
                "location": "Data Center A",
                "tags": ["production", "critical"],
            }
        }


class GeoInfo(BaseModel):
    """
    Geographic enrichment information (for external IPs).
    """
    
    country: Optional[str] = Field(
        None,
        description="Country name",
        examples=["United States", "United Kingdom"],
    )
    country_code: Optional[str] = Field(
        None,
        description="Country code (ISO 3166-1 alpha-2)",
        examples=["US", "GB", "IN"],
        min_length=2,
        max_length=2,
    )
    city: Optional[str] = Field(
        None,
        description="City name",
        examples=["New York", "London", "Mumbai"],
    )
    region: Optional[str] = Field(
        None,
        description="Region or state",
        examples=["NY", "California", "Maharashtra"],
    )
    latitude: Optional[float] = Field(
        None,
        ge=-90.0,
        le=90.0,
        description="Latitude coordinate",
    )
    longitude: Optional[float] = Field(
        None,
        ge=-180.0,
        le=180.0,
        description="Longitude coordinate",
    )
    timezone: Optional[str] = Field(
        None,
        description="Time zone",
        examples=["America/New_York", "Asia/Kolkata"],
    )
    isp: Optional[str] = Field(
        None,
        description="Internet Service Provider",
        examples=["Comcast", "Verizon", "AWS"],
    )
    organization: Optional[str] = Field(
        None,
        description="Organization that owns the IP",
        examples=["Google Inc.", "Microsoft Corp."],
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "country": "United States",
                "country_code": "US",
                "city": "New York",
                "region": "NY",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "timezone": "America/New_York",
                "isp": "Verizon",
            }
        }


class ThreatIntel(BaseModel):
    """
    Threat intelligence enrichment information.
    """
    
    is_malicious: bool = Field(
        default=False,
        description="Flagged as malicious by threat intelligence",
    )
    reputation_score: Optional[int] = Field(
        None,
        ge=0,
        le=100,
        description="Reputation score (0=benign, 100=malicious)",
    )
    threat_feed: Optional[str] = Field(
        None,
        description="Threat feed source",
        examples=["VirusTotal", "AlienVault OTX", "AbuseIPDB"],
    )
    threat_category: Optional[str] = Field(
        None,
        description="Threat category",
        examples=["malware", "phishing", "scanning", "botnet"],
    )
    confidence: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Confidence score (0-1)",
        examples=[0.95, 0.75],
    )
    threat_families: List[str] = Field(
        default_factory=list,
        description="Threat family names",
        examples=[["Mirai", "Gafgyt"]],
    )
    first_seen: Optional[datetime] = Field(
        None,
        description="When the threat was first seen",
    )
    last_seen: Optional[datetime] = Field(
        None,
        description="When the threat was last seen",
    )
    references: List[str] = Field(
        default_factory=list,
        description="Reference URLs",
        examples=[["https://www.virustotal.com/gui/ip-address/1.1.1.1"]],
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_malicious": True,
                "reputation_score": 85,
                "threat_feed": "VirusTotal",
                "threat_category": "scanning",
                "confidence": 0.92,
                "threat_families": ["Botnet"],
                "first_seen": "2026-01-01T00:00:00Z",
                "references": ["https://www.virustotal.com/gui/ip-address/1.1.1.1"],
            }
        }


class EnrichedEvent(BaseModel):
    """
    Enriched security event.
    
    Adds asset information, geographic data, threat intelligence,
    and other contextual information to the normalized event.
    """
    
    # The base normalized event
    normalized: NormalizedEvent = Field(
        ...,
        description="Base normalized event",
    )
    
    # Enrichment fields
    source_asset: Optional[AssetInfo] = Field(
        None,
        description="Source asset information",
    )
    destination_asset: Optional[AssetInfo] = Field(
        None,
        description="Destination asset information",
    )
    source_geo: Optional[GeoInfo] = Field(
        None,
        description="Source geographic information (for external IPs)",
    )
    destination_geo: Optional[GeoInfo] = Field(
        None,
        description="Destination geographic information (for external IPs)",
    )
    threat_intel: Optional[ThreatIntel] = Field(
        None,
        description="Threat intelligence information",
    )
    application_name: Optional[str] = Field(
        None,
        description="Identified application or service",
        examples=["SSH", "HTTP", "MySQL", "Active Directory"],
    )
    application_version: Optional[str] = Field(
        None,
        description="Application version if available",
        examples=["8.0.1", "3.2.1"],
    )
    
    # Enrichment metadata
    enrichment_applied: List[str] = Field(
        default_factory=list,
        description="List of enrichment types applied",
        examples=[["asset_info", "geo_ip", "protocol_mapping"]],
    )
    enrichment_warnings: Optional[List[str]] = Field(
        None,
        description="Warnings during enrichment",
        examples=[["Asset not found in CMDB for IP 192.168.1.10"]],
    )
    enriched_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When enrichment was performed",
    )
    enrichments_failed: List[str] = Field(
        default_factory=list,
        description="Enrichments that failed",
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "normalized": {
                    "event_id": "EVT-12345678",
                    "timestamp": "2026-08-29T10:30:15.000Z",
                    "event_type": "NETWORK_CONNECTION",
                    "raw_source": "syslog",
                    "source": {
                        "ip": "192.168.1.10",
                        "hostname": "PC-01",
                        "port": 45122,
                    },
                    "destination": {
                        "ip": "192.168.1.20",
                        "hostname": "SERVER-01",
                        "port": 22,
                    },
                    "protocol": "TCP",
                    "action": "ALLOW",
                    "severity": "INFO",
                },
                "source_asset": {
                    "asset_type": "workstation",
                    "owner": "John Doe",
                    "department": "Engineering",
                    "criticality": 5,
                    "tags": ["windows", "user-workstation"],
                },
                "destination_asset": {
                    "asset_type": "server",
                    "owner": "IT Team",
                    "department": "Engineering",
                    "criticality": 9,
                    "tags": ["linux", "production"],
                },
                "application_name": "SSH",
                "enrichment_applied": ["asset_info", "protocol_mapping"],
                "enriched_at": "2026-08-29T10:30:15.500Z",
            }
        }