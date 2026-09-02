"""Technique mapper for Member 5 - Attack Engine."""

from typing import List, Dict, Any, Optional, Set
from collections import defaultdict

from src.core.logging import get_logger
from src.mitre.mitre_data import MitreData


class TechniqueMapper:
    """
    Maps behaviors to MITRE ATT&CK techniques.
    
    Features:
    - Map events to techniques
    - Map attack types to techniques
    - Map behaviors to techniques
    - Get technique details
    """
    
    def __init__(self):
        """Initialize the technique mapper."""
        self.logger = get_logger("mitre.technique_mapper")
        self.mitre_data = MitreData()
        
        # Mapping rules
        self.mapping_rules = self._default_rules()
    
    def _default_rules(self) -> Dict[str, List[str]]:
        """Default mapping rules."""
        return {
            # Authentication events
            "LOGIN_FAILURE": ["T1110", "T1110.001", "T1110.003"],
            "LOGIN_SUCCESS": ["T1078"],
            "LOGIN_LOCKOUT": ["T1110"],
            
            # Network events
            "NETWORK_CONNECTION": ["T1046", "T1021"],
            "NETWORK_DISCONNECTION": ["T1046"],
            "PORT_SCAN": ["T1046"],
            
            # Firewall events
            "FIREWALL_ALLOW": ["T1046"],
            "FIREWALL_DENY": ["T1562.004"],
            "FIREWALL_DROP": ["T1562.004"],
            
            # File events
            "FILE_ACCESS": ["T1083"],
            "FILE_MODIFIED": ["T1083", "T1562"],
            "FILE_DELETED": ["T1083", "T1562"],
            "FILE_CREATED": ["T1083"],
            
            # User events
            "USER_CREATED": ["T1078", "T1136"],
            "USER_DELETED": ["T1078", "T1136"],
            "USER_MODIFIED": ["T1078", "T1136"],
            "PERMISSION_CHANGE": ["T1068", "T1548"],
            
            # Process events
            "PROCESS_START": ["T1059"],
            "PROCESS_END": ["T1059"],
            
            # Alert events
            "ALERT": ["T1078", "T1068", "T1562"],
            
            # System events
            "SYSTEM_EVENT": ["T1059"],
            "AUDIT_EVENT": ["T1562"],
            
            # Custom attack types
            "brute_force": ["T1110"],
            "lateral_movement": ["T1021"],
            "privilege_escalation": ["T1068", "T1548"],
            "data_exfiltration": ["T1537", "T1048"],
            "reconnaissance": ["T1046"],
            "malware": ["T1059"],
            "ransomware": ["T1486"],
        }
    
    def map_event(self, event: Dict[str, Any]) -> List[str]:
        """
        Map an event to MITRE techniques.
        
        Args:
            event: Event data
            
        Returns:
            List[str]: Technique IDs
        """
        event_type = event.get("event_type", "")
        attack_type = event.get("attack_type", "")
        
        techniques = set()
        
        # Check event type mapping
        for key, tech_ids in self.mapping_rules.items():
            if key in event_type:
                techniques.update(tech_ids)
        
        # Check attack type mapping
        if attack_type:
            attack_lower = attack_type.lower()
            for key, tech_ids in self.mapping_rules.items():
                if key in attack_lower:
                    techniques.update(tech_ids)
        
        # Check behavior mapping
        if "message" in event:
            behavior = event.get("message", "")
            tech = self.mitre_data.get_technique_by_behavior(behavior)
            if tech:
                techniques.add(tech.get("id"))
        
        return list(techniques)
    
    def map_attack_type(self, attack_type: str) -> List[str]:
        """
        Map an attack type to techniques.
        
        Args:
            attack_type: Attack type
            
        Returns:
            List[str]: Technique IDs
        """
        attack_lower = attack_type.lower()
        techniques = set()
        
        for key, tech_ids in self.mapping_rules.items():
            if key in attack_lower:
                techniques.update(tech_ids)
        
        return list(techniques)
    
    def map_behavior(self, behavior: str) -> Optional[str]:
        """
        Map a behavior to a technique.
        
        Args:
            behavior: Behavior description
            
        Returns:
            Optional[str]: Technique ID
        """
        tech = self.mitre_data.get_technique_by_behavior(behavior)
        if tech:
            return tech.get("id")
        return None
    
    def get_technique_details(self, technique_id: str) -> Optional[Dict[str, Any]]:
        """
        Get details for a technique.
        
        Args:
            technique_id: Technique ID
            
        Returns:
            Optional[Dict[str, Any]]: Technique details
        """
        return self.mitre_data.get_technique(technique_id)
    
    def get_techniques_for_incident(
        self,
        events: List[Dict[str, Any]],
        attack_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get techniques for an incident.
        
        Args:
            events: List of events
            attack_type: Attack type
            
        Returns:
            List[Dict[str, Any]]: Techniques with details
        """
        technique_ids = set()
        
        # Map events
        for event in events:
            techniques = self.map_event(event)
            technique_ids.update(techniques)
        
        # Map attack type
        if attack_type:
            techniques = self.map_attack_type(attack_type)
            technique_ids.update(techniques)
        
        # Get details for each technique
        result = []
        for tech_id in technique_ids:
            details = self.get_technique_details(tech_id)
            if details:
                result.append(details)
        
        # Sort by ID
        result.sort(key=lambda x: x.get("id", ""))
        
        return result
    
    def add_mapping_rule(self, event_type: str, technique_ids: List[str]) -> None:
        """
        Add a mapping rule.
        
        Args:
            event_type: Event type
            technique_ids: Technique IDs
        """
        self.mapping_rules[event_type] = technique_ids
        self.logger.info(f"Added mapping rule: {event_type} -> {technique_ids}")