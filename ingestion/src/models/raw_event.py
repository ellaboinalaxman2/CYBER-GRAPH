"""Raw event model - what comes directly from collectors."""

from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime

# Source types for raw events
RawSourceType = Literal[
    "syslog",
    "windows",
    "linux",
    "network",
    "firewall",
    "application",
    "custom",
]


class RawEvent(BaseModel):
    """
    Raw event from a collector before any processing.
    
    This represents the original, unprocessed data as received from the source.
    No parsing, normalization, or enrichment has been applied.
    """
    
    raw_source: RawSourceType = Field(
        ...,
        description="Type of source that generated this event",
        examples=["syslog", "firewall", "windows"],
    )
    raw_content: str = Field(
        ...,
        description="Raw log content (original message)",
        examples=["Aug 29 10:30:15 firewall sshd[1234]: Failed password for admin from 192.168.1.50"],
        min_length=1,
    )
    raw_json: Optional[Dict[str, Any]] = Field(
        None,
        description="Raw JSON payload if the source provides structured data",
        examples=[{"src": "192.168.1.10", "dst": "192.168.1.20", "action": "ALLOW"}],
    )
    collected_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the collector received this event (UTC)",
    )
    source_host: Optional[str] = Field(
        None,
        description="Host identifier that sent this event",
        examples=["firewall-01", "192.168.1.1:514"],
    )
    original_timestamp: Optional[str] = Field(
        None,
        description="Original timestamp string from the source (before normalization)",
        examples=["Aug 29 10:30:15", "2026-08-29T10:30:15Z"],
    )
    collection_metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata about the collection process",
        examples=[{"interface": "eth0", "batch_id": "BATCH-001"}],
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "raw_source": "syslog",
                "raw_content": "Aug 29 10:30:15 firewall sshd[1234]: Failed password for admin from 192.168.1.50",
                "collected_at": "2026-08-29T10:30:15.123Z",
                "source_host": "firewall-01.example.com",
                "original_timestamp": "Aug 29 10:30:15",
                "collection_metadata": {"interface": "eth0", "batch_id": "BATCH-001"},
            }
        }