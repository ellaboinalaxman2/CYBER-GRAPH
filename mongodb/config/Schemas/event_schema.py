from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from ..models.event import EventType, Protocol

class EventSchema(BaseModel):
    """Event schema for validation"""
    
    event_id: str = Field(..., description="Unique event identifier")
    timestamp: datetime = Field(..., description="Event timestamp")
    source: str = Field(..., description="Source IP/hostname")
    source_port: Optional[int] = Field(None, ge=0, le=65535, description="Source port")
    destination: str = Field(..., description="Destination IP/hostname")
    destination_port: Optional[int] = Field(None, ge=0, le=65535, description="Destination port")
    protocol: Optional[Protocol] = Field(None, description="Network protocol")
    event_type: EventType = Field(..., description="Type of event")
    user: Optional[str] = Field(None, description="Associated user")
    process: Optional[str] = Field(None, description="Associated process")
    command_line: Optional[str] = Field(None, description="Full command line")
    message: str = Field(..., description="Event message")
    severity: Optional[str] = Field(None, description="Event severity")
    raw_log: str = Field(..., description="Original raw log")
    normalized_data: Dict[str, Any] = Field(default={}, description="Normalized fields")
    tags: List[str] = Field(default=[], description="Event tags")
    is_anomaly: bool = Field(default=False, description="Anomaly flag")
    anomaly_score: Optional[float] = Field(None, ge=0, le=1, description="Anomaly score")
    source_hostname: Optional[str] = Field(None, description="Source hostname")
    destination_hostname: Optional[str] = Field(None, description="Destination hostname")
    bytes_sent: Optional[int] = Field(None, ge=0, description="Bytes sent")
    bytes_received: Optional[int] = Field(None, ge=0, description="Bytes received")
    duration: Optional[float] = Field(None, ge=0, description="Connection duration")
    country: Optional[str] = Field(None, description="Country for IP")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")
    source_type: str = Field(default="NETWORK", description="Log source type")
    
    class Config:
        use_enum_values = True
        
    @validator('event_id')
    def validate_event_id(cls, v):
        if not v.startswith('EVT-'):
            raise ValueError('Event ID must start with EVT-')
        return v

class EventCreateSchema(BaseModel):
    """Schema for creating a new event"""
    source: str
    destination: str
    protocol: Optional[Protocol] = None
    event_type: EventType
    message: str
    raw_log: str
    timestamp: Optional[datetime] = None
    source_port: Optional[int] = Field(None, ge=0, le=65535)
    destination_port: Optional[int] = Field(None, ge=0, le=65535)
    user: Optional[str] = None
    process: Optional[str] = None
    command_line: Optional[str] = None
    severity: Optional[str] = None
    normalized_data: Dict[str, Any] = {}
    tags: List[str] = []