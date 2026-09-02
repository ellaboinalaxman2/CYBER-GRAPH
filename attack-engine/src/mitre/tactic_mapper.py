"""Tactic mapper for Member 5 - Attack Engine."""

from typing import List, Dict, Any, Optional, Set
from collections import defaultdict

from src.core.logging import get_logger
from src.mitre.mitre_data import MitreData
from src.mitre.technique_mapper import TechniqueMapper


class TacticMapper:
    """
    Maps techniques to MITRE ATT&CK tactics.
    
    Features:
    - Map techniques to tactics
    - Get tactics for incident
    - Tactic coverage analysis
    - Tactic chains
    """
    
    def __init__(self):
        """Initialize the tactic mapper."""
        self.logger = get_logger("mitre.tactic_mapper")
        self.mitre_data = MitreData()
        self.technique_mapper = TechniqueMapper()
        
        # Tactic order (for chain analysis)
        self.tactic_order = [
            "Reconnaissance",
            "Resource Development",
            "Initial Access",
            "Execution",
            "Persistence",
            "Privilege Escalation",
            "Defense Evasion",
            "Credential Access",
            "Discovery",
            "Lateral Movement",
            "Collection",
            "Command and Control",
            "Exfiltration",
            "Impact"
        ]
    
    def get_tactics_for_technique(self, technique_id: str) -> List[str]:
        """
        Get tactics for a technique.
        
        Args:
            technique_id: Technique ID
            
        Returns:
            List[str]: Tactic names
        """
        technique = self.mitre_data.get_technique(technique_id)
        if technique:
            return technique.get("tactics", [])
        return []
    
    def get_tactics_for_techniques(self, technique_ids: List[str]) -> Set[str]:
        """
        Get tactics for multiple techniques.
        
        Args:
            technique_ids: Technique IDs
            
        Returns:
            Set[str]: Tactic names
        """
        tactics = set()
        for tech_id in technique_ids:
            tactics.update(self.get_tactics_for_technique(tech_id))
        return tactics
    
    def get_tactics_for_incident(
        self,
        events: List[Dict[str, Any]],
        attack_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get tactics for an incident.
        
        Args:
            events: List of events
            attack_type: Attack type
            
        Returns:
            Dict[str, Any]: Tactics analysis
        """
        # Get techniques first
        techniques = self.technique_mapper.get_techniques_for_incident(events, attack_type)
        
        # Extract tactic coverage
        tactic_map = defaultdict(list)
        for technique in techniques:
            tech_id = technique.get("id")
            for tactic in technique.get("tactics", []):
                tactic_map[tactic].append(tech_id)
        
        # Analyze tactic chain
        chain = self._analyze_tactic_chain(list(tactic_map.keys()))
        
        return {
            "techniques": techniques,
            "tactics": dict(tactic_map),
            "tactic_coverage": len(tactic_map),
            "total_techniques": len(techniques),
            "tactic_chain": chain,
            "tactic_chain_length": len(chain),
            "all_tactics": list(tactic_map.keys()),
            "tactic_order": self._get_tactic_order(),
        }
    
    def _analyze_tactic_chain(self, tactics: List[str]) -> List[str]:
        """
        Analyze tactic chain (ordered sequence of tactics).
        
        Args:
            tactics: List of tactics
            
        Returns:
            List[str]: Ordered tactic chain
        """
        # Sort tactics by order
        chain = []
        for tactic in self.tactic_order:
            if tactic in tactics:
                chain.append(tactic)
        
        return chain
    
    def _get_tactic_order(self) -> Dict[str, int]:
        """
        Get tactic order mapping.
        
        Returns:
            Dict[str, int]: Tactic to order mapping
        """
        return {tactic: idx for idx, tactic in enumerate(self.tactic_order)}
    
    def get_attack_phase(self, tactics: List[str]) -> str:
        """
        Get attack phase based on tactics.
        
        Args:
            tactics: List of tactics
            
        Returns:
            str: Attack phase
        """
        if any(t in tactics for t in ["Initial Access", "Execution"]):
            return "Initial Compromise"
        elif any(t in tactics for t in ["Persistence", "Privilege Escalation", "Defense Evasion"]):
            return "Establish Foothold"
        elif any(t in tactics for t in ["Discovery", "Lateral Movement"]):
            return "Internal Reconnaissance & Movement"
        elif any(t in tactics for t in ["Collection", "Exfiltration"]):
            return "Data Exfiltration"
        elif any(t in tactics for t in ["Impact"]):
            return "Impact & Destruction"
        else:
            return "Unknown"
    
    def get_tactic_description(self, tactic: str) -> str:
        """
        Get description for a tactic.
        
        Args:
            tactic: Tactic name
            
        Returns:
            str: Tactic description
        """
        descriptions = {
            "Reconnaissance": "Gathering information about the target",
            "Resource Development": "Establishing resources for the attack",
            "Initial Access": "Gaining initial entry into the target",
            "Execution": "Running malicious code",
            "Persistence": "Maintaining access to the target",
            "Privilege Escalation": "Obtaining higher-level permissions",
            "Defense Evasion": "Avoiding detection",
            "Credential Access": "Stealing credentials",
            "Discovery": "Exploring the target environment",
            "Lateral Movement": "Moving through the target network",
            "Collection": "Gathering target data",
            "Command and Control": "Communicating with compromised systems",
            "Exfiltration": "Stealing data from the target",
            "Impact": "Damaging the target",
        }
        return descriptions.get(tactic, "Unknown tactic")