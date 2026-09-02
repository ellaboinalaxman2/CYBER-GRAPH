# app/models/alert.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class Alert(BaseModel):
    alert_id: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    risk_score: float
    attack_type: str
    confidence: float
    description: Optional[str] = None
    affected_nodes: List[str] = []
    attack_path: Optional[List[str]] = None
    mitre_techniques: Optional[List[dict]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    blockchain_hash: Optional[str] = None
    blockchain_verified: bool = False