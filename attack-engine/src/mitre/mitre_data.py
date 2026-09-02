"""MITRE ATT&CK data management for Member 5 - Attack Engine."""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path

from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import MitreError


class MitreData:
    """
    Manages MITRE ATT&CK data.
    
    Features:
    - Load MITRE data from JSON
    - Get techniques by ID
    - Get techniques by tactic
    - Search techniques
    - Update MITRE data
    """
    
    _instance = None
    _data = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the MITRE data manager."""
        if not hasattr(self, '_initialized'):
            self.logger = get_logger("mitre.mitre_data")
            self._initialized = True
            self._load_data()
    
    def _load_data(self) -> None:
        """Load MITRE data from JSON file."""
        try:
            data_path = Path(settings.mitre_data_path)
            
            if not data_path.exists():
                self.logger.warning(f"MITRE data file not found at {data_path}, using default")
                self._data = self._default_data()
                return
            
            with open(data_path, 'r') as f:
                self._data = json.load(f)
            
            self.logger.info(f"Loaded MITRE data with {len(self._data.get('techniques', []))} techniques")
            
        except Exception as e:
            self.logger.error(f"Failed to load MITRE data: {e}")
            self._data = self._default_data()
    
    def _default_data(self) -> Dict[str, Any]:
        """Default MITRE data if file not found."""
        return {
            "techniques": [],
            "tactics": [
                "Reconnaissance", "Resource Development", "Initial Access",
                "Execution", "Persistence", "Privilege Escalation",
                "Defense Evasion", "Credential Access", "Discovery",
                "Lateral Movement", "Collection", "Command and Control",
                "Exfiltration", "Impact"
            ],
            "version": "14.1",
            "last_updated": "2026-09-01T00:00:00Z"
        }
    
    def get_technique(self, technique_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a technique by ID.
        
        Args:
            technique_id: Technique ID
            
        Returns:
            Optional[Dict[str, Any]]: Technique data
        """
        for technique in self._data.get("techniques", []):
            if technique.get("id") == technique_id:
                return technique
            
            # Check subtechniques
            for sub in technique.get("subtechniques", []):
                if sub.get("id") == technique_id:
                    return {
                        "id": sub.get("id"),
                        "name": sub.get("name"),
                        "tactics": technique.get("tactics", []),
                        "is_subtechnique": True,
                        "parent": technique.get("id"),
                    }
        
        return None
    
    def get_techniques_by_tactic(self, tactic: str) -> List[Dict[str, Any]]:
        """
        Get techniques for a tactic.
        
        Args:
            tactic: Tactic name
            
        Returns:
            List[Dict[str, Any]]: Techniques
        """
        results = []
        for technique in self._data.get("techniques", []):
            if tactic in technique.get("tactics", []):
                results.append(technique)
        return results
    
    def search_techniques(self, query: str) -> List[Dict[str, Any]]:
        """
        Search techniques by name or description.
        
        Args:
            query: Search query
            
        Returns:
            List[Dict[str, Any]]: Matching techniques
        """
        query_lower = query.lower()
        results = []
        
        for technique in self._data.get("techniques", []):
            if query_lower in technique.get("name", "").lower():
                results.append(technique)
            elif query_lower in technique.get("description", "").lower():
                results.append(technique)
            
            # Check subtechniques
            for sub in technique.get("subtechniques", []):
                if query_lower in sub.get("name", "").lower():
                    results.append({
                        "id": sub.get("id"),
                        "name": sub.get("name"),
                        "tactics": technique.get("tactics", []),
                        "is_subtechnique": True,
                        "parent": technique.get("id"),
                    })
        
        return results
    
    def get_all_techniques(self) -> List[Dict[str, Any]]:
        """
        Get all techniques.
        
        Returns:
            List[Dict[str, Any]]: All techniques
        """
        return self._data.get("techniques", [])
    
    def get_all_tactics(self) -> List[str]:
        """
        Get all tactics.
        
        Returns:
            List[str]: All tactics
        """
        return self._data.get("tactics", [])
    
    def get_technique_by_behavior(self, behavior: str) -> Optional[Dict[str, Any]]:
        """
        Map behavior to technique.
        
        Args:
            behavior: Behavior description
            
        Returns:
            Optional[Dict[str, Any]]: Matching technique
        """
        behavior_lower = behavior.lower()
        
        # Map behaviors to technique IDs
        behavior_map = {
            # Authentication attacks
            "password guessing": "T1110",
            "brute force": "T1110",
            "password spraying": "T1110.003",
            "credential dumping": "T1003",
            
            # Lateral movement
            "ssh": "T1021.004",
            "rdp": "T1021.001",
            "smb": "T1021.002",
            "winrm": "T1021.006",
            "remote desktop": "T1021.001",
            
            # Discovery
            "port scan": "T1046",
            "network scan": "T1046",
            "file discovery": "T1083",
            "account discovery": "T1087",
            
            # Execution
            "powershell": "T1059.001",
            "command shell": "T1059.003",
            "unix shell": "T1059.004",
            
            # Privilege escalation
            "privilege escalation": "T1068",
            
            # Defense evasion
            "disable firewall": "T1562.004",
            "disable logging": "T1562.002",
            
            # Exfiltration
            "data exfiltration": "T1537",
            "file access": "T1083",
        }
        
        # Check exact matches
        for key, tech_id in behavior_map.items():
            if key in behavior_lower:
                return self.get_technique(tech_id)
        
        # Check partial matches
        for technique in self._data.get("techniques", []):
            if behavior_lower in technique.get("name", "").lower():
                return technique
        
        return None