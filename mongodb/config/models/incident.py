from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

class IncidentStatus(str, Enum):
    NEW = "NEW"
    UNDER_INVESTIGATION = "UNDER_INVESTIGATION"
    CONFIRMED = "CONFIRMED"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    CONTAINED = "CONTAINED"
    ERADICATED = "ERADICATED"
    RECOVERED = "RECOVERED"
    CLOSED = "CLOSED"

class IncidentModel:
    """Incident model for MongoDB"""
    
    def __init__(self, data: dict):
        self.data = data
    
    @staticmethod
    def schema() -> dict:
        """Incident schema definition"""
        return {
            "incident_id": str,          # Unique incident identifier
            "title": str,               # Incident title
            "description": str,          # Incident description
            "status": IncidentStatus,    # Current status
            "severity": str,            # Overall severity
            "priority": int,            # Priority (1-5)
            "risk_score": float,        # Overall risk score
            "timestamp_start": datetime,  # First event timestamp
            "timestamp_end": Optional[datetime],  # Last event timestamp
            "events": List[str],        # Associated event IDs
            "alerts": List[str],        # Associated alert IDs
            "affected_nodes": List[str],  # Affected nodes
            "attack_path": List[str],   # Attack path
            "root_cause": Optional[str],  # Root cause analysis
            "impact_assessment": Optional[str],  # Business impact
            "containment_actions": List[str],  # Containment actions
            "eradication_actions": List[str],  # Eradication actions
            "recovery_actions": List[str],  # Recovery actions
            "lessons_learned": Optional[str],  # Lessons learned
            "assigned_to": Optional[str],  # Assigned team
            "investigation_log": List[Dict[str, Any]],  # Investigation timeline
            "evidence": List[Dict[str, Any]],  # Evidence collected
            "indicators_of_compromise": List[Dict[str, Any]],  # IOCs
            "mitre_techniques": List[str],  # MITRE techniques
            "remediation_completed": bool,  # Remediation flag
            "time_to_detect": Optional[float],  # TTD in seconds
            "time_to_respond": Optional[float],  # TTR in seconds
            "created_at": datetime,      # Creation timestamp
            "updated_at": datetime,      # Last update timestamp
            "closed_at": Optional[datetime],  # Closure timestamp
            "metadata": Dict[str, Any]   # Additional metadata
        }
    
    @classmethod
    def create(cls, incident_data: dict) -> dict:
        """Create a new incident document"""
        return {
            "incident_id": incident_data.get("incident_id"),
            "title": incident_data.get("title"),
            "description": incident_data.get("description"),
            "status": incident_data.get("status", IncidentStatus.NEW),
            "severity": incident_data.get("severity"),
            "priority": incident_data.get("priority", 3),
            "risk_score": incident_data.get("risk_score", 0.0),
            "timestamp_start": incident_data.get("timestamp_start", datetime.utcnow()),
            "timestamp_end": incident_data.get("timestamp_end"),
            "events": incident_data.get("events", []),
            "alerts": incident_data.get("alerts", []),
            "affected_nodes": incident_data.get("affected_nodes", []),
            "attack_path": incident_data.get("attack_path", []),
            "root_cause": incident_data.get("root_cause"),
            "impact_assessment": incident_data.get("impact_assessment"),
            "containment_actions": incident_data.get("containment_actions", []),
            "eradication_actions": incident_data.get("eradication_actions", []),
            "recovery_actions": incident_data.get("recovery_actions", []),
            "lessons_learned": incident_data.get("lessons_learned"),
            "assigned_to": incident_data.get("assigned_to"),
            "investigation_log": incident_data.get("investigation_log", []),
            "evidence": incident_data.get("evidence", []),
            "indicators_of_compromise": incident_data.get("indicators_of_compromise", []),
            "mitre_techniques": incident_data.get("mitre_techniques", []),
            "remediation_completed": incident_data.get("remediation_completed", False),
            "time_to_detect": incident_data.get("time_to_detect"),
            "time_to_respond": incident_data.get("time_to_respond"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "closed_at": incident_data.get("closed_at"),
            "metadata": incident_data.get("metadata", {})
        }