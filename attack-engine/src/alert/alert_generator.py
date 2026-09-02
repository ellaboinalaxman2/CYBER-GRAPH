"""Alert generator for Member 5 - Attack Engine."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from src.core.logging import get_logger
from src.core.exceptions import AlertError
from src.alert.alert_classifier import AlertClassifier, AlertStatus
from src.alert.alert_formatter import AlertFormatter


class AlertGenerator:
    """
    Generates security alerts from incidents.
    
    Features:
    - Generate alerts from incidents
    - Create alert ID
    - Set alert fields
    - Update alert status
    - Add notes
    """
    
    def __init__(self):
        """Initialize the alert generator."""
        self.logger = get_logger("alert.alert_generator")
        self.classifier = AlertClassifier()
        self.formatter = AlertFormatter()
        self._alerts = {}
    
    def generate(
        self,
        incident: Dict[str, Any],
        events: List[Dict[str, Any]],
        risk_assessment: Dict[str, Any],
        mitre_mapping: Dict[str, Any],
        attack_path: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Generate an alert from an incident.
        
        Args:
            incident: Incident data
            events: List of events
            risk_assessment: Risk assessment results
            mitre_mapping: MITRE mapping results
            attack_path: Attack path
            
        Returns:
            Dict[str, Any]: Generated alert
        """
        self.logger.info(f"Generating alert for incident {incident.get('incident_id', 'unknown')}")
        
        # Get classification
        classification = self.classifier.classify(
            risk_score=risk_assessment.get("risk_score", 50),
            attack_type=incident.get("attack_type"),
            mitre_techniques=mitre_mapping.get("technique_ids", []),
            affected_nodes=risk_assessment.get("affected_nodes", []),
            anomaly_score=incident.get("anomaly_score"),
        )
        
        # Generate alert ID
        alert_id = f"ALT-{uuid.uuid4().hex[:8].upper()}"
        
        # Build alert
        alert = {
            "alert_id": alert_id,
            "incident_id": incident.get("incident_id"),
            "title": self._generate_title(incident, classification),
            "description": self._generate_description(incident, events, risk_assessment),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z",
            "severity": classification["severity"],
            "priority": classification["priority"],
            "urgency": classification["urgency"],
            "risk_score": risk_assessment.get("risk_score", 50),
            "confidence": incident.get("confidence", 0.8),
            "attack_type": classification["alert_type"],
            "attack_path": attack_path or incident.get("attack_path", []),
            "mitre_techniques": mitre_mapping.get("technique_ids", []),
            "mitre_tactics": mitre_mapping.get("tactic_ids", []),
            "affected_nodes": risk_assessment.get("affected_nodes", []),
            "event_ids": [e.get("event_id") for e in events if e.get("event_id")],
            "status": classification["status"],
            "recommendations": self._generate_recommendations(incident, classification, risk_assessment),
            "investigation_notes": [],
            "blockchain_hash": None,
            "blockchain_verified": False,
            "needs_immediate_action": classification["needs_immediate_action"],
            "recommended_response": classification["recommended_response"],
        }
        
        # Store alert
        self._alerts[alert_id] = alert
        
        self.logger.info(f"Generated alert {alert_id} with severity {alert['severity']}")
        return alert
    
    def _generate_title(self, incident: Dict[str, Any], classification: Dict[str, Any]) -> str:
        """Generate alert title."""
        attack_type = classification["alert_type"]
        
        if attack_type != "Security Alert":
            return f"{attack_type} Detected"
        
        if incident.get("attack_type"):
            return f"{incident['attack_type'].replace('_', ' ').title()} Attack Detected"
        
        return "Security Alert Generated"
    
    def _generate_description(self, incident: Dict[str, Any], events: List[Dict[str, Any]], risk: Dict[str, Any]) -> str:
        """Generate alert description."""
        parts = []
        
        # Attack type
        if incident.get("attack_type"):
            parts.append(f"Attack type: {incident['attack_type'].replace('_', ' ').title()}")
        
        # Events
        if events:
            parts.append(f"Based on {len(events)} correlated events")
        
        # Affected nodes
        nodes = risk.get("affected_nodes", [])
        if nodes:
            parts.append(f"Affected systems: {', '.join(nodes[:5])}")
        
        # Risk
        risk_score = risk.get("risk_score", 0)
        if risk_score >= 85:
            parts.append("CRITICAL risk level detected")
        elif risk_score >= 70:
            parts.append("High risk level detected")
        
        return ". ".join(parts)
    
    def _generate_recommendations(self, incident: Dict[str, Any], classification: Dict[str, Any], risk: Dict[str, Any]) -> List[str]:
        """Generate recommendations."""
        recommendations = []
        
        # Based on severity
        severity = classification["severity"]
        if severity == "CRITICAL":
            recommendations.append("Immediate investigation and containment required")
            recommendations.append("Notify security team and management")
            recommendations.append("Preserve evidence for forensic analysis")
        elif severity == "HIGH":
            recommendations.append("Urgent investigation required")
            recommendations.append("Contain affected systems")
            recommendations.append("Gather evidence")
        elif severity == "MEDIUM":
            recommendations.append("Investigate within 24 hours")
            recommendations.append("Monitor for further activity")
        else:
            recommendations.append("Monitor and log for future correlation")
        
        # Based on attack type
        attack_type = incident.get("attack_type", "")
        if "lateral_movement" in attack_type:
            recommendations.append("Review network connections and implement segmentation")
        elif "brute_force" in attack_type:
            recommendations.append("Review authentication logs and implement account lockout")
        elif "data_exfiltration" in attack_type:
            recommendations.append("Review data access logs and implement DLP controls")
        elif "privilege_escalation" in attack_type:
            recommendations.append("Review user privileges and audit administrative actions")
        
        return recommendations
    
    def update_status(self, alert_id: str, status: str, note: Optional[str] = None, user: Optional[str] = None) -> Dict[str, Any]:
        """
        Update alert status.
        
        Args:
            alert_id: Alert ID
            status: New status
            note: Optional note
            user: User making the change
            
        Returns:
            Dict[str, Any]: Updated alert
        """
        if alert_id not in self._alerts:
            raise AlertError(f"Alert {alert_id} not found")
        
        alert = self._alerts[alert_id]
        alert["status"] = status
        alert["updated_at"] = datetime.utcnow().isoformat() + "Z"
        
        if note:
            alert["investigation_notes"].append({
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "user": user or "system",
                "note": note,
                "action": f"Status changed to {status}",
            })
        
        self.logger.info(f"Updated alert {alert_id} status to {status}")
        return alert
    
    def add_note(self, alert_id: str, note: str, user: Optional[str] = None) -> Dict[str, Any]:
        """
        Add an investigation note to an alert.
        
        Args:
            alert_id: Alert ID
            note: Note content
            user: User adding the note
            
        Returns:
            Dict[str, Any]: Updated alert
        """
        if alert_id not in self._alerts:
            raise AlertError(f"Alert {alert_id} not found")
        
        alert = self._alerts[alert_id]
        alert["investigation_notes"].append({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "user": user or "system",
            "note": note,
            "action": "Note added",
        })
        alert["updated_at"] = datetime.utcnow().isoformat() + "Z"
        
        self.logger.info(f"Added note to alert {alert_id}")
        return alert
    
    def get_alert(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an alert by ID.
        
        Args:
            alert_id: Alert ID
            
        Returns:
            Optional[Dict[str, Any]]: Alert data
        """
        return self._alerts.get(alert_id)
    
    def get_all_alerts(self) -> List[Dict[str, Any]]:
        """
        Get all alerts.
        
        Returns:
            List[Dict[str, Any]]: All alerts
        """
        return list(self._alerts.values())
    
    def get_alerts_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Get alerts by status.
        
        Args:
            status: Alert status
            
        Returns:
            List[Dict[str, Any]]: Alerts with status
        """
        return [a for a in self._alerts.values() if a.get("status") == status]
    
    def get_alerts_by_severity(self, severity: str) -> List[Dict[str, Any]]:
        """
        Get alerts by severity.
        
        Args:
            severity: Alert severity
            
        Returns:
            List[Dict[str, Any]]: Alerts with severity
        """
        return [a for a in self._alerts.values() if a.get("severity") == severity]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get alert statistics.
        
        Returns:
            Dict[str, Any]: Statistics
        """
        alerts = list(self._alerts.values())
        
        if not alerts:
            return {
                "total": 0,
                "by_severity": {},
                "by_status": {},
                "by_attack_type": {},
            }
        
        severity_counts = {}
        status_counts = {}
        attack_type_counts = {}
        
        for alert in alerts:
            severity = alert.get("severity", "UNKNOWN")
            status = alert.get("status", "UNKNOWN")
            attack_type = alert.get("attack_type", "UNKNOWN")
            
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            status_counts[status] = status_counts.get(status, 0) + 1
            attack_type_counts[attack_type] = attack_type_counts.get(attack_type, 0) + 1
        
        return {
            "total": len(alerts),
            "by_severity": severity_counts,
            "by_status": status_counts,
            "by_attack_type": attack_type_counts,
            "open_alerts": sum(1 for a in alerts if a.get("status") in ["OPEN", "INVESTIGATING"]),
            "critical_alerts": severity_counts.get("CRITICAL", 0),
            "high_alerts": severity_counts.get("HIGH", 0),
        }