"""Alert model for MongoDB."""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class AlertModel(BaseModel):
    """MongoDB alert document model."""
    
    alert_id: str = Field(..., description="Unique alert identifier")
    incident_id: Optional[str] = Field(None, description="Associated incident ID")
    event_ids: List[str] = Field(default_factory=list, description="Related event IDs")
    
    # Alert details
    severity: str = Field(..., description="Alert severity (LOW/MEDIUM/HIGH/CRITICAL)")
    risk_score: float = Field(..., ge=0, le=100, description="Risk score")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    attack_type: Optional[str] = Field(None, description="Type of attack")
    mitre_techniques: List[str] = Field(default_factory=list, description="MITRE ATT&CK techniques")
    
    # Status
    status: str = Field(default="OPEN", description="Alert status (OPEN/INVESTIGATING/RESOLVED/CLOSED)")
    assigned_to: Optional[str] = Field(None, description="Assigned analyst")
    
    # Attack path
    attack_path: List[Dict[str, Any]] = Field(default_factory=list, description="Reconstructed attack path")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    resolved_at: Optional[datetime] = Field(None, description="Resolution timestamp")
    resolved_by: Optional[str] = Field(None, description="Who resolved the alert")
    
    # Blockchain verification
    blockchain_hash: Optional[str] = Field(None, description="Blockchain verification hash")
    blockchain_verified: bool = Field(default=False, description="Blockchain verification status")
    blockchain_tx_id: Optional[str] = Field(None, description="Blockchain transaction ID")
    
    # Additional metadata
    tags: List[str] = Field(default_factory=list, description="Alert tags")
    notes: List[Dict[str, Any]] = Field(default_factory=list, description="Investigation notes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "alert_id": "ALT-001",
                "incident_id": "INC-001",
                "event_ids": ["EVT-001", "EVT-002", "EVT-003"],
                "severity": "CRITICAL",
                "risk_score": 94.0,
                "confidence": 0.93,
                "attack_type": "Lateral Movement",
                "mitre_techniques": ["T1021", "T1078"],
                "status": "OPEN",
                "attack_path": [
                    {"from": "PC-01", "to": "SERVER-01"},
                    {"from": "SERVER-01", "to": "DB-01"}
                ],
                "blockchain_hash": "0x1234...",
                "blockchain_verified": True,
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB."""
        data = self.dict()
        # Convert datetime objects to ISO format strings
        for field in ['created_at', 'updated_at', 'resolved_at']:
            if field in data and isinstance(data[field], datetime):
                data[field] = data[field].isoformat() + 'Z'
        return data