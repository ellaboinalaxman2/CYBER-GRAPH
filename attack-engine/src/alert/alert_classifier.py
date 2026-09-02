"""Alert classifier for Member 5 - Attack Engine."""

from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime

from src.core.logging import get_logger


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertStatus(str, Enum):
    """Alert status values."""
    
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    CONTAINED = "CONTAINED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class AlertClassifier:
    """
    Classifies alerts based on risk and context.
    
    Features:
    - Classify by severity
    - Classify by type
    - Determine priority
    - Auto-assign status
    """
    
    def __init__(self):
        """Initialize the alert classifier."""
        self.logger = get_logger("alert.alert_classifier")
    
    def classify(
        self,
        risk_score: float,
        attack_type: Optional[str] = None,
        mitre_techniques: Optional[List[str]] = None,
        affected_nodes: Optional[List[str]] = None,
        anomaly_score: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Classify an alert.
        
        Args:
            risk_score: Risk score (0-100)
            attack_type: Type of attack
            mitre_techniques: MITRE techniques
            affected_nodes: Affected nodes
            anomaly_score: Anomaly score
            
        Returns:
            Dict[str, Any]: Classification result
        """
        # Determine severity
        severity = self._get_severity(risk_score, anomaly_score)
        
        # Determine alert type
        alert_type = self._get_alert_type(attack_type, mitre_techniques)
        
        # Determine priority
        priority = self._get_priority(severity, risk_score, affected_nodes)
        
        # Determine initial status
        status = AlertStatus.OPEN.value
        
        # Determine urgency
        urgency = self._get_urgency(severity, risk_score)
        
        return {
            "severity": severity,
            "alert_type": alert_type,
            "priority": priority,
            "status": status,
            "urgency": urgency,
            "risk_score": risk_score,
            "anomaly_score": anomaly_score,
            "attack_type": attack_type,
            "mitre_techniques": mitre_techniques or [],
            "affected_nodes": affected_nodes or [],
            "needs_immediate_action": priority >= 3,
            "recommended_response": self._get_response(severity, alert_type),
        }
    
    def _get_severity(self, risk_score: float, anomaly_score: Optional[float]) -> str:
        """Get severity based on risk score."""
        if risk_score >= 85:
            return AlertSeverity.CRITICAL.value
        elif risk_score >= 70:
            return AlertSeverity.HIGH.value
        elif risk_score >= 40:
            return AlertSeverity.MEDIUM.value
        else:
            return AlertSeverity.LOW.value
    
    def _get_alert_type(self, attack_type: Optional[str], mitre_techniques: Optional[List[str]]) -> str:
        """Get alert type based on attack type and MITRE techniques."""
        if attack_type:
            return attack_type.replace("_", " ").title()
        
        if mitre_techniques:
            # Map MITRE techniques to alert types
            tech_map = {
                "T1110": "Brute Force Attack",
                "T1021": "Lateral Movement",
                "T1078": "Account Compromise",
                "T1068": "Privilege Escalation",
                "T1003": "Credential Dumping",
                "T1486": "Ransomware",
                "T1046": "Network Scanning",
                "T1059": "Command Execution",
                "T1562": "Defense Evasion",
                "T1083": "File Discovery",
                "T1133": "External Remote Access",
                "T1190": "Application Exploit",
            }
            
            for tech_id in mitre_techniques:
                if tech_id in tech_map:
                    return tech_map[tech_id]
        
        return "Security Alert"
    
    def _get_priority(self, severity: str, risk_score: float, affected_nodes: Optional[List[str]]) -> int:
        """Get priority level (1-5)."""
        base_priority = {
            AlertSeverity.LOW.value: 1,
            AlertSeverity.MEDIUM.value: 2,
            AlertSeverity.HIGH.value: 3,
            AlertSeverity.CRITICAL.value: 4,
        }
        
        priority = base_priority.get(severity, 2)
        
        # Increase priority for high risk
        if risk_score >= 90:
            priority += 1
        
        # Increase priority for critical nodes
        if affected_nodes:
            critical_nodes = sum(1 for n in affected_nodes if "db" in n.lower() or "database" in n.lower() or "critical" in n.lower())
            if critical_nodes >= 2:
                priority += 1
        
        return min(priority, 5)
    
    def _get_urgency(self, severity: str, risk_score: float) -> str:
        """Get urgency level."""
        if risk_score >= 85 or severity == AlertSeverity.CRITICAL.value:
            return "IMMEDIATE"
        elif risk_score >= 70 or severity == AlertSeverity.HIGH.value:
            return "URGENT"
        elif risk_score >= 40 or severity == AlertSeverity.MEDIUM.value:
            return "NORMAL"
        else:
            return "LOW"
    
    def _get_response(self, severity: str, alert_type: str) -> str:
        """Get recommended response based on severity and type."""
        responses = {
            AlertSeverity.CRITICAL.value: "Immediate investigation and containment required. Notify security team and management.",
            AlertSeverity.HIGH.value: "Urgent investigation required. Contain affected systems and gather evidence.",
            AlertSeverity.MEDIUM.value: "Investigate within 24 hours. Monitor for further activity.",
            AlertSeverity.LOW.value: "Monitor and log for future correlation. Investigate if pattern continues.",
        }
        
        base_response = responses.get(severity, "Investigate as per severity level.")
        
        # Add type-specific recommendations
        if "Brute Force" in alert_type:
            base_response += " Review authentication logs and implement account lockout policies."
        elif "Lateral Movement" in alert_type:
            base_response += " Check for unusual network connections and implement segmentation."
        elif "Ransomware" in alert_type:
            base_response += " Isolate affected systems immediately and check for backups."
        elif "Privilege Escalation" in alert_type:
            base_response += " Review user privileges and audit administrative actions."
        
        return base_response