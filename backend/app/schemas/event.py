# app/schemas/event.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class EventCreate(BaseModel):
    source: str
    destination: str
    protocol: str
    timestamp: Optional[datetime] = None
    src_port: Optional[int] = None
    dst_port: Optional[int] = None
    payload: Optional[Dict[str, Any]] = None
    label: Optional[str] = None

class EventResponse(BaseModel):
    id: str
    source: str
    destination: str
    protocol: str
    timestamp: Optional[str]
    src_port: Optional[int]
    dst_port: Optional[int]
    label: Optional[str]
    created_at: Optional[str]