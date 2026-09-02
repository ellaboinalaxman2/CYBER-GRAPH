"""IP address normalizer."""

import re
from typing import Optional, Dict, Any, Tuple

from src.normalizers.base import BaseNormalizer
from src.core.exceptions import NormalizationError


class IPNormalizer(BaseNormalizer):
    """
    Normalizes IP addresses to a consistent format.
    
    Handles:
    - IPv4 addresses
    - IPv6 addresses (basic)
    - IP with ports
    - CIDR notation
    - Private IP detection
    """
    
    # IPv4 pattern
    IPV4_PATTERN = r'^(\d{1,3}\.){3}\d{1,3}$'
    
    # IPv6 pattern (simplified)
    IPV6_PATTERN = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
    
    # Private IP ranges (RFC 1918)
    PRIVATE_IPV4 = [
        (r'^10\.', '10.0.0.0/8'),
        (r'^172\.(1[6-9]|2[0-9]|3[0-1])\.', '172.16.0.0/12'),
        (r'^192\.168\.', '192.168.0.0/16'),
        (r'^127\.', '127.0.0.0/8'),
        (r'^169\.254\.', '169.254.0.0/16'),
    ]
    
    def __init__(self, normalize_ports: bool = True):
        """
        Initialize IP normalizer.
        
        Args:
            normalize_ports: Whether to extract ports from IP strings
        """
        super().__init__(normalizer_name="ip-normalizer")
        self.normalize_ports = normalize_ports
    
    def normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize IP addresses in the data.
        
        Args:
            data: Dictionary containing IP fields
            
        Returns:
            Dict[str, Any]: Data with normalized IPs
        """
        result = data.copy()
        
        # Find IP fields
        ip_keys = ["ip", "src_ip", "source_ip", "dst_ip", "dest_ip", "destination_ip"]
        
        for key in ip_keys:
            value = self._safe_get(data, key)
            if value:
                normalized = self._normalize_ip(value)
                if normalized:
                    result[key] = normalized
                    result[f"_{key}_normalized"] = True
                    self._update_stats(success=True, fields_count=1)
                else:
                    result[f"_{key}_normalization_error"] = f"Invalid IP: {value}"
                    self._update_stats(success=False)
        
        return result
    
    def _normalize_ip(self, value: Any) -> Optional[str]:
        """
        Normalize an IP address.
        
        Args:
            value: IP address value
            
        Returns:
            Optional[str]: Normalized IP or None
        """
        if value is None:
            return None
        
        # If already a string, clean it
        if isinstance(value, str):
            ip_str = value.strip()
            
            # Remove brackets (common in IPv6)
            ip_str = ip_str.strip('[]')
            
            # Extract IP from "IP:PORT" format
            if ':' in ip_str and not self._is_ipv6(ip_str):
                parts = ip_str.split(':')
                if len(parts) == 2:
                    ip_str = parts[0]
                    if self.normalize_ports:
                        # Store port separately
                        pass
        
        # Validate and return
        if self._is_valid_ipv4(ip_str):
            return ip_str
        
        if self._is_valid_ipv6(ip_str):
            return ip_str
        
        return None
    
    def _is_valid_ipv4(self, ip: str) -> bool:
        """Check if string is a valid IPv4 address."""
        if not re.match(self.IPV4_PATTERN, ip):
            return False
        
        parts = ip.split('.')
        return all(0 <= int(p) <= 255 for p in parts)
    
    def _is_valid_ipv6(self, ip: str) -> bool:
        """Check if string is a valid IPv6 address (basic)."""
        return bool(re.match(self.IPV6_PATTERN, ip))
    
    def _is_ipv6(self, ip: str) -> bool:
        """Check if string appears to be IPv6."""
        return ':' in ip and '.' not in ip
    
    def is_private_ip(self, ip: str) -> bool:
        """
        Check if IP is private (RFC 1918).
        
        Args:
            ip: IP address to check
            
        Returns:
            bool: True if private
        """
        for pattern, _ in self.PRIVATE_IPV4:
            if re.match(pattern, ip):
                return True
        return False
    
    def get_ip_type(self, ip: str) -> str:
        """
        Get the type of IP address.
        
        Args:
            ip: IP address
            
        Returns:
            str: "private", "public", "loopback", "link-local", or "unknown"
        """
        if not self._is_valid_ipv4(ip):
            return "unknown"
        
        if ip.startswith('127.'):
            return "loopback"
        if ip.startswith('169.254.'):
            return "link-local"
        if self.is_private_ip(ip):
            return "private"
        return "public"