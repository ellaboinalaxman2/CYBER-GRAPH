"""Risk engine for Member 5 - Attack Engine."""

from typing import Dict, Any, List, Optional
from datetime import datetime

from src.core.logging import get_logger
from src.risk.risk_scoring import RiskScorer
from src.risk.severity import SeverityCalculator, SeverityLevel
from src.risk.asset_criticality import AssetCriticalityManager
from src.risk.risk_rules import RiskRulesEngine


class RiskEngine:
    """
    Main risk engine for attack incidents.
    
    Features:
    - Calculate risk for incidents
    - Determine severity
    - Apply risk rules
    - Generate risk reports
    """
    
    def __init__(self):
        """Initialize the risk engine."""
        self.logger = get_logger("risk.risk_engine")
        self.risk_scorer = RiskScorer()
        self.severity_calculator = SeverityCalculator()
        self.asset_criticality = AssetCriticalityManager()
        self.risk_rules = RiskRulesEngine()
    
    def assess(
        self,
        incident: Dict[str, Any],
        events: List[Dict[str, Any]],
        predictions: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Assess risk for an incident.
        
        Args:
            incident: Incident data
            events: List of events
            predictions: AI predictions
            
        Returns:
            Dict[str, Any]: Risk assessment results
        """
        self.logger.info(f"Assessing risk for incident {incident.get('incident_id', 'unknown')}")
        
        # Extract data
        nodes = self._extract_nodes(incident, events)
        attack_type = incident.get("attack_type")
        event_severity = incident.get("severity")
        
        # Get anomaly scores from predictions
        anomaly_score = self._get_max_anomaly_score(nodes, predictions or [])
        
        # Build context for risk rules
        context = self._build_context(events, predictions)
        
        # Calculate risk
        risk_result = self.risk_scorer.calculate(
            anomaly_score=anomaly_score,
            nodes=nodes,
            attack_type=attack_type,
            event_severity=event_severity,
            additional_context=context,
        )
        
        # Calculate severity
        severity = self.severity_calculator.calculate(risk_result["risk_score"])
        
        # Get risk level
        risk_level = self.risk_scorer.get_risk_level(risk_result["risk_score"])
        
        # Build result
        result = {
            "incident_id": incident.get("incident_id"),
            "risk_score": risk_result["risk_score"],
            "severity": severity.value,
            "severity_color": self.severity_calculator.get_severity_color(severity),
            "severity_icon": self.severity_calculator.get_severity_icon(severity),
            "risk_level": risk_level["level"],
            "components": risk_result["components"],
            "applied_rules": risk_result["applied_rules"],
            "affected_nodes": nodes,
            "node_criticalities": risk_result["node_criticalities"],
            "max_criticality": max(risk_result["node_criticalities"].values()) if risk_result["node_criticalities"] else 0,
            "anomaly_score": anomaly_score,
            "recommendations": self._generate_recommendations(risk_result),
            "assessed_at": datetime.utcnow().isoformat() + "Z",
        }
        
        self.logger.info(f"Risk assessment complete: {result['risk_score']} ({result['severity']})")
        return result
    
    def _extract_nodes(self, incident: Dict[str, Any], events: List[Dict[str, Any]]) -> List[str]:
        """Extract nodes from incident and events."""
        nodes = set()
        
        # From incident
        if "nodes" in incident:
            nodes.update(incident["nodes"])
        
        # From attack path
        if "attack_path" in incident:
            for step in incident["attack_path"]:
                if "from" in step:
                    nodes.add(step["from"])
                if "to" in step:
                    nodes.add(step["to"])
        
        # From events
        for event in events:
            source = event.get("source_ip") or event.get("source_hostname")
            dest = event.get("destination_ip") or event.get("destination_hostname")
            if source:
                nodes.add(source)
            if dest:
                nodes.add(dest)
        
        return list(nodes)
    
    def _get_max_anomaly_score(self, nodes: List[str], predictions: List[Dict[str, Any]]) -> float:
        """Get maximum anomaly score from predictions."""
        if not predictions or not nodes:
            return 0.3
        
        max_score = 0.0
        for node in nodes:
            for pred in predictions:
                if pred.get("node_id") == node:
                    score = pred.get("anomaly_score", 0)
                    max_score = max(max_score, score)
        
        return max_score
    
    def _build_context(self, events: List[Dict[str, Any]], predictions: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Build context for risk rules."""
        context = {
            "failed_logins": 0,
            "file_access": False,
            "network_connection": False,
            "user_change": False,
            "source_is_external": False,
            "time_of_day": datetime.utcnow().hour,
        }
        
        for event in events:
            event_type = event.get("event_type", "")
            
            if "LOGIN_FAILURE" in event_type:
                context["failed_logins"] += 1
            elif "FILE_ACCESS" in event_type:
                context["file_access"] = True
            elif "NETWORK_CONNECTION" in event_type:
                context["network_connection"] = True
            elif "USER_MODIFIED" in event_type or "PERMISSION_CHANGE" in event_type:
                context["user_change"] = True
            
            # Check if source is external
            source = event.get("source_ip", "")
            if source and not source.startswith(("192.168.", "10.", "172.16.", "172.17.", "172.18.", "172.19.", "172.20.", "172.21.", "172.22.", "172.23.", "172.24.", "172.25.", "172.26.", "172.27.", "172.28.", "172.29.", "172.30.", "172.31.")):
                context["source_is_external"] = True
        
        return context
    
    def _generate_recommendations(self, risk_result: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on risk assessment."""
        recommendations = []
        
        risk_score = risk_result["risk_score"]
        severity = risk_result.get("severity", "LOW")
        
        if risk_score >= 85:
            recommendations.append("Immediate action required - isolate affected systems")
            recommendations.append("Notify security team and management")
            recommendations.append("Begin forensic investigation")
        elif risk_score >= 70:
            recommendations.append("Escalate to security team")
            recommendations.append("Contain affected systems")
            recommendations.append("Review access logs")
        elif risk_score >= 40:
            recommendations.append("Investigate suspicious activity")
            recommendations.append("Monitor affected systems")
            recommendations.append("Review security controls")
        else:
            recommendations.append("Monitor for unusual activity")
            recommendations.append("Continue regular security checks")
        
        # Add specific recommendations based on applied rules
        for rule in risk_result.get("applied_rules", []):
            if "critical" in rule.get("tags", []):
                recommendations.append(f"Review critical asset: {rule['description']}")
        
        return recommendations