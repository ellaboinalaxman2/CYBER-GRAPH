"""Firewall log parser for various firewall formats."""

import json
import re
from typing import Optional, Dict, Any

from src.parsers.base import BaseParser
from src.models.raw_event import RawEvent
from src.core.exceptions import ParserError


class FirewallParser(BaseParser):
    """
    Parser for firewall logs.
    
    Supports:
    - JSON formatted logs
    - Common firewall text formats
    - Cisco ASA format (basic)
    - iptables format (basic)
    """
    
    def __init__(self):
        super().__init__(parser_name="firewall-parser")
    
    def parse(self, raw_event: RawEvent) -> Optional[Dict[str, Any]]:
        """
        Parse a firewall raw event into structured data.
        
        Args:
            raw_event: RawEvent from firewall collector
            
        Returns:
            Dict[str, Any]: Parsed firewall data
        """
        content = raw_event.raw_content
        
        if not content:
            self._update_stats(success=False)
            return None
        
        result = {
            "raw_source": "firewall",
            "original_timestamp": raw_event.original_timestamp,
            "raw_content": content,
            "source_host": raw_event.source_host,
        }
        
        # Try JSON first
        parsed = self._parse_json(content)
        if parsed:
            result.update(parsed)
            self._update_stats(success=True)
            return result
        
        # Try common firewall format
        parsed = self._parse_firewall_text(content)
        if parsed:
            result.update(parsed)
            self._update_stats(success=True)
            return result
        
        # Try Cisco ASA format
        parsed = self._parse_cisco_asa(content)
        if parsed:
            result.update(parsed)
            self._update_stats(success=True)
            return result
        
        # Try iptables format
        parsed = self._parse_iptables(content)
        if parsed:
            result.update(parsed)
            self._update_stats(success=True)
            return result
        
        self._update_stats(success=False)
        return None
    
    def _parse_json(self, content: str) -> Optional[Dict[str, Any]]:
        """Parse JSON formatted firewall log."""
        try:
            data = json.loads(content)
            return {
                "parsed_json": data,
                "format": "json",
                "timestamp": data.get("timestamp") or data.get("time"),
                "source_ip": data.get("src") or data.get("source_ip") or data.get("src_ip"),
                "source_port": data.get("sport") or data.get("source_port"),
                "destination_ip": data.get("dst") or data.get("destination_ip") or data.get("dst_ip"),
                "destination_port": data.get("dport") or data.get("destination_port"),
                "protocol": data.get("proto") or data.get("protocol"),
                "action": data.get("action"),
                "interface": data.get("interface"),
                "reason": data.get("reason"),
            }
        except json.JSONDecodeError:
            return None
    
    def _parse_firewall_text(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Parse common firewall text format.
        
        Example: SRC=192.168.1.10 DST=192.168.1.20 PROTO=TCP DPORT=22 ACTION=ALLOW
        """
        result = {}
        
        # Extract key=value pairs
        kv_pairs = re.findall(r'(\w+)=([^\s]+)', content)
        for key, value in kv_pairs:
            key_lower = key.lower()
            if key_lower in ["src", "source", "src_ip", "source_ip"]:
                result["source_ip"] = value
            elif key_lower in ["dst", "dest", "dst_ip", "destination_ip", "dest_ip"]:
                result["destination_ip"] = value
            elif key_lower in ["sport", "source_port"]:
                result["source_port"] = value
            elif key_lower in ["dport", "dest_port", "destination_port"]:
                result["destination_port"] = value
            elif key_lower in ["proto", "protocol"]:
                result["protocol"] = value
            elif key_lower in ["action"]:
                result["action"] = value
            elif key_lower in ["interface"]:
                result["interface"] = value
            else:
                result[key_lower] = value
        
        # Try to extract timestamp
        if not result.get("timestamp"):
            timestamp = self._extract_timestamp(content)
            if timestamp:
                result["timestamp"] = timestamp
        
        if result:
            result["format"] = "text_kv"
            return result
        
        return None
    
    def _parse_cisco_asa(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Parse Cisco ASA log format.
        
        Example: %ASA-6-302013: Built outbound TCP connection 12345 from 192.168.1.10/45122 to 192.168.1.20/22
        """
        # Cisco ASA pattern
        pattern = r'%ASA-(\d+)-(\d+):\s*(.*?)(?:\s+from\s+([^\s]+)(?::(\d+))?)?(?:\s+to\s+([^\s]+)(?::(\d+))?)?'
        
        match = re.search(pattern, content)
        if not match:
            return None
        
        severity, message_id, message, src, src_port, dst, dst_port = match.groups()
        
        result = {
            "format": "cisco_asa",
            "severity": severity,
            "message_id": message_id,
            "message": message.strip(),
            "source_ip": src.split('/')[0] if src else None,
            "source_port": src_port,
            "destination_ip": dst.split('/')[0] if dst else None,
            "destination_port": dst_port,
        }
        
        # Try to extract protocol
        protocol_match = re.search(r'(TCP|UDP|ICMP|GRE|ESP)', message, re.IGNORECASE)
        if protocol_match:
            result["protocol"] = protocol_match.group(1).upper()
        
        # Try to extract action
        if "Built" in message and "outbound" in message:
            result["action"] = "ALLOW"
        elif "Denied" in message or "denied" in message:
            result["action"] = "DENY"
        elif "Blocked" in message:
            result["action"] = "BLOCK"
        
        return result
    
    def _parse_iptables(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Parse iptables log format.
        
        Example: IN=eth0 OUT= MAC=00:11:22:33:44:55:66 SRC=192.168.1.10 DST=192.168.1.20 LEN=60 PROTO=TCP SPT=45122 DPT=22
        """
        result = {}
        
        # Extract key=value pairs
        kv_pairs = re.findall(r'(\w+)=([^\s]+)', content)
        for key, value in kv_pairs:
            key_lower = key.lower()
            if key_lower in ["src"]:
                result["source_ip"] = value
            elif key_lower in ["dst"]:
                result["destination_ip"] = value
            elif key_lower in ["spt", "sport"]:
                result["source_port"] = value
            elif key_lower in ["dpt", "dport"]:
                result["destination_port"] = value
            elif key_lower in ["proto"]:
                result["protocol"] = value
            elif key_lower in ["in", "out"]:
                result["interface"] = value
            elif key_lower in ["mac"]:
                result["mac"] = value
            else:
                result[key_lower] = value
        
        # Try to extract action from message
        if "Blocked" in content or "DROP" in content:
            result["action"] = "BLOCK"
        elif "ACCEPT" in content or "ALLOW" in content:
            result["action"] = "ALLOW"
        
        # Try to extract timestamp
        timestamp = self._extract_timestamp(content)
        if timestamp:
            result["timestamp"] = timestamp
        
        if result:
            result["format"] = "iptables"
            return result
        
        return None
    
    @staticmethod
    def supports(source_type: str) -> bool:
        """Check if parser supports firewall source type."""
        return source_type in ["firewall", "asa", "iptables", "pf"]