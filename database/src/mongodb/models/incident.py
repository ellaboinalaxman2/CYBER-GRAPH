"""Incident model for MongoDB."""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class IncidentModel(BaseModel):
    """MongoDB incident document model."""
    
    incident_id: str = Field(..., description="Unique incident identifier")
    alert_ids: List[str] = Field(default_factory=list, description="Related alert IDs")
    event_ids: List[str] = Field(default_factory=list, description="Related event IDs")
    node_ids: List[str] = Field(default_factory=list, description="Related Neo4j node IDs")
    
    # Incident details
    title: str = Field(..., description="Incident title")
    description: Optional[str] = Field(None, description="Incident description")
    severity: str = Field(..., description="Incident severity (LOW/MEDIUM/HIGH/CRITICAL)")
    risk_score: float = Field(..., ge=0, le=100, description="Risk score")
    
    # Status
    status: str = Field(default="OPEN", description="Incident status (OPEN/INVESTIGATING/CONTAINED/ERADICATED/RECOVERED/CLOSED)")
    assigned_to: Optional[str] = Field(None, description="Assigned analyst")
    assigned_team: Optional[str] = Field(None, description="Assigned team")
    
    # Timeline
    started_at: datetime = Field(..., description="Incident start time")
    detected_at: datetime = Field(default_factory=datetime.utcnow, description="Detection time")
    contained_at: Optional[datetime] = Field(None, description="Containment time")
    eradicated_at: Optional[datetime] = Field(None, description="Eradication time")
    recovered_at: Optional[datetime] = Field(None, description="Recovery time")
    resolved_at: Optional[datetime] = Field(None, description="Resolution time")
    
    # MITRE ATT&CK
    mitre_techniques: List[str] = Field(default_factory=list, description="MITRE ATT&CK techniques")
    mitre_tactics: List[str] = Field(default_factory=list, description="MITRE ATT&CK tactics")
    
    # Investigation
    investigation_notes: List[Dict[str, Any]] = Field(default_factory=list, description="Investigation notes")
    root_cause: Optional[str] = Field(None, description="Root cause analysis")
    lessons_learned: Optional[str] = Field(None, description="Lessons learned")
    
    # Impact
    affected_systems: List[str] = Field(default_factory=list, description="Affected systems")
    data_breach: bool = Field(default=False, description="Data breach indicator")
    financial_impact: Optional[float] = Field(None, description="Estimated financial impact")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    closed_by: Optional[str] = Field(None, description="Who closed the incident")
    
    class Config:
        json_schema_extra = {
            "example": {
                "incident_id": "INC-001",
                "alert_ids": ["ALT-001", "ALT-002"],
                "event_ids": ["EVT-001", "EVT-002", "EVT-003"],
                "title": "Lateral Movement Attack",
                "description": "Attacker moved from PC-01 to Database",
                "severity": "CRITICAL",
                "risk_score": 94.0,
                "status": "INVESTIGATING",
                "started_at": "2026-08-29T10:30:00Z",
                "mitre_techniques": ["T1021", "T1078"],
                "affected_systems": ["PC-01", "SERVER-01", "DB-01"],
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB."""
        data = self.dict()
        # Convert datetime objects to ISO format strings
        for field in ['started_at', 'detected_at', 'contained_at', 'eradicated_at', 
                     'recovered_at', 'resolved_at', 'created_at', 'updated_at']:
            if field in data and isinstance(data[field], datetime):
                data[field] = data[field].isoformat() + 'Z'
        return data