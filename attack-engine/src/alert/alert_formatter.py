"""Alert formatter for Member 5 - Attack Engine."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from src.core.logging import get_logger


class AlertFormatter:
    """
    Formats alerts for different outputs.
    
    Features:
    - JSON format
    - Human-readable format
    - Slack/Teams format
    - Email format
    - Dashboard format
    """
    
    def __init__(self):
        """Initialize the alert formatter."""
        self.logger = get_logger("alert.alert_formatter")
    
    def format_json(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format alert as JSON.
        
        Args:
            alert: Alert data
            
        Returns:
            Dict[str, Any]: Formatted alert
        """
        return {
            "alert_id": alert.get("alert_id"),
            "timestamp": alert.get("timestamp", datetime.utcnow().isoformat() + "Z"),
            "severity": alert.get("severity"),
            "title": alert.get("title"),
            "description": alert.get("description"),
            "risk_score": alert.get("risk_score"),
            "confidence": alert.get("confidence"),
            "attack_type": alert.get("attack_type"),
            "attack_path": alert.get("attack_path", []),
            "mitre_techniques": alert.get("mitre_techniques", []),
            "mitre_tactics": alert.get("mitre_tactics", []),
            "affected_nodes": alert.get("affected_nodes", []),
            "event_ids": alert.get("event_ids", []),
            "status": alert.get("status", "OPEN"),
            "priority": alert.get("priority", 2),
            "urgency": alert.get("urgency", "NORMAL"),
            "recommendations": alert.get("recommendations", []),
            "investigation_notes": alert.get("investigation_notes", []),
            "blockchain_hash": alert.get("blockchain_hash"),
            "blockchain_verified": alert.get("blockchain_verified", False),
            "created_at": alert.get("created_at", datetime.utcnow().isoformat() + "Z"),
            "updated_at": alert.get("updated_at", datetime.utcnow().isoformat() + "Z"),
        }
    
    def format_human_readable(self, alert: Dict[str, Any]) -> str:
        """
        Format alert as human-readable text.
        
        Args:
            alert: Alert data
            
        Returns:
            str: Human-readable alert
        """
        lines = []
        
        # Header
        lines.append("=" * 60)
        lines.append(f"🔔 SECURITY ALERT: {alert.get('title', 'Unknown Alert')}")
        lines.append("=" * 60)
        
        # Basic info
        lines.append(f"🆔 Alert ID: {alert.get('alert_id', 'N/A')}")
        lines.append(f"📅 Timestamp: {alert.get('timestamp', 'N/A')}")
        lines.append(f"📊 Severity: {alert.get('severity', 'UNKNOWN')}")
        lines.append(f"🎯 Priority: {alert.get('priority', 0)}/5")
        lines.append(f"⚡ Urgency: {alert.get('urgency', 'NORMAL')}")
        
        # Risk
        lines.append(f"📈 Risk Score: {alert.get('risk_score', 0):.1f}/100")
        lines.append(f"🔬 Confidence: {alert.get('confidence', 0):.1%}")
        
        # Attack details
        lines.append(f"🎭 Attack Type: {alert.get('attack_type', 'Unknown')}")
        
        # MITRE
        techniques = alert.get('mitre_techniques', [])
        if techniques:
            lines.append(f"📋 MITRE Techniques: {', '.join(techniques)}")
        
        # Attack path
        attack_path = alert.get('attack_path', [])
        if attack_path:
            lines.append("🗺️ Attack Path:")
            for i, step in enumerate(attack_path):
                if isinstance(step, dict):
                    from_node = step.get("from", "?")
                    to_node = step.get("to", "?")
                    lines.append(f"  {i+1}. {from_node} → {to_node}")
                else:
                    lines.append(f"  {i+1}. {step}")
        
        # Affected nodes
        nodes = alert.get('affected_nodes', [])
        if nodes:
            lines.append(f"💻 Affected Nodes: {', '.join(nodes)}")
        
        # Recommendations
        recommendations = alert.get('recommendations', [])
        if recommendations:
            lines.append("\n📋 RECOMMENDATIONS:")
            for rec in recommendations:
                lines.append(f"  • {rec}")
        
        # Footer
        lines.append("-" * 60)
        lines.append(f"Status: {alert.get('status', 'OPEN')}")
        lines.append(f"Blockchain Verified: {'✅' if alert.get('blockchain_verified', False) else '❌'}")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def format_slack(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format alert for Slack/Teams.
        
        Args:
            alert: Alert data
            
        Returns:
            Dict[str, Any]: Slack message format
        """
        severity = alert.get('severity', 'UNKNOWN')
        colors = {
            "LOW": "#2ecc71",
            "MEDIUM": "#f39c12",
            "HIGH": "#e67e22",
            "CRITICAL": "#e74c3c",
        }
        
        return {
            "text": f"🚨 *Security Alert: {alert.get('title', 'Unknown')}*",
            "attachments": [
                {
                    "color": colors.get(severity, "#95a5a6"),
                    "title": f"{severity} Severity Alert",
                    "fields": [
                        {
                            "title": "Alert ID",
                            "value": alert.get('alert_id', 'N/A'),
                            "short": True,
                        },
                        {
                            "title": "Risk Score",
                            "value": f"{alert.get('risk_score', 0):.1f}/100",
                            "short": True,
                        },
                        {
                            "title": "Attack Type",
                            "value": alert.get('attack_type', 'Unknown'),
                            "short": True,
                        },
                        {
                            "title": "Confidence",
                            "value": f"{alert.get('confidence', 0):.1%}",
                            "short": True,
                        },
                        {
                            "title": "Affected Nodes",
                            "value": ", ".join(alert.get('affected_nodes', ['None'])),
                            "short": False,
                        },
                        {
                            "title": "MITRE Techniques",
                            "value": ", ".join(alert.get('mitre_techniques', ['None'])),
                            "short": False,
                        },
                        {
                            "title": "Recommendations",
                            "value": "\n".join([f"• {r}" for r in alert.get('recommendations', ['Monitor'])]),
                            "short": False,
                        },
                    ],
                    "footer": f"Status: {alert.get('status', 'OPEN')} | {alert.get('timestamp', 'N/A')}",
                }
            ],
        }
    
    def format_dashboard(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format alert for dashboard.
        
        Args:
            alert: Alert data
            
        Returns:
            Dict[str, Any]: Dashboard format
        """
        return {
            "id": alert.get("alert_id"),
            "title": alert.get("title"),
            "severity": alert.get("severity"),
            "severity_color": {
                "LOW": "#2ecc71",
                "MEDIUM": "#f39c12",
                "HIGH": "#e67e22",
                "CRITICAL": "#e74c3c",
            }.get(alert.get("severity", "LOW"), "#95a5a6"),
            "risk_score": alert.get("risk_score", 0),
            "confidence": alert.get("confidence", 0),
            "attack_type": alert.get("attack_type"),
            "attack_path": alert.get("attack_path", []),
            "mitre_techniques": alert.get("mitre_techniques", []),
            "affected_nodes": alert.get("affected_nodes", []),
            "status": alert.get("status", "OPEN"),
            "timestamp": alert.get("timestamp"),
            "created_at": alert.get("created_at"),
            "updated_at": alert.get("updated_at"),
            "has_blockchain": alert.get("blockchain_verified", False),
            "priority": alert.get("priority", 2),
            "urgency": alert.get("urgency", "NORMAL"),
        }