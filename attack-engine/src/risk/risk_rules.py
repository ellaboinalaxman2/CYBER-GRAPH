"""Risk rules for Member 5 - Attack Engine."""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field

from src.core.logging import get_logger


@dataclass
class RiskRule:
    """Risk rule definition."""
    
    name: str
    description: str
    condition: Dict[str, Any]
    score_modifier: float
    severity: str = "MEDIUM"
    tags: List[str] = field(default_factory=list)


class RiskRulesEngine:
    """
    Risk rules engine for applying business rules to risk scoring.
    
    Features:
    - Define risk rules
    - Apply rules to risk calculation
    - Rule priority
    - Dynamic rule updates
    """
    
    def __init__(self):
        """Initialize the risk rules engine."""
        self.logger = get_logger("risk.risk_rules")
        self.rules = self._default_rules()
    
    def _default_rules(self) -> List[RiskRule]:
        """Default risk rules."""
        return [
            RiskRule(
                name="critical_asset_compromise",
                description="Critical asset compromised",
                condition={
                    "asset_criticality": {"operator": ">=", "value": 80},
                    "anomaly_score": {"operator": ">=", "value": 0.7},
                },
                score_modifier=25,
                severity="CRITICAL",
                tags=["critical", "compromise"],
            ),
            RiskRule(
                name="lateral_movement_detected",
                description="Lateral movement detected",
                condition={
                    "attack_type": "lateral_movement",
                    "path_length": {"operator": ">=", "value": 2},
                },
                score_modifier=20,
                severity="HIGH",
                tags=["lateral_movement", "network"],
            ),
            RiskRule(
                name="brute_force_successful",
                description="Successful brute force attack",
                condition={
                    "attack_type": "brute_force",
                    "anomaly_score": {"operator": ">=", "value": 0.8},
                },
                score_modifier=15,
                severity="HIGH",
                tags=["brute_force", "authentication"],
            ),
            RiskRule(
                name="data_exfiltration_suspected",
                description="Data exfiltration suspected",
                condition={
                    "attack_type": "data_exfiltration",
                    "file_access": True,
                    "network_connection": True,
                },
                score_modifier=30,
                severity="CRITICAL",
                tags=["data_exfiltration", "data_loss"],
            ),
            RiskRule(
                name="privilege_escalation",
                description="Privilege escalation detected",
                condition={
                    "attack_type": "privilege_escalation",
                    "user_change": True,
                },
                score_modifier=25,
                severity="CRITICAL",
                tags=["privilege_escalation", "security"],
            ),
            RiskRule(
                name="multiple_failures",
                description="Multiple authentication failures",
                condition={
                    "failed_logins": {"operator": ">=", "value": 5},
                },
                score_modifier=10,
                severity="MEDIUM",
                tags=["authentication", "brute_force"],
            ),
            RiskRule(
                name="suspicious_time_activity",
                description="Suspicious activity at unusual time",
                condition={
                    "time_of_day": {"operator": "not_in", "value": [8, 9, 10, 11, 12, 13, 14, 15, 16, 17]},
                },
                score_modifier=5,
                severity="LOW",
                tags=["anomaly", "time_pattern"],
            ),
            RiskRule(
                name="external_threat",
                description="External threat detected",
                condition={
                    "source_is_external": True,
                    "anomaly_score": {"operator": ">=", "value": 0.6},
                },
                score_modifier=15,
                severity="HIGH",
                tags=["external", "threat"],
            ),
        ]
    
    def apply_rules(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply risk rules to a context.
        
        Args:
            context: Risk context (event data, predictions, etc.)
            
        Returns:
            Dict[str, Any]: Applied rules and score modifiers
        """
        applied_rules = []
        total_modifier = 0
        
        for rule in self.rules:
            if self._check_condition(rule.condition, context):
                applied_rules.append({
                    "name": rule.name,
                    "description": rule.description,
                    "modifier": rule.score_modifier,
                    "severity": rule.severity,
                    "tags": rule.tags,
                })
                total_modifier += rule.score_modifier
        
        return {
            "applied_rules": applied_rules,
            "total_modifier": min(total_modifier, 100),
            "rule_count": len(applied_rules),
        }
    
    def _check_condition(self, condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Check if a condition is met.
        
        Args:
            condition: Condition dictionary
            context: Context data
            
        Returns:
            bool: True if condition is met
        """
        for key, value in condition.items():
            if key == "operator":
                continue
            
            # Get context value
            context_value = context.get(key)
            if context_value is None:
                return False
            
            # Check operator
            operator = value.get("operator", "equals")
            compare_value = value.get("value")
            
            if operator == "equals":
                if context_value != compare_value:
                    return False
            elif operator == "not_equals":
                if context_value == compare_value:
                    return False
            elif operator == ">=":
                if context_value < compare_value:
                    return False
            elif operator == ">":
                if context_value <= compare_value:
                    return False
            elif operator == "<=":
                if context_value > compare_value:
                    return False
            elif operator == "<":
                if context_value >= compare_value:
                    return False
            elif operator == "in":
                if context_value not in compare_value:
                    return False
            elif operator == "not_in":
                if context_value in compare_value:
                    return False
            elif operator == "contains":
                if compare_value not in context_value:
                    return False
        
        return True
    
    def add_rule(self, rule: RiskRule) -> None:
        """
        Add a new risk rule.
        
        Args:
            rule: Risk rule
        """
        self.rules.append(rule)
        self.logger.info(f"Added risk rule: {rule.name}")
    
    def remove_rule(self, rule_name: str) -> bool:
        """
        Remove a risk rule.
        
        Args:
            rule_name: Rule name
            
        Returns:
            bool: True if removed
        """
        for i, rule in enumerate(self.rules):
            if rule.name == rule_name:
                self.rules.pop(i)
                self.logger.info(f"Removed risk rule: {rule_name}")
                return True
        return False
    
    def get_rules(self) -> List[Dict[str, Any]]:
        """
        Get all rules.
        
        Returns:
            List[Dict[str, Any]]: All rules
        """
        return [
            {
                "name": rule.name,
                "description": rule.description,
                "condition": rule.condition,
                "score_modifier": rule.score_modifier,
                "severity": rule.severity,
                "tags": rule.tags,
            }
            for rule in self.rules
        ]