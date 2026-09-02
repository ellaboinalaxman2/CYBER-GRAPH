"""Syslog parser for RFC 3164 and RFC 5424 formats."""

import re
from typing import Optional, Dict, Any

from src.parsers.base import BaseParser
from src.models.raw_event import RawEvent
from src.core.exceptions import ParserError


class SyslogParser(BaseParser):
    """
    Parser for syslog messages.
    
    Supports:
    - RFC 3164 (BSD syslog)
    - RFC 5424 (modern syslog)
    - Common syslog variations
    """
    
    def __init__(self):
        super().__init__(parser_name="syslog-parser")
    
    def parse(self, raw_event: RawEvent) -> Optional[Dict[str, Any]]:
        """
        Parse a syslog raw event into structured data.
        
        Args:
            raw_event: RawEvent from syslog collector
            
        Returns:
            Dict[str, Any]: Parsed syslog data
        """
        content = raw_event.raw_content
        
        if not content:
            self._update_stats(success=False)
            return None
        
        result = {
            "raw_source": "syslog",
            "original_timestamp": raw_event.original_timestamp,
            "raw_content": content,
            "source_host": raw_event.source_host,
        }
        
        # Try RFC 5424 format first
        parsed = self._parse_rfc5424(content)
        if parsed:
            result.update(parsed)
            self._update_stats(success=True)
            return result
        
        # Try RFC 3164 format
        parsed = self._parse_rfc3164(content)
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
    
    def _parse_rfc5424(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Parse RFC 5424 syslog format.
        
        Format: <pri>version timestamp hostname app-name procid msgid structured-data message
        
        Example: <34>1 2026-08-29T10:30:15Z firewall sshd 1234 ID47 [origin host="firewall-01"] Failed password for admin
        """
        # RFC 5424 pattern
        pattern = r'<(\d+)>(\d+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+(?:\[([^\]]*)\])?\s*(.*)$'
        
        match = re.match(pattern, content)
        if not match:
            return None
        
        pri, version, timestamp, hostname, app_name, procid, msgid, structured_data, message = match.groups()
        
        return {
            "facility": int(pri) // 8,
            "severity": int(pri) % 8,
            "version": version,
            "timestamp": timestamp,
            "hostname": hostname,
            "application": app_name,
            "process_id": procid,
            "message_id": msgid,
            "structured_data": structured_data,
            "message": message.strip(),
            "format": "rfc5424",
        }
    
    def _parse_rfc3164(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Parse RFC 3164 syslog format.
        
        Format: <pri>timestamp hostname tag[pid]: message
        
        Example: <34>Aug 29 10:30:15 firewall sshd[1234]: Failed password for admin
        """
        # RFC 3164 pattern
        pattern = r'<(\d+)>([A-Za-z]{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+([^\s]+)\s+([^\s\[\]]+)(?:\[(\d+)\])?:\s*(.*)$'
        
        match = re.match(pattern, content)
        if not match:
            return None
        
        pri, timestamp, hostname, tag, pid, message = match.groups()
        
        return {
            "facility": int(pri) // 8,
            "severity": int(pri) % 8,
            "timestamp": timestamp,
            "hostname": hostname,
            "tag": tag,
            "process_id": pid,
            "message": message.strip(),
            "format": "rfc3164",
        }
    
    def _parse_fallback(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Fallback parsing for syslog-like messages.
        
        Tries to extract common fields using regex.
        """
        result = {}
        
        # Try to extract timestamp
        timestamp = self._extract_timestamp(content)
        if timestamp:
            result["timestamp"] = timestamp
        
        # Try to extract hostname
        hostname_match = re.search(r'^([^\s:]+)\s+', content)
        if hostname_match:
            result["hostname"] = hostname_match.group(1)
        
        # Try to extract IP
        ip = self._extract_ip(content)
        if ip:
            result["source_ip"] = ip
        
        # Try to extract process/tag
        tag_match = re.search(r'([^\s\[\]]+)\[(\d+)\]', content)
        if tag_match:
            result["tag"] = tag_match.group(1)
            result["process_id"] = tag_match.group(2)
        
        # Look for key=value pairs
        kv_pairs = re.findall(r'(\w+)=([^\s]+)', content)
        for key, value in kv_pairs:
            result[key.lower()] = value
        
        # Extract message (everything after the last colon)
        message_parts = content.split(':', 1)
        if len(message_parts) > 1:
            result["message"] = message_parts[-1].strip()
        else:
            result["message"] = content
        
        if result:
            result["format"] = "fallback"
            return result
        
        return None
    
    @staticmethod
    def supports(source_type: str) -> bool:
        """Check if parser supports syslog source type."""
        return source_type in ["syslog", "syslog-ng", "rsyslog"]