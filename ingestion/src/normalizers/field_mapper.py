"""Field name mapper for standardizing field names."""

import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path

from src.normalizers.base import BaseNormalizer
from src.core.config import settings


class FieldMapper(BaseNormalizer):
    """
    Maps field names from various sources to canonical names.
    
    Supports:
    - Field name mapping
    - Field renaming
    - Field removal (for sensitive data)
    - Field aliasing
    """
    
    DEFAULT_MAPPINGS = {
        # Source IP
        "src": "source_ip",
        "src_ip": "source_ip",
        "source": "source_ip",
        "source_address": "source_ip",
        "source_addr": "source_ip",
        "saddr": "source_ip",
        
        # Destination IP
        "dst": "destination_ip",
        "dst_ip": "destination_ip",
        "dest": "destination_ip",
        "destination": "destination_ip",
        "dest_address": "destination_ip",
        "dest_addr": "destination_ip",
        "daddr": "destination_ip",
        
        # Source Port
        "sport": "source_port",
        "src_port": "source_port",
        "source_port": "source_port",
        
        # Destination Port
        "dport": "destination_port",
        "dst_port": "destination_port",
        "dest_port": "destination_port",
        "destination_port": "destination_port",
        
        # Protocol
        "proto": "protocol",
        "protocol": "protocol",
        "transport": "protocol",
        
        # Action
        "action": "action",
        "verdict": "action",
        "result": "action",
        "status": "action",
        
        # Hostname
        "host": "hostname",
        "hostname": "hostname",
        "machine": "hostname",
        "system": "hostname",
        
        # User
        "user": "user",
        "username": "user",
        "account": "user",
        "account_name": "user",
        
        # Timestamp
        "time": "timestamp",
        "ts": "timestamp",
        "event_time": "timestamp",
        "log_time": "timestamp",
        "date": "timestamp",
        "datetime": "timestamp",
        
        # Message
        "msg": "message",
        "log": "message",
        "text": "message",
        "description": "message",
        
        # Event Type
        "type": "event_type",
        "event_type": "event_type",
        "category": "event_type",
        "log_type": "event_type",
        
        # Event ID
        "id": "event_id",
        "event_id": "event_id",
        "eventid": "event_id",
        "log_id": "event_id",
        
        # Severity
        "level": "severity",
        "severity": "severity",
        "priority": "severity",
    }
    
    def __init__(
        self,
        mappings: Optional[Dict[str, str]] = None,
        remove_original: bool = True,
        keep_unknown: bool = True,
    ):
        """
        Initialize field mapper.
        
        Args:
            mappings: Custom field mappings
            remove_original: Remove original fields after mapping
            keep_unknown: Keep fields that aren't mapped
        """
        super().__init__(normalizer_name="field-mapper")
        self.mappings = mappings or self.DEFAULT_MAPPINGS.copy()
        self.remove_original = remove_original
        self.keep_unknown = keep_unknown
        self._load_mappings_from_file()
    
    def _load_mappings_from_file(self) -> None:
        """Load custom mappings from file if exists."""
        mapping_file = Path("data/mappings/field_mappings.json")
        if mapping_file.exists():
            try:
                with open(mapping_file, 'r') as f:
                    custom_mappings = json.load(f)
                    self.mappings.update(custom_mappings)
                    self.logger.info(f"Loaded {len(custom_mappings)} custom field mappings")
            except Exception as e:
                self.logger.warning(f"Failed to load field mappings: {e}")
    
    def normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map field names to canonical names.
        
        Args:
            data: Dictionary with fields to map
            
        Returns:
            Dict[str, Any]: Data with canonical field names
        """
        result = {}
        mapped_fields = []
        
        for key, value in data.items():
            # Skip internal fields
            if key.startswith('_'):
                result[key] = value
                continue
            
            # Map to canonical name
            canonical = self.mappings.get(key)
            
            if canonical:
                # Check if canonical key already exists (prefer mapped values)
                if canonical in result:
                    # If value is None or empty, skip
                    if value is None or value == "":
                        continue
                    # If both exist, keep the mapped one if it's more complete
                    existing = result.get(canonical)
                    if existing is None or existing == "":
                        result[canonical] = value
                    # Otherwise keep the existing value
                else:
                    result[canonical] = value
                    mapped_fields.append(key)
                
                if self.remove_original and key != canonical:
                    # Don't add original key
                    pass
                elif self.keep_unknown:
                    result[key] = value
            else:
                # Keep unknown fields
                if self.keep_unknown:
                    result[key] = value
        
        # Track what was mapped
        result["_mapped_fields"] = mapped_fields
        result["_field_mapping_count"] = len(mapped_fields)
        
        self._update_stats(success=True, fields_count=len(mapped_fields))
        
        return result
    
    def add_mapping(self, source_field: str, target_field: str) -> None:
        """
        Add a field mapping.
        
        Args:
            source_field: Original field name
            target_field: Canonical field name
        """
        self.mappings[source_field] = target_field
    
    def remove_mapping(self, source_field: str) -> None:
        """
        Remove a field mapping.
        
        Args:
            source_field: Field to remove mapping for
        """
        if source_field in self.mappings:
            del self.mappings[source_field]