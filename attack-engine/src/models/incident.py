"""Incident model for Member 5 - Attack Engine."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class IncidentModel(BaseModel):
    """Incident model representing a correlated group of events."""
    
    incident_id: str = Field(..., description="Unique incident identifier")
    title: str = Field(..., description="Incident title")
    description: Optional[str] = Field(None, description="Incident description")
    severity: str = Field(..., description="Incident severity (LOW/MEDIUM/HIGH/CRITICAL)")
    risk_score: float = Field(..., ge=0, le=100, description="Risk score")
    
    # Related events
    event_ids: List[str] = Field(default_factory=list, description="Related event IDs")
    alert_ids: List[str] = Field(default_factory=list, description="Related alert IDs")
    
    # Attack information
    attack_type: Optional[str] = Field(None, description="Type of attack")
    attack_path: Optional[List[Dict[str, Any]]] = Field(None, description="Attack path")
    
    # MITRE
    mitre_techniques: List[str] = Field(default_factory=list, description="MITRE ATT&CK techniques")
    mitre_tactics: List[str] = Field(default_factory=list, description="MITRE ATT&CK tactics")
    
    # Timeline
    started_at: datetime = Field(..., description="Incident start time")
    detected_at: datetime = Field(default_factory=datetime.utcnow, description="Detection time")
    resolved_at: Optional[datetime] = Field(None, description="Resolution time")
    
    # Status
    status: str = Field(default="OPEN", description="Incident status")
    assigned_to: Optional[str] = Field(None, description="Assigned analyst")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    investigation_notes: List[Dict[str, Any]] = Field(default_factory=list, description="Investigation notes")
    
    # Blockchain
    blockchain_hash: Optional[str] = Field(None, description="Blockchain verification hash")
    blockchain_verified: bool = Field(default=False, description="Blockchain verification status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "incident_id": "INC-001",
                "title": "Lateral Movement Attack",
                "description": "Attacker moved from PC-01 to Database",
                "severity": "CRITICAL",
                "risk_score": 94.0,
                "event_ids": ["EVT-001", "EVT-002", "EVT-003"],
                "attack_type": "Lateral Movement",
                "attack_path": [
                    {"from": "PC-01", "to": "SERVER-01"},
                    {"from": "SERVER-01", "to": "DB-01"}
                ],
                "mitre_techniques": ["T1021", "T1078"],
                "started_at": "2026-08-29T10:30:00Z",
                "status": "OPEN",
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = self.dict()
        for field in ['started_at', 'detected_at', 'resolved_at', 'created_at', 'updated_at']:
            if field in data and isinstance(data[field], datetime):
                data[field] = data[field].isoformat() + 'Z'
        return data