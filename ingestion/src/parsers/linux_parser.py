"""Linux system log parser."""

import re
from typing import Optional, Dict, Any

from src.parsers.base import BaseParser
from src.models.raw_event import RawEvent
from src.core.exceptions import ParserError


class LinuxParser(BaseParser):
    """
    Parser for Linux system logs.
    
    Supports:
    - /var/log/auth.log (authentication)
    - /var/log/syslog (system)
    - /var/log/secure (security)
    - Common Linux log formats
    """
    
    def __init__(self):
        super().__init__(parser_name="linux-parser")
    
    def parse(self, raw_event: RawEvent) -> Optional[Dict[str, Any]]:
        """
        Parse a Linux log raw event into structured data.
        
        Args:
            raw_event: RawEvent from Linux collector
            
        Returns:
            Dict[str, Any]: Parsed Linux log data
        """
        content = raw_event.raw_content
        
        if not content:
            self._update_stats(success=False)
            return None
        
        result = {
            "raw_source": "linux",
            "original_timestamp": raw_event.original_timestamp,
            "raw_content": content,
            "source_host": raw_event.source_host,
        }
        
        # Try authentication log format
        parsed = self._parse_auth_log(content)
        if parsed:
            result.update(parsed)
            self._update_stats(success=True)
            return result
        
        # Try system log format
        parsed = self._parse_syslog(content)
        if parsed:
            result.update(parsed)
            self._update_stats(success=True)
            return result
        
        # Try kernel log format
        parsed = self._parse_kernel_log(content)
        if parsed:
            result.update(parsed)
            self._update_stats(success=True)
            return result
        
        # Try fallback parsing
        parsed = self._parse_fallback(content)
        if parsed:
            result.update(parsed)
            self._update_stats(success=True)
            return result
        
        self._update_stats(success=False)
        return None
    
    def _parse_auth_log(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Parse authentication log format.
        
        Example: Aug 29 10:30:15 server01 sshd[1234]: Failed password for invalid user admin from 192.168.1.50
        """
        pattern = r'^([A-Za-z]{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+([^\s]+)\s+([^\s\[\]]+)(?:\[(\d+)\])?:\s*(.*)$'
        
        match = re.match(pattern, content)
        if not match:
            return None
        
        timestamp, hostname, tag, pid, message = match.groups()
        
        result = {
            "format": "auth_log",
            "timestamp": timestamp,
            "hostname": hostname,
            "tag": tag,
            "process_id": pid,
            "message": message.strip(),
        }
        
        # Extract authentication events
        if "Failed password" in message:
            result["event_type"] = "LOGIN_FAILURE"
            # Extract user
            user_match = re.search(r'for (invalid user )?([^\s]+)', message)
            if user_match:
                result["user"] = user_match.group(2)
        elif "Accepted password" in message:
            result["event_type"] = "LOGIN_SUCCESS"
            user_match = re.search(r'for ([^\s]+)', message)
            if user_match:
                result["user"] = user_match.group(1)
        elif "sudo" in tag:
            result["event_type"] = "PRIVILEGE_ESCALATION"
            user_match = re.search(r'([^\s]+)\s*:', message)
            if user_match:
                result["user"] = user_match.group(1)
        
        # Extract IP
        ip = self._extract_ip(message)
        if ip:
            result["source_ip"] = ip
        
        return result
    
    def _parse_syslog(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Parse system log format.
        
        Example: Aug 29 10:30:15 server01 kernel: [12345.678] Firewall: *TCP_IN Blocked*
        """
        pattern = r'^([A-Za-z]{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+([^\s]+)\s+([^\s:]+):\s*(.*)$'
        
        match = re.match(pattern, content)
        if not match:
            return None
        
        timestamp, hostname, tag, message = match.groups()
        
        result = {
            "format": "syslog",
            "timestamp": timestamp,
            "hostname": hostname,
            "tag": tag,
            "message": message.strip(),
        }
        
        # Extract IP
        ip = self._extract_ip(message)
        if ip:
            result["source_ip"] = ip
        
        # Extract key=value pairs
        kv_pairs = re.findall(r'(\w+)=([^\s]+)', message)
        for key, value in kv_pairs:
            result[key.lower()] = value
        
        return result
    
    def _parse_kernel_log(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Parse kernel log format.
        
        Example: [12345.678] Firewall: *TCP_IN Blocked* IN=eth0 SRC=192.168.1.10 DST=192.168.1.20
        """
        pattern = r'^\[([0-9.]+)\]\s+([^:]+):\s*(.*)$'
        
        match = re.match(pattern, content)
        if not match:
            return None
        
        timestamp, tag, message = match.groups()
        
        result = {
            "format": "kernel_log",
            "timestamp": timestamp,
            "tag": tag,
            "message": message.strip(),
        }
        
        # Extract key=value pairs
        kv_pairs = re.findall(r'(\w+)=([^\s]+)', message)
        for key, value in kv_pairs:
            key_lower = key.lower()
            if key_lower in ["src"]:
                result["source_ip"] = value
            elif key_lower in ["dst"]:
                result["destination_ip"] = value
            elif key_lower in ["spt"]:
                result["source_port"] = value
            elif key_lower in ["dpt"]:
                result["destination_port"] = value
            elif key_lower in ["proto"]:
                result["protocol"] = value
            else:
                result[key_lower] = value
        
        # Extract action
        if "Blocked" in message or "DROP" in message:
            result["action"] = "BLOCK"
        elif "ACCEPT" in message:
            result["action"] = "ALLOW"
        
        return result
    
    def _parse_fallback(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Fallback parsing for Linux logs.
        """
        result = {}
        
        # Try to extract timestamp
        timestamp = self._extract_timestamp(content)
        if timestamp:
            result["timestamp"] = timestamp
        
        # Try to extract IP
        ip = self._extract_ip(content)
        if ip:
            result["source_ip"] = ip
        
        # Try to extract hostname
        hostname_match = re.search(r'^([^\s]+)\s+', content)
        if hostname_match:
            result["hostname"] = hostname_match.group(1)
        
        # Look for key=value pairs
        kv_pairs = re.findall(r'(\w+)=([^\s]+)', content)
        for key, value in kv_pairs:
            result[key.lower()] = value
        
        if result:
            result["format"] = "fallback"
            result["message"] = content
            return result
        
        return None
    
    @staticmethod
    def supports(source_type: str) -> bool:
        """Check if parser supports Linux source type."""
        return source_type in ["linux", "syslog", "auth", "secure", "kern"]