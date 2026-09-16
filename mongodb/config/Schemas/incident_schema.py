from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from ..models.incident import IncidentStatus

class IncidentSchema(BaseModel):
    """Incident schema for validation"""
    
    incident_id: str = Field(..., description="Unique incident identifier")
    title: str = Field(..., min_length=3, max_length=200, description="Incident title")
    description: str = Field(..., description="Incident description")
    status: IncidentStatus = Field(default=IncidentStatus.NEW, description="Current status")
    severity: str = Field(..., description="Overall severity")
    priority: int = Field(default=3, ge=1, le=5, description="Priority (1-5)")
    risk_score: float = Field(default=0.0, ge=0, le=100, description="Overall risk score")
    timestamp_start: datetime = Field(..., description="First event timestamp")
    timestamp_end: Optional[datetime] = Field(None, description="Last event timestamp")
    events: List[str] = Field(default=[], description="Associated event IDs")
    alerts: List[str] = Field(default=[], description="Associated alert IDs")
    affected_nodes: List[str] = Field(default=[], description="Affected nodes")
    attack_path: List[str] = Field(default=[], description="Attack path")
    root_cause: Optional[str] = Field(None, description="Root cause analysis")
    impact_assessment: Optional[str] = Field(None, description="Business impact")
    containment_actions: List[str] = Field(default=[], description="Containment actions")
    eradication_actions: List[str] = Field(default=[], description="Eradication actions")
    recovery_actions: List[str] = Field(default=[], description="Recovery actions")
    lessons_learned: Optional[str] = Field(None, description="Lessons learned")
    assigned_to: Optional[str] = Field(None, description="Assigned team")
    investigation_log: List[Dict[str, Any]] = Field(default=[], description="Investigation timeline")
    evidence: List[Dict[str, Any]] = Field(default=[], description="Evidence collected")
    indicators_of_compromise: List[Dict[str, Any]] = Field(default=[], description="IOCs")
    mitre_techniques: List[str] = Field(default=[], description="MITRE techniques")
    remediation_completed: bool = Field(default=False, description="Remediation flag")
    time_to_detect: Optional[float] = Field(None, description="TTD in seconds")
    time_to_respond: Optional[float] = Field(None, description="TTR in seconds")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")
    
    class Config:
        use_enum_values = True
        
    @validator('incident_id')
    def validate_incident_id(cls, v):
        if not v.startswith('INC-'):
            raise ValueError('Incident ID must start with INC-')
        return v

class IncidentCreateSchema(BaseModel):
    """Schema for creating a new incident"""
    title: str = Field(..., min_length=3, max_length=200)
    description: str
    severity: str
    events: List[str]
    alerts: List[str]
    affected_nodes: List[str]
    attack_path: List[str]
    priority: int = Field(default=3, ge=1, le=5)