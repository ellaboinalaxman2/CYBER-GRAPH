"""Windows event log parser."""

import json
import re
from typing import Optional, Dict, Any
from datetime import datetime

from src.parsers.base import BaseParser
from src.models.raw_event import RawEvent
from src.core.exceptions import ParserError


class WindowsParser(BaseParser):
    """
    Parser for Windows Event Logs.
    
    Supports:
    - JSON formatted Windows events
    - Windows Event Log text format
    - Common Windows event patterns
    """
    
    # Windows Event IDs and their meanings
    EVENT_IDS = {
        4624: "LOGIN_SUCCESS",
        4625: "LOGIN_FAILURE",
        4634: "LOGOUT",
        4647: "LOGOUT",
        4672: "LOGIN_SUCCESS",
        4720: "USER_CREATED",
        4726: "USER_DELETED",
        4732: "GROUP_CHANGE",
        4733: "GROUP_CHANGE",
        4740: "ACCOUNT_LOCKOUT",
        4768: "AUTHENTICATION",
        4769: "AUTHENTICATION",
        4776: "AUTHENTICATION",
    }
    
    def __init__(self):
        super().__init__(parser_name="windows-parser")
    
    def parse(self, raw_event: RawEvent) -> Optional[Dict[str, Any]]:
        """
        Parse a Windows event raw event into structured data.
        
        Args:
            raw_event: RawEvent from Windows collector
            
        Returns:
            Dict[str, Any]: Parsed Windows event data
        """
        content = raw_event.raw_content
        
        if not content:
            self._update_stats(success=False)
            return None
        
        result = {
            "raw_source": "windows",
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
        
        # Try Windows event log format
        parsed = self._parse_windows_text(content)
        if parsed:
            result.update(parsed)
            self._update_stats(success=True)
            return result
        
        self._update_stats(success=False)
        return None
    
    def _parse_json(self, content: str) -> Optional[Dict[str, Any]]:
        """Parse JSON formatted Windows event."""
        try:
            data = json.loads(content)
            
            result = {
                "format": "json",
                "parsed_json": data,
                "timestamp": data.get("timestamp"),
                "event_id": data.get("event_id") or data.get("eventId") or data.get("EventID"),
                "log_name": data.get("log_name") or data.get("logName") or data.get("LogName"),
                "message": data.get("message"),
                "account_name": data.get("account_name") or data.get("accountName") or data.get("AccountName"),
                "workstation_name": data.get("workstation_name") or data.get("workstationName") or data.get("WorkstationName"),
                "source_ip": data.get("source_ip") or data.get("sourceIp") or data.get("SourceIp"),
            }
            
            # Map event ID to event type
            if result.get("event_id"):
                event_type = WindowsParser.EVENT_IDS.get(int(result["event_id"]))
                if event_type:
                    result["event_type"] = event_type
            
            return result
            
        except json.JSONDecodeError:
            return None
    
    def _parse_windows_text(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Parse Windows event log text format.
        
        Example: Log Name: Security, Source: Microsoft-Windows-Security-Auditing, Event ID: 4624
        """
        result = {}
        
        # Extract key: value pairs
        kv_pairs = re.findall(r'([^:]+):\s*([^,\n]+)', content)
        for key, value in kv_pairs:
            key_clean = key.strip().lower().replace(' ', '_')
            value_clean = value.strip()
            
            if key_clean in ["log_name", "log name"]:
                result["log_name"] = value_clean
            elif key_clean in ["event_id", "event id"]:
                result["event_id"] = value_clean
            elif key_clean in ["source"]:
                result["source"] = value_clean
            elif key_clean in ["account_name", "account name"]:
                result["account_name"] = value_clean
            elif key_clean in ["workstation_name", "workstation name"]:
                result["workstation_name"] = value_clean
            elif key_clean in ["source_ip", "source ip", "ip address"]:
                result["source_ip"] = value_clean
            elif key_clean in ["message"]:
                result["message"] = value_clean
        
        # Extract timestamp
        timestamp = self._extract_timestamp(content)
        if timestamp:
            result["timestamp"] = timestamp
        
        # Extract IP from message
        if not result.get("source_ip"):
            ip = self._extract_ip(content)
            if ip:
                result["source_ip"] = ip
        
        # Map event ID to event type
        if result.get("event_id"):
            try:
                event_id = int(result["event_id"])
                event_type = WindowsParser.EVENT_IDS.get(event_id)
                if event_type:
                    result["event_type"] = event_type
            except ValueError:
                pass
        
        if result:
            result["format"] = "text"
            return result
        
        return None
    
    @staticmethod
    def supports(source_type: str) -> bool:
        """Check if parser supports Windows source type."""
        return source_type in ["windows", "winlog", "eventlog"]