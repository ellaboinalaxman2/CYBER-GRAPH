"""Model version for Member 3 - AI Engine."""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ModelVersion:
    """Model version information."""
    
    version: str
    name: str
    path: str
    created_at: datetime
    metrics: Dict[str, float]
    config: Dict[str, Any]
    status: str = "active"
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "name": self.name,
            "path": self.path,
            "created_at": self.created_at.isoformat() + "Z",
            "metrics": self.metrics,
            "config": self.config,
            "status": self.status,
            "description": self.description,
        }