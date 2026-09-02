"""Event model for Member 5 - Attack Engine."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


class EventModel(BaseModel):
    """Security event model."""
    
    event_id: str = Field(..., description="Unique event identifier")
    timestamp: datetime = Field(..., description="Event timestamp")
    event_type: str = Field(..., description="Type of security event")
    source_ip: Optional[str] = Field(None, description="Source IP address")
    destination_ip: Optional[str] = Field(None, description="Destination IP address")
    source_hostname: Optional[str] = Field(None, description="Source hostname")
    destination_hostname: Optional[str] = Field(None, description="Destination hostname")
    source_port: Optional[int] = Field(None, description="Source port")
    destination_port: Optional[int] = Field(None, description="Destination port")
    protocol: Optional[str] = Field(None, description="Network protocol")
    severity: Optional[str] = Field(None, description="Event severity")
    action: Optional[str] = Field(None, description="Action taken")
    user: Optional[str] = Field(None, description="Username")
    message: Optional[str] = Field(None, description="Event message")
    raw_source: str = Field(..., description="Original source type")
    tags: List[str] = Field(default_factory=list, description="Event tags")
    
    # Detection info (from Member 3)
    prediction: Optional[str] = Field(None, description="AI prediction")
    anomaly_score: Optional[float] = Field(None, ge=0, le=1, description="Anomaly score")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Confidence score")
    
    @validator('timestamp', pre=True)
    def parse_timestamp(cls, v):
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                return datetime.utcnow()
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = self.dict()
        if isinstance(data.get('timestamp'), datetime):
            data['timestamp'] = data['timestamp'].isoformat() + 'Z'
        return data