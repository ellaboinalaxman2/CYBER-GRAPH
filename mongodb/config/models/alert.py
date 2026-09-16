from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

class AlertSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class AlertStatus(str, Enum):
    OPEN = "OPEN"
    UNDER_INVESTIGATION = "UNDER_INVESTIGATION"
    CONFIRMED = "CONFIRMED"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class AlertModel:
    """Alert model for MongoDB"""
    
    def __init__(self, data: dict):
        self.data = data
    
    @staticmethod
    def schema() -> dict:
        """Alert schema definition"""
        return {
            "alert_id": str,            # Unique alert identifier
            "incident_id": Optional[str],  # Associated incident
            "timestamp": datetime,      # Alert timestamp
            "severity": AlertSeverity,  # Alert severity
            "status": AlertStatus,      # Alert status
            "risk_score": float,        # Risk score (0-100)
            "confidence": float,        # Confidence score (0-1)
            "attack_type": str,         # Type of attack
            "attack_technique": str,    # MITRE ATT&CK technique
            "attack_technique_id": str, # MITRE ATT&CK technique ID
            "source": str,             # Source of attack
            "target": str,             # Target of attack
            "description": str,         # Alert description
            "events": List[str],        # Related event IDs
            "affected_nodes": List[str],  # Affected nodes
            "attack_path": List[str],   # Attack path
            "reconstruction_details": Dict[str, Any],  # Path reconstruction
            "mitre_mapping": Dict[str, Any],  # MITRE ATT&CK mapping
            "behavioral_evidence": List[str],  # Evidence list
            "recommendations": List[str],  # Remediation recommendations
            "assigned_to": Optional[str],  # Assigned analyst
            "investigation_notes": List[Dict[str, Any]],  # Investigation notes
            "blockchain_hash": Optional[str],  # Blockchain hash
            "blockchain_tx_id": Optional[str],  # Blockchain transaction
            "metadata": Dict[str, Any],  # Additional metadata
            "created_at": datetime,     # Creation timestamp
            "updated_at": datetime,     # Last update timestamp
            "resolved_at": Optional[datetime],  # Resolution timestamp
            "false_positive_reason": Optional[str],  # FP reason
            "escalated": bool          # Escalation flag
        }
    
    @classmethod
    def create(cls, alert_data: dict) -> dict:
        """Create a new alert document"""
        return {
            "alert_id": alert_data.get("alert_id"),
            "incident_id": alert_data.get("incident_id"),
            "timestamp": alert_data.get("timestamp", datetime.utcnow()),
            "severity": alert_data.get("severity", AlertSeverity.MEDIUM),
            "status": alert_data.get("status", AlertStatus.OPEN),
            "risk_score": alert_data.get("risk_score", 0.0),
            "confidence": alert_data.get("confidence", 0.0),
            "attack_type": alert_data.get("attack_type"),
            "attack_technique": alert_data.get("attack_technique"),
            "attack_technique_id": alert_data.get("attack_technique_id"),
            "source": alert_data.get("source"),
            "target": alert_data.get("target"),
            "description": alert_data.get("description"),
            "events": alert_data.get("events", []),
            "affected_nodes": alert_data.get("affected_nodes", []),
            "attack_path": alert_data.get("attack_path", []),
            "reconstruction_details": alert_data.get("reconstruction_details", {}),
            "mitre_mapping": alert_data.get("mitre_mapping", {}),
            "behavioral_evidence": alert_data.get("behavioral_evidence", []),
            "recommendations": alert_data.get("recommendations", []),
            "assigned_to": alert_data.get("assigned_to"),
            "investigation_notes": alert_data.get("investigation_notes", []),
            "blockchain_hash": alert_data.get("blockchain_hash"),
            "blockchain_tx_id": alert_data.get("blockchain_tx_id"),
            "metadata": alert_data.get("metadata", {}),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "resolved_at": alert_data.get("resolved_at"),
            "false_positive_reason": alert_data.get("false_positive_reason"),
            "escalated": alert_data.get("escalated", False)
        }
    
    @classmethod
    def calculate_risk_level(cls, risk_score: float) -> str:
        """Calculate risk level from score"""
        if risk_score >= 81:
            return "CRITICAL"
        elif risk_score >= 61:
            return "HIGH"
        elif risk_score >= 31:
            return "MEDIUM"
        else:
            return "LOW"