"""Normalized event model - after parsing and normalization."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from src.models.common import Source, Destination, EventType, Protocol, Action, Severity, Metadata


class NormalizedEvent(BaseModel):
    """
    Normalized security event - the canonical format.
    
    This is the contract that all downstream consumers (M3, M4, M5) use.
    All sources produce the same structure after parsing and normalization.
    """
    
    # Core metadata
    event_id: str = Field(
        ...,
        description="Unique event identifier",
        min_length=4,
        max_length=64,
    )
    timestamp: datetime = Field(
        ...,
        description="Normalized timestamp in UTC",
    )
    event_type: EventType = Field(
        ...,
        description="Normalized event type",
    )
    raw_source: str = Field(
        ...,
        description="Original source type",
    )
    
    # Network information
    source: Source = Field(
        ...,
        description="Normalized source information",
    )
    destination: Destination = Field(
        ...,
        description="Normalized destination information",
    )
    protocol: Optional[Protocol] = Field(
        None,
        description="Normalized protocol",
    )
    
    # Action and severity
    action: Optional[Action] = Field(
        None,
        description="Normalized action",
    )
    severity: Optional[Severity] = Field(
        None,
        description="Event severity level",
    )
    
    # Additional context
    raw_message: Optional[str] = Field(
        None,
        description="Original raw message for reference",
    )
    normalized_fields: List[str] = Field(
        default_factory=list,
        description="List of fields that were normalized",
        examples=[["timestamp", "source.ip", "destination.ip", "protocol", "action"]],
    )
    normalization_warnings: Optional[List[str]] = Field(
        None,
        description="Warnings during normalization (non-fatal issues)",
        examples=[["Ambiguous timestamp format, used fallback parser"]],
    )
    
    # Additional metadata
    original_timestamp: Optional[str] = Field(
        None,
        description="Original timestamp before normalization",
    )
    source_host: Optional[str] = Field(
        None,
        description="Host that sent the original event",
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Tags for categorization",
        examples=[["network", "lateral-movement"]],
    )
    extra: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional normalized fields not covered by schema",
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "EVT-12345678",
                "timestamp": "2026-08-29T10:30:15.000Z",
                "event_type": "NETWORK_CONNECTION",
                "raw_source": "syslog",
                "source": {
                    "ip": "192.168.1.10",
                    "hostname": "PC-01",
                    "port": 45122,
                    "user": "admin",
                },
                "destination": {
                    "ip": "192.168.1.20",
                    "hostname": "SERVER-01",
                    "port": 22,
                },
                "protocol": "TCP",
                "action": "ALLOW",
                "severity": "INFO",
                "raw_message": "Aug 29 10:30:15 SRC=192.168.1.10 DST=192.168.1.20 PROTO=TCP DPORT=22 ACTION=ALLOW",
                "normalized_fields": ["timestamp", "source.ip", "destination.ip", "protocol", "action"],
                "tags": ["network", "ssh"],
            }
        }