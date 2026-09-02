"""Attack path model for Member 5 - Attack Engine."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class AttackPathModel(BaseModel):
    """Attack path model."""
    
    path_id: str = Field(..., description="Unique path identifier")
    nodes: List[str] = Field(..., description="Nodes in the path (ordered)")
    edges: List[Dict[str, str]] = Field(default_factory=list, description="Edges between nodes")
    source: str = Field(..., description="Source node")
    target: str = Field(..., description="Target node")
    events: List[str] = Field(default_factory=list, description="Related event IDs")
    length: int = Field(..., description="Number of edges in path")
    
    # Path metadata
    confidence: float = Field(default=0.5, ge=0, le=1, description="Confidence score")
    score: float = Field(default=0.0, ge=0, le=100, description="Path score")
    description: Optional[str] = Field(None, description="Path description")
    
    # Detection info
    detection_type: Optional[str] = Field(None, description="How path was detected")
    mitre_techniques: List[str] = Field(default_factory=list, description="MITRE techniques")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "path_id": "PATH-001",
                "nodes": ["PC-01", "SERVER-01", "SERVER-02", "DB-01"],
                "edges": [
                    {"from": "PC-01", "to": "SERVER-01", "type": "CONNECTS_TO"},
                    {"from": "SERVER-01", "to": "SERVER-02", "type": "CONNECTS_TO"},
                    {"from": "SERVER-02", "to": "DB-01", "type": "ACCESSES"}
                ],
                "source": "PC-01",
                "target": "DB-01",
                "events": ["EVT-001", "EVT-002", "EVT-003"],
                "length": 3,
                "confidence": 0.85,
                "score": 78.5,
                "description": "Lateral movement from PC-01 to Database",
                "mitre_techniques": ["T1021", "T1078"],
                "created_at": "2026-08-29T10:30:00Z"
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = self.dict()
        for field in ['created_at', 'updated_at']:
            if field in data and isinstance(data[field], datetime):
                data[field] = data[field].isoformat() + 'Z'
        return data