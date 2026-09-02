"""Protocol and application enrichment."""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

from src.enrichers.base import BaseEnricher


class ProtocolEnricher(BaseEnricher):
    """
    Enriches events with protocol and application information.
    
    Adds:
    - Application name (SSH, HTTP, etc.)
    - Application version (if available)
    - Protocol details
    - Service information
    """
    
    def __init__(self, protocol_db_path: Optional[str] = None):
        """
        Initialize protocol enricher.
        
        Args:
            protocol_db_path: Path to protocol mapping data JSON file
        """
        super().__init__(enricher_name="protocol-enricher")
        self.protocol_db_path = protocol_db_path or "data/enrichment_data/protocol_map.json"
        self.protocol_data = {}
        self._load_protocol_data()
    
    def _load_protocol_data(self) -> None:
        """Load protocol mapping data from file."""
        if os.path.exists(self.protocol_db_path):
            try:
                with open(self.protocol_db_path, 'r') as f:
                    self.protocol_data = json.load(f)
                self.logger.info(f"Loaded protocol data with {len(self.protocol_data)} mappings")
            except Exception as e:
                self.logger.warning(f"Failed to load protocol data: {e}")
                self._create_default_protocol_data()
        else:
            self.logger.info("No protocol data found, creating default")
            self._create_default_protocol_data()
    
    def _create_default_protocol_data(self) -> None:
        """Create default protocol mapping data."""
        self.protocol_data = {
            "port_mappings": {
                20: {"protocol": "FTP", "application": "FTP", "description": "FTP data"},
                21: {"protocol": "FTP", "application": "FTP", "description": "FTP control"},
                22: {"protocol": "SSH", "application": "SSH", "description": "SSH"},
                23: {"protocol": "TELNET", "application": "Telnet", "description": "Telnet"},
                25: {"protocol": "SMTP", "application": "SMTP", "description": "SMTP"},
                53: {"protocol": "DNS", "application": "DNS", "description": "DNS"},
                67: {"protocol": "DHCP", "application": "DHCP", "description": "DHCP server"},
                68: {"protocol": "DHCP", "application": "DHCP", "description": "DHCP client"},
                80: {"protocol": "HTTP", "application": "HTTP", "description": "HTTP"},
                110: {"protocol": "POP3", "application": "POP3", "description": "POP3"},
                123: {"protocol": "NTP", "application": "NTP", "description": "NTP"},
                143: {"protocol": "IMAP", "application": "IMAP", "description": "IMAP"},
                161: {"protocol": "SNMP", "application": "SNMP", "description": "SNMP"},
                443: {"protocol": "HTTPS", "application": "HTTPS", "description": "HTTPS"},
                445: {"protocol": "SMB", "application": "SMB", "description": "SMB"},
                465: {"protocol": "SMTPS", "application": "SMTPS", "description": "SMTPS"},
                587: {"protocol": "SMTP", "application": "SMTP", "description": "SMTP submission"},
                636: {"protocol": "LDAPS", "application": "LDAPS", "description": "LDAPS"},
                993: {"protocol": "IMAPS", "application": "IMAPS", "description": "IMAPS"},
                995: {"protocol": "POP3S", "application": "POP3S", "description": "POP3S"},
                1433: {"protocol": "MSSQL", "application": "Microsoft SQL Server", "description": "MSSQL"},
                1521: {"protocol": "ORACLE", "application": "Oracle Database", "description": "Oracle"},
                3306: {"protocol": "MYSQL", "application": "MySQL", "description": "MySQL"},
                3389: {"protocol": "RDP", "application": "RDP", "description": "RDP"},
                5432: {"protocol": "POSTGRESQL", "application": "PostgreSQL", "description": "PostgreSQL"},
                6379: {"protocol": "REDIS", "application": "Redis", "description": "Redis"},
                27017: {"protocol": "MONGODB", "application": "MongoDB", "description": "MongoDB"},
            },
            "protocol_aliases": {
                "tcp": "TCP",
                "udp": "UDP",
                "icmp": "ICMP",
                "http": "HTTP",
                "https": "HTTPS",
                "ssh": "SSH",
                "ftp": "FTP",
                "smtp": "SMTP",
                "dns": "DNS",
            },
        }
        
        # Save default data
        os.makedirs(os.path.dirname(self.protocol_db_path), exist_ok=True)
        with open(self.protocol_db_path, 'w') as f:
            json.dump(self.protocol_data, f, indent=2)
        
        self.logger.info(f"Created default protocol data at {self.protocol_db_path}")
    
    def enrich(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich event with protocol and application information.
        
        Args:
            event: Event data to enrich
            
        Returns:
            Dict[str, Any]: Event with protocol enrichment
        """
        if not self.enabled:
            return event
        
        result = event.copy()
        enrichments_applied = []
        
        # Get destination port
        dest_port = self._get_port(event, "destination")
        
        # Get protocol (might already be set)
        current_protocol = self._safe_get(event, "protocol")
        
        # Map port to protocol
        if dest_port and dest_port in self.protocol_data["port_mappings"]:
            mapping = self.protocol_data["port_mappings"][dest_port]
            
            # Only set if not already set or if we have better info
            if not current_protocol or current_protocol == "UNKNOWN":
                result["protocol"] = mapping["protocol"]
                result["application_name"] = mapping["application"]
                result["_protocol_mapped_from_port"] = True
                enrichments_applied.append("protocol_mapping")
                
                self.logger.debug(f"Mapped port {dest_port} to {mapping['protocol']}")
        
        # Normalize protocol aliases
        if "protocol" in result and result["protocol"]:
            proto = result["protocol"].upper()
            if proto in self.protocol_data.get("protocol_aliases", {}):
                result["protocol"] = self.protocol_data["protocol_aliases"][proto]
                if "protocol_mapping" not in enrichments_applied:
                    enrichments_applied.append("protocol_normalization")
        
        # Update metadata
        if enrichments_applied:
            if "enrichment_applied" not in result:
                result["enrichment_applied"] = []
            result["enrichment_applied"].extend(enrichments_applied)
        
        self._update_stats(success=True, enrichments_count=len(enrichments_applied))
        return result
    
    def _get_port(self, event: Dict[str, Any], field: str) -> Optional[int]:
        """Get port from event."""
        # Try direct field
        port = self._safe_get(event, f"{field}_port")
        if port:
            try:
                return int(port)
            except (ValueError, TypeError):
                pass
        
        # Try nested object
        obj = self._safe_get(event, field)
        if obj and isinstance(obj, dict):
            port = obj.get("port")
            if port:
                try:
                    return int(port)
                except (ValueError, TypeError):
                    pass
        
        # Try dport/sport
        if field == "destination":
            port = self._safe_get(event, "dport")
            if port:
                try:
                    return int(port)
                except (ValueError, TypeError):
                    pass
        elif field == "source":
            port = self._safe_get(event, "sport")
            if port:
                try:
                    return int(port)
                except (ValueError, TypeError):
                    pass
        
        return None