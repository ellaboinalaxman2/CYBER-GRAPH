from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from ..models.alert import AlertSeverity, AlertStatus

class AlertSchema(BaseModel):
    """Alert schema for validation"""
    
    alert_id: str = Field(..., description="Unique alert identifier")
    incident_id: Optional[str] = Field(None, description="Associated incident")
    timestamp: datetime = Field(..., description="Alert timestamp")
    severity: AlertSeverity = Field(..., description="Alert severity")
    status: AlertStatus = Field(default=AlertStatus.OPEN, description="Alert status")
    risk_score: float = Field(..., ge=0, le=100, description="Risk score")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    attack_type: str = Field(..., description="Type of attack")
    attack_technique: Optional[str] = Field(None, description="MITRE ATT&CK technique")
    attack_technique_id: Optional[str] = Field(None, description="MITRE ATT&CK technique ID")
    source: str = Field(..., description="Source of attack")
    target: str = Field(..., description="Target of attack")
    description: str = Field(..., description="Alert description")
    events: List[str] = Field(default=[], description="Related event IDs")
    affected_nodes: List[str] = Field(default=[], description="Affected nodes")
    attack_path: List[str] = Field(default=[], description="Attack path")
    reconstruction_details: Dict[str, Any] = Field(default={}, description="Path reconstruction")
    mitre_mapping: Dict[str, Any] = Field(default={}, description="MITRE ATT&CK mapping")
    behavioral_evidence: List[str] = Field(default=[], description="Evidence list")
    recommendations: List[str] = Field(default=[], description="Recommendations")
    assigned_to: Optional[str] = Field(None, description="Assigned analyst")
    investigation_notes: List[Dict[str, Any]] = Field(default=[], description="Investigation notes")
    blockchain_hash: Optional[str] = Field(None, description="Blockchain hash")
    blockchain_tx_id: Optional[str] = Field(None, description="Blockchain transaction")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")
    escalated: bool = Field(default=False, description="Escalation flag")
    
    class Config:
        use_enum_values = True
        
    @validator('alert_id')
    def validate_alert_id(cls, v):
        if not v.startswith('ALT-'):
            raise ValueError('Alert ID must start with ALT-')
        return v
    
    @validator('risk_score')
    def validate_risk_score(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('Risk score must be between 0 and 100')
        return v

class AlertCreateSchema(BaseModel):
    """Schema for creating a new alert"""
    attack_type: str
    source: str
    target: str
    description: str
    severity: AlertSeverity
    risk_score: float = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0, le=1)
    events: List[str] = []
    attack_technique: Optional[str] = None
    attack_technique_id: Optional[str] = None
    affected_nodes: List[str] = []
    attack_path: List[str] = []
    recommendations: List[str] = []

class AlertUpdateSchema(BaseModel):
    """Schema for updating an alert"""
    status: Optional[AlertStatus] = None
    assigned_to: Optional[str] = None
    investigation_notes: Optional[List[Dict[str, Any]]] = None
    escalated: Optional[bool] = None
    false_positive_reason: Optional[str] = None
    resolved_at: Optional[datetime] = None