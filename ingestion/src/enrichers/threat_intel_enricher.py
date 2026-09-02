"""Threat intelligence enrichment."""

import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from src.enrichers.base import BaseEnricher
from src.models.enriched_event import ThreatIntel


class ThreatIntelEnricher(BaseEnricher):
    """
    Enriches events with threat intelligence data.
    
    Adds:
    - Malicious flag
    - Reputation score
    - Threat feed source
    - Threat category
    - Confidence score
    - Threat families
    """
    
    def __init__(self, threat_db_path: Optional[str] = None):
        """
        Initialize threat intelligence enricher.
        
        Args:
            threat_db_path: Path to threat intelligence data JSON file
        """
        super().__init__(enricher_name="threat-intel-enricher")
        self.threat_db_path = threat_db_path or "data/enrichment_data/threat_intel.json"
        self.threat_data = {}
        self._load_threat_data()
    
    def _load_threat_data(self) -> None:
        """Load threat intelligence data from file."""
        if os.path.exists(self.threat_db_path):
            try:
                with open(self.threat_db_path, 'r') as f:
                    self.threat_data = json.load(f)
                self.logger.info(f"Loaded threat intelligence data with {len(self.threat_data)} entries")
            except Exception as e:
                self.logger.warning(f"Failed to load threat data: {e}")
                self._create_default_threat_data()
        else:
            self.logger.info("No threat intelligence data found, creating default")
            self._create_default_threat_data()
    
    def _create_default_threat_data(self) -> None:
        """Create default threat intelligence data."""
        self.threat_data = {
            "192.168.1.50": {
                "is_malicious": True,
                "reputation_score": 85,
                "threat_feed": "Internal SIEM",
                "threat_category": "brute_force",
                "confidence": 0.92,
                "threat_families": ["BruteForce", "Scanning"],
                "first_seen": "2026-08-20T00:00:00Z",
                "last_seen": "2026-08-29T10:30:00Z",
                "references": ["Internal SIEM Alert #12345"],
            },
            "10.0.0.5": {
                "is_malicious": True,
                "reputation_score": 75,
                "threat_feed": "Internal SIEM",
                "threat_category": "scanning",
                "confidence": 0.85,
                "threat_families": ["PortScan"],
                "first_seen": "2026-08-25T00:00:00Z",
                "last_seen": "2026-08-29T10:30:00Z",
                "references": ["Internal SIEM Alert #12346"],
            },
            "185.130.5.253": {
                "is_malicious": True,
                "reputation_score": 95,
                "threat_feed": "VirusTotal",
                "threat_category": "malware",
                "confidence": 0.98,
                "threat_families": ["Mirai", "Gafgyt"],
                "first_seen": "2026-07-01T00:00:00Z",
                "last_seen": "2026-08-29T00:00:00Z",
                "references": [
                    "https://www.virustotal.com/gui/ip-address/185.130.5.253",
                    "https://www.abuseipdb.com/check/185.130.5.253",
                ],
            },
        }
        
        # Save default data
        os.makedirs(os.path.dirname(self.threat_db_path), exist_ok=True)
        with open(self.threat_db_path, 'w') as f:
            json.dump(self.threat_data, f, indent=2)
        
        self.logger.info(f"Created default threat intelligence data at {self.threat_db_path}")
    
    def enrich(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich event with threat intelligence.
        
        Args:
            event: Event data to enrich
            
        Returns:
            Dict[str, Any]: Event with threat intelligence
        """
        if not self.enabled:
            return event
        
        result = event.copy()
        
        # Get source IP
        source_ip = self._get_ip(event, "source")
        dest_ip = self._get_ip(event, "destination")
        
        # Check threat intelligence for source IP
        threat_intel = None
        if source_ip and source_ip in self.threat_data:
            threat_data = self.threat_data[source_ip]
            threat_intel = ThreatIntel(**threat_data)
            self.logger.debug(f"Threat intelligence found for source {source_ip}")
        
        # Also check destination IP
        if dest_ip and dest_ip in self.threat_data and not threat_intel:
            threat_data = self.threat_data[dest_ip]
            threat_intel = ThreatIntel(**threat_data)
            self.logger.debug(f"Threat intelligence found for destination {dest_ip}")
        
        if threat_intel:
            result["threat_intel"] = threat_intel.dict()
            if "enrichment_applied" not in result:
                result["enrichment_applied"] = []
            result["enrichment_applied"].append("threat_intel")
            self._update_stats(success=True, enrichments_count=1)
        else:
            self._update_stats(success=True, enrichments_count=0)
        
        return result
    
    def _get_ip(self, event: Dict[str, Any], field: str) -> Optional[str]:
        """Get IP address from event."""
        # Try direct field
        ip = self._safe_get(event, f"{field}_ip")
        if ip:
            return ip
        
        # Try nested object
        obj = self._safe_get(event, field)
        if obj and isinstance(obj, dict):
            ip = obj.get("ip")
            if ip:
                return ip
        
        return None
    
    def add_threat_intel(self, ip: str, threat_data: Dict[str, Any]) -> None:
        """
        Add or update threat intelligence for an IP.
        
        Args:
            ip: IP address
            threat_data: Threat intelligence data dictionary
        """
        self.threat_data[ip] = threat_data
        self._save_threat_data()
        self.logger.info(f"Added/updated threat intelligence for {ip}")
    
    def _save_threat_data(self) -> None:
        """Save threat intelligence data to file."""
        try:
            os.makedirs(os.path.dirname(self.threat_db_path), exist_ok=True)
            with open(self.threat_db_path, 'w') as f:
                json.dump(self.threat_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save threat data: {e}")