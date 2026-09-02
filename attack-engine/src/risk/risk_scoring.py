"""Risk scoring for Member 5 - Attack Engine."""

from typing import Dict, Any, Optional, List
from datetime import datetime

from src.core.logging import get_logger
from src.risk.asset_criticality import AssetCriticalityManager
from src.risk.risk_rules import RiskRulesEngine


class RiskScorer:
    """
    Calculates risk scores for incidents.
    
    Features:
    - Combine multiple risk factors
    - Weighted scoring
    - Normalization
    - Confidence scoring
    """
    
    def __init__(self):
        """Initialize the risk scorer."""
        self.logger = get_logger("risk.risk_scoring")
        self.asset_criticality = AssetCriticalityManager()
        self.risk_rules = RiskRulesEngine()
        
        # Default weights
        self.weights = {
            "anomaly_score": 0.30,
            "asset_criticality": 0.25,
            "attack_severity": 0.20,
            "evidence_strength": 0.15,
            "rules_modifier": 0.10,
        }
    
    def calculate(
        self,
        anomaly_score: float,
        nodes: List[str],
        attack_type: Optional[str] = None,
        event_severity: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Calculate risk score.
        
        Args:
            anomaly_score: AI anomaly score (0-1)
            nodes: List of affected nodes
            attack_type: Type of attack
            event_severity: Event severity
            additional_context: Additional context
            
        Returns:
            Dict[str, Any]: Risk calculation results
        """
        self.logger.info(f"Calculating risk for {len(nodes)} nodes")
        
        # 1. Asset criticality
        criticality_scores = self.asset_criticality.get_criticality_for_nodes(nodes)
        avg_criticality = sum(criticality_scores.values()) / len(criticality_scores) if criticality_scores else 0
        max_criticality = max(criticality_scores.values()) if criticality_scores else 0
        
        # 2. Attack severity
        attack_severity_score = self._get_attack_severity_score(attack_type, event_severity)
        
        # 3. Evidence strength
        evidence_score = self._get_evidence_score(additional_context or {})
        
        # 4. Rules modifier
        context = {
            "anomaly_score": anomaly_score,
            "attack_type": attack_type,
            "asset_criticality": max_criticality,
            "failed_logins": additional_context.get("failed_logins", 0) if additional_context else 0,
            "file_access": additional_context.get("file_access", False) if additional_context else False,
            "network_connection": additional_context.get("network_connection", False) if additional_context else False,
            "user_change": additional_context.get("user_change", False) if additional_context else False,
            "source_is_external": additional_context.get("source_is_external", False) if additional_context else False,
            "time_of_day": datetime.utcnow().hour,
        }
        
        rules_result = self.risk_rules.apply_rules(context)
        
        # Calculate base risk
        base_risk = (
            (anomaly_score * 100) * self.weights["anomaly_score"] +
            max_criticality * self.weights["asset_criticality"] +
            attack_severity_score * self.weights["attack_severity"] +
            evidence_score * self.weights["evidence_strength"]
        )
        
        # Apply rules modifier
        total_risk = base_risk + (rules_result["total_modifier"] * self.weights["rules_modifier"])
        
        # Normalize to 0-100
        final_risk = min(max(total_risk, 0), 100)
        
        return {
            "risk_score": round(final_risk, 2),
            "components": {
                "anomaly_score": round(anomaly_score * 100, 2),
                "asset_criticality": round(max_criticality, 2),
                "attack_severity": round(attack_severity_score, 2),
                "evidence_strength": round(evidence_score, 2),
                "rules_modifier": round(rules_result["total_modifier"], 2),
            },
            "weights": self.weights,
            "applied_rules": rules_result["applied_rules"],
            "affected_nodes": nodes,
            "node_criticalities": criticality_scores,
        }
    
    def _get_attack_severity_score(self, attack_type: Optional[str], event_severity: Optional[str]) -> float:
        """Get attack severity score."""
        # Map attack types to severity scores
        attack_severity_map = {
            "lateral_movement": 80,
            "privilege_escalation": 85,
            "data_exfiltration": 90,
            "brute_force": 60,
            "malware": 85,
            "ransomware": 95,
            "phishing": 50,
            "dos": 70,
            "ddos": 75,
            "reconnaissance": 40,
            "unknown": 50,
        }
        
        # Map event severity to score
        severity_map = {
            "LOW": 20,
            "MEDIUM": 50,
            "HIGH": 75,
            "CRITICAL": 90,
        }
        
        # Try attack type first
        if attack_type:
            attack_lower = attack_type.lower().replace("_", " ")
            for key, value in attack_severity_map.items():
                if key.replace("_", " ") in attack_lower or attack_lower in key.replace("_", " "):
                    return value
        
        # Try event severity
        if event_severity:
            return severity_map.get(event_severity.upper(), 50)
        
        return 50
    
    def _get_evidence_score(self, context: Dict[str, Any]) -> float:
        """Get evidence strength score."""
        score = 0
        evidence_count = 0
        
        # Check evidence types
        evidence_weights = {
            "multiple_failed_logins": 15,
            "successful_login": 10,
            "network_connection": 10,
            "file_access": 15,
            "permission_change": 20,
            "user_creation": 15,
            "process_start": 10,
            "alert": 25,
        }
        
        for evidence, weight in evidence_weights.items():
            if context.get(evidence, False):
                score += weight
                evidence_count += 1
        
        # Cap at 100
        return min(score, 100)
    
    def get_risk_level(self, risk_score: float) -> Dict[str, Any]:
        """
        Get risk level from risk score.
        
        Args:
            risk_score: Risk score (0-100)
            
        Returns:
            Dict[str, Any]: Risk level information
        """
        if risk_score >= 85:
            return {"level": "CRITICAL", "color": "#e74c3c", "icon": "🚨"}
        elif risk_score >= 70:
            return {"level": "HIGH", "color": "#e67e22", "icon": "🔴"}
        elif risk_score >= 40:
            return {"level": "MEDIUM", "color": "#f39c12", "icon": "⚠️"}
        else:
            return {"level": "LOW", "color": "#2ecc71", "icon": "ℹ️"}
    
    def update_weights(self, weights: Dict[str, float]) -> None:
        """
        Update scoring weights.
        
        Args:
            weights: New weights (must sum to 1.0)
        """
        total = sum(weights.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0 (current: {total})")
        
        self.weights = weights
        self.logger.info(f"Updated risk weights: {weights}")