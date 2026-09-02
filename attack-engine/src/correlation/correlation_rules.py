"""Correlation rules for Member 5 - Attack Engine."""

from typing import Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class CorrelationRule:
    """Correlation rule definition."""
    
    name: str
    description: str
    event_types: List[str]
    min_count: int
    time_window: int  # seconds
    severity: str = "MEDIUM"
    risk_score: float = 50.0
    tags: List[str] = field(default_factory=list)


class CorrelationRules:
    """Collection of correlation rules."""
    
    @staticmethod
    def get_all_rules() -> List[CorrelationRule]:
        """Get all correlation rules."""
        return [
            CorrelationRule(
                name="brute_force",
                description="Multiple login failures from same source",
                event_types=["LOGIN_FAILURE"],
                min_count=5,
                time_window=300,
                severity="HIGH",
                risk_score=75.0,
                tags=["authentication", "brute_force"],
            ),
            CorrelationRule(
                name="successful_brute_force",
                description="Multiple failures followed by success",
                event_types=["LOGIN_FAILURE", "LOGIN_SUCCESS"],
                min_count=6,
                time_window=600,
                severity="HIGH",
                risk_score=80.0,
                tags=["authentication", "brute_force", "compromise"],
            ),
            CorrelationRule(
                name="lateral_movement",
                description="Successful login then network connection",
                event_types=["LOGIN_SUCCESS", "NETWORK_CONNECTION"],
                min_count=2,
                time_window=600,
                severity="HIGH",
                risk_score=75.0,
                tags=["network", "lateral_movement"],
            ),
            CorrelationRule(
                name="data_exfiltration",
                description="File access with network connection",
                event_types=["FILE_ACCESS", "NETWORK_CONNECTION", "FILE_MODIFIED"],
                min_count=3,
                time_window=3600,
                severity="CRITICAL",
                risk_score=85.0,
                tags=["data_exfiltration", "file_access"],
            ),
            CorrelationRule(
                name="privilege_escalation",
                description="Permission or user modifications",
                event_types=["PERMISSION_CHANGE", "USER_MODIFIED", "GROUP_CHANGE"],
                min_count=2,
                time_window=300,
                severity="HIGH",
                risk_score=78.0,
                tags=["privilege_escalation", "user_modification"],
            ),
            CorrelationRule(
                name="port_scanning",
                description="Multiple connection attempts to different ports",
                event_types=["NETWORK_CONNECTION", "FIREWALL_DENY"],
                min_count=10,
                time_window=120,
                severity="MEDIUM",
                risk_score=60.0,
                tags=["scanning", "network_recon"],
            ),
            CorrelationRule(
                name="malware_behavior",
                description="Alert with suspicious file access",
                event_types=["ALERT", "FILE_ACCESS", "PROCESS_START"],
                min_count=3,
                time_window=1800,
                severity="CRITICAL",
                risk_score=90.0,
                tags=["malware", "suspicious"],
            ),
        ]