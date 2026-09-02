"""Event model for MongoDB."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


class EventModel(BaseModel):
    """MongoDB event document model."""
    
    event_id: str = Field(..., description="Unique event identifier")
    timestamp: datetime = Field(..., description="Event timestamp")
    source_ip: Optional[str] = Field(None, description="Source IP address")
    destination_ip: Optional[str] = Field(None, description="Destination IP address")
    source_hostname: Optional[str] = Field(None, description="Source hostname")
    destination_hostname: Optional[str] = Field(None, description="Destination hostname")
    source_port: Optional[int] = Field(None, description="Source port")
    destination_port: Optional[int] = Field(None, description="Destination port")
    protocol: Optional[str] = Field(None, description="Network protocol")
    event_type: str = Field(..., description="Type of security event")
    severity: Optional[str] = Field(None, description="Event severity")
    action: Optional[str] = Field(None, description="Action taken")
    raw_source: str = Field(..., description="Original source type")
    user: Optional[str] = Field(None, description="Username")
    message: Optional[str] = Field(None, description="Event message")
    tags: List[str] = Field(default_factory=list, description="Event tags")
    processed_at: datetime = Field(default_factory=datetime.utcnow, description="Processing timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "EVT-12345678",
                "timestamp": "2026-08-29T10:30:15.000Z",
                "source_ip": "192.168.1.10",
                "destination_ip": "192.168.1.20",
                "source_hostname": "PC-01",
                "destination_hostname": "SERVER-01",
                "source_port": 45122,
                "destination_port": 22,
                "protocol": "TCP",
                "event_type": "NETWORK_CONNECTION",
                "severity": "INFO",
                "action": "ALLOW",
                "raw_source": "firewall",
                "user": "admin",
                "message": "SSH connection established",
                "tags": ["network", "ssh"],
            }
        }
    
    @validator('timestamp', pre=True)
    def parse_timestamp(cls, v):
        """Parse timestamp to datetime."""
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                return datetime.utcnow()
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB."""
        data = self.dict()
        if isinstance(data.get('timestamp'), datetime):
            data['timestamp'] = data['timestamp'].isoformat() + 'Z'
        return data