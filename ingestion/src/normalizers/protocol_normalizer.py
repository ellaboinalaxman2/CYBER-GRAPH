"""Protocol normalizer."""

from typing import Optional, Dict, Any
import re

from src.normalizers.base import BaseNormalizer
from src.models.common import Protocol


class ProtocolNormalizer(BaseNormalizer):
    """
    Normalizes protocol names to standard format.
    
    Handles:
    - Various protocol name variations
    - Protocol number to name conversion
    - Port to protocol mapping
    """
    
    # Protocol mappings
    PROTOCOL_MAPPINGS = {
        # TCP-related
        'tcp': 'TCP',
        'TCP': 'TCP',
        '6': 'TCP',
        'tcp6': 'TCP',
        # UDP-related
        'udp': 'UDP',
        'UDP': 'UDP',
        '17': 'UDP',
        'udp6': 'UDP',
        # ICMP-related
        'icmp': 'ICMP',
        'ICMP': 'ICMP',
        '1': 'ICMP',
        # HTTP-related
        'http': 'HTTP',
        'HTTP': 'HTTP',
        'https': 'HTTPS',
        'HTTPS': 'HTTPS',
        '443': 'HTTPS',
        '80': 'HTTP',
        # SSH-related
        'ssh': 'SSH',
        'SSH': 'SSH',
        '22': 'SSH',
        # FTP-related
        'ftp': 'FTP',
        'FTP': 'FTP',
        '21': 'FTP',
        # DNS-related
        'dns': 'DNS',
        'DNS': 'DNS',
        '53': 'DNS',
        # SMTP-related
        'smtp': 'SMTP',
        'SMTP': 'SMTP',
        '25': 'SMTP',
        # Others
        'rdp': 'RDP',
        'RDP': 'RDP',
        '3389': 'RDP',
        'smb': 'SMB',
        'SMB': 'SMB',
        '445': 'SMB',
        'ldap': 'LDAP',
        'LDAP': 'LDAP',
        '389': 'LDAP',
        'ntp': 'NTP',
        'NTP': 'NTP',
        '123': 'NTP',
        'dhcp': 'DHCP',
        'DHCP': 'DHCP',
        '67': 'DHCP',
        '68': 'DHCP',
        'snmp': 'SNMP',
        'SNMP': 'SNMP',
        '161': 'SNMP',
        '162': 'SNMP',
    }
    
    # Port to protocol mapping
    PORT_PROTOCOL = {
        20: 'FTP',
        21: 'FTP',
        22: 'SSH',
        23: 'TELNET',
        25: 'SMTP',
        53: 'DNS',
        67: 'DHCP',
        68: 'DHCP',
        80: 'HTTP',
        110: 'POP3',
        123: 'NTP',
        143: 'IMAP',
        161: 'SNMP',
        162: 'SNMP',
        389: 'LDAP',
        443: 'HTTPS',
        445: 'SMB',
        465: 'SMTPS',
        587: 'SMTP',
        636: 'LDAPS',
        993: 'IMAPS',
        995: 'POP3S',
        1433: 'MSSQL',
        1521: 'ORACLE',
        3306: 'MYSQL',
        3389: 'RDP',
        5432: 'POSTGRESQL',
        6379: 'REDIS',
        27017: 'MONGODB',
    }
    
    def __init__(self, use_port_mapping: bool = True):
        """
        Initialize protocol normalizer.
        
        Args:
            use_port_mapping: Whether to infer protocol from port
        """
        super().__init__(normalizer_name="protocol-normalizer")
        self.use_port_mapping = use_port_mapping
    
    def normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize protocol fields in the data.
        
        Args:
            data: Dictionary containing protocol data
            
        Returns:
            Dict[str, Any]: Data with normalized protocol
        """
        result = data.copy()
        
        # Find protocol field
        protocol_keys = ["protocol", "proto", "protocol_name", "transport_protocol"]
        
        protocol = None
        for key in protocol_keys:
            value = self._safe_get(data, key)
            if value:
                protocol = value
                break
        
        # If no protocol found, try to infer from port
        if not protocol and self.use_port_mapping:
            dest_port = self._safe_get(data, "destination_port") or self._safe_get(data, "dport")
            if dest_port:
                try:
                    port = int(dest_port)
                    if port in self.PORT_PROTOCOL:
                        protocol = self.PORT_PROTOCOL[port]
                        result["_protocol_inferred_from_port"] = True
                except (ValueError, TypeError):
                    pass
        
        if protocol:
            normalized = self._normalize_protocol(protocol)
            if normalized:
                result["protocol"] = normalized
                result["_protocol_normalized"] = True
                self._update_stats(success=True, fields_count=1)
            else:
                result["protocol"] = "UNKNOWN"
                result["_protocol_normalization_error"] = f"Unknown protocol: {protocol}"
                self._update_stats(success=False)
        
        return result
    
    def _normalize_protocol(self, protocol: Any) -> Optional[str]:
        """
        Normalize a protocol value.
        
        Args:
            protocol: Protocol value (string, int, etc.)
            
        Returns:
            Optional[str]: Normalized protocol or None
        """
        if protocol is None:
            return None
        
        # Convert to string
        protocol_str = str(protocol).strip().lower()
        
        # Direct mapping
        if protocol_str in self.PROTOCOL_MAPPINGS:
            return self.PROTOCOL_MAPPINGS[protocol_str]
        
        # Try to extract from longer string
        # e.g., "TCP/IP" -> "TCP"
        for key, value in self.PROTOCOL_MAPPINGS.items():
            if key.lower() in protocol_str:
                return value
        
        return None
    
    def infer_protocol_from_port(self, port: int) -> Optional[str]:
        """
        Infer protocol from port number.
        
        Args:
            port: Port number
            
        Returns:
            Optional[str]: Protocol name or None
        """
        if port in self.PORT_PROTOCOL:
            return self.PORT_PROTOCOL[port]
        return None