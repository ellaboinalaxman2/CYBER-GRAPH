"""Generic JSON parser for structured logs."""

import json
from typing import Optional, Dict, Any

from src.parsers.base import BaseParser
from src.models.raw_event import RawEvent
from src.core.exceptions import ParserError


class JSONParser(BaseParser):
    """
    Generic JSON parser.
    
    Parses JSON formatted logs and extracts common fields.
    Can be configured with field mappings.
    """
    
    def __init__(self, field_mappings: Optional[Dict[str, str]] = None):
        """
        Initialize JSON parser.
        
        Args:
            field_mappings: Mapping of source field names to standard field names
        """
        super().__init__(parser_name="json-parser")
        self.field_mappings = field_mappings or self._default_mappings()
    
    def _default_mappings(self) -> Dict[str, str]:
        """Default field mappings."""
        return {
            "timestamp": "timestamp",
            "time": "timestamp",
            "ts": "timestamp",
            "event_time": "timestamp",
            "log_time": "timestamp",
            "source_ip": "source_ip",
            "src_ip": "source_ip",
            "src": "source_ip",
            "source": "source_ip",
            "source_address": "source_ip",
            "destination_ip": "destination_ip",
            "dst_ip": "destination_ip",
            "dst": "destination_ip",
            "dest": "destination_ip",
            "destination": "destination_ip",
            "dest_address": "destination_ip",
            "source_port": "source_port",
            "src_port": "source_port",
            "sport": "source_port",
            "destination_port": "destination_port",
            "dst_port": "destination_port",
            "dport": "destination_port",
            "protocol": "protocol",
            "proto": "protocol",
            "action": "action",
            "severity": "severity",
            "level": "severity",
            "message": "message",
            "msg": "message",
            "log": "message",
            "hostname": "hostname",
            "host": "hostname",
            "user": "user",
            "username": "user",
            "event_type": "event_type",
            "type": "event_type",
            "event_id": "event_id",
            "id": "event_id",
        }
    
    def parse(self, raw_event: RawEvent) -> Optional[Dict[str, Any]]:
        """
        Parse a JSON raw event into structured data.
        
        Args:
            raw_event: RawEvent with JSON content
            
        Returns:
            Dict[str, Any]: Parsed JSON data with normalized fields
        """
        content = raw_event.raw_content
        
        if not content:
            self._update_stats(success=False)
            return None
        
        # Try to parse as JSON
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from text
            json_match = re.search(r'\{.*\}', content)
            if json_match:
                try:
                    data = json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    self._update_stats(success=False)
                    return None
            else:
                self._update_stats(success=False)
                return None
        
        result = {
            "format": "json",
            "raw_source": raw_event.raw_source,
            "source_host": raw_event.source_host,
            "original_timestamp": raw_event.original_timestamp,
            "parsed_json": data,
        }
        
        # Map fields using the configured mappings
        for source_field, target_field in self.field_mappings.items():
            if source_field in data:
                value = data[source_field]
                result[target_field] = value
        
        # Keep any fields that don't have mappings
        for key, value in data.items():
            if key not in self.field_mappings and key not in result:
                result[f"raw_{key}"] = value
        
        self._update_stats(success=True)
        return result
    
    def add_mapping(self, source_field: str, target_field: str) -> None:
        """
        Add a field mapping.
        
        Args:
            source_field: Field name in the JSON
            target_field: Standard field name to map to
        """
        self.field_mappings[source_field] = target_field
    
    @staticmethod
    def supports(source_type: str) -> bool:
        """Check if parser supports JSON source type."""
        return source_type in ["json", "application", "api", "webhook"]