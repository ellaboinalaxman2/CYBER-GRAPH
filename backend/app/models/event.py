# app/models/event.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Event(BaseModel):
    event_id: str
    source: str
    destination: str
    protocol: str
    timestamp: datetime
    src_port: Optional[int] = None
    dst_port: Optional[int] = None
    payload: Optional[dict] = None
    label: Optional[str] = None  # from CICIDS2017
    ingested_at: datetime = Field(default_factory=datetime.utcnow)