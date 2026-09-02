"""Event type mapper for standardizing event types."""

import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path

from src.normalizers.base import BaseNormalizer
from src.models.common import EventType


class EventTypeMapper(BaseNormalizer):
    """
    Maps various event type names to canonical event types.
    
    Supports:
    - Authentication events
    - Network events
    - System events
    - Security events
    - Custom mappings
    """
    
    DEFAULT_MAPPINGS = {
        # Authentication
        "login": "LOGIN_SUCCESS",
        "login_success": "LOGIN_SUCCESS",
        "logon": "LOGIN_SUCCESS",
        "authenticated": "LOGIN_SUCCESS",
        "login_failure": "LOGIN_FAILURE",
        "login_failed": "LOGIN_FAILURE",
        "failed_login": "LOGIN_FAILURE",
        "failed_logon": "LOGIN_FAILURE",
        "authentication_failed": "LOGIN_FAILURE",
        "logout": "LOGOUT",
        "logoff": "LOGOUT",
        "log_out": "LOGOUT",
        
        # Network
        "network_connection": "NETWORK_CONNECTION",
        "connection": "NETWORK_CONNECTION",
        "connect": "NETWORK_CONNECTION",
        "network_disconnect": "NETWORK_DISCONNECTION",
        "disconnect": "NETWORK_DISCONNECTION",
        
        # Firewall
        "firewall_allow": "FIREWALL_ALLOW",
        "allow": "FIREWALL_ALLOW",
        "firewall_deny": "FIREWALL_DENY",
        "deny": "FIREWALL_DENY",
        "block": "FIREWALL_BLOCK",
        "firewall_block": "FIREWALL_BLOCK",
        "drop": "FIREWALL_DROP",
        
        # Process
        "process_start": "PROCESS_START",
        "process_created": "PROCESS_START",
        "process_end": "PROCESS_END",
        "process_terminated": "PROCESS_END",
        
        # File
        "file_access": "FILE_ACCESS",
        "file_read": "FILE_ACCESS",
        "file_modified": "FILE_MODIFIED",
        "file_update": "FILE_MODIFIED",
        "file_changed": "FILE_MODIFIED",
        "file_deleted": "FILE_DELETED",
        "file_delete": "FILE_DELETED",
        "file_created": "FILE_CREATED",
        "file_create": "FILE_CREATED",
        
        # User management
        "user_created": "USER_CREATED",
        "user_added": "USER_CREATED",
        "user_deleted": "USER_DELETED",
        "user_removed": "USER_DELETED",
        "user_modified": "USER_MODIFIED",
        "user_changed": "USER_MODIFIED",
        
        # System
        "system_event": "SYSTEM_EVENT",
        "system": "SYSTEM_EVENT",
        "alert": "ALERT",
        "security_alert": "ALERT",
        "audit": "AUDIT_EVENT",
        "audit_event": "AUDIT_EVENT",
    }
    
    # Windows Event ID mappings (extended)
    WINDOWS_EVENT_IDS = {
        4624: "LOGIN_SUCCESS",
        4625: "LOGIN_FAILURE",
        4634: "LOGOUT",
        4647: "LOGOUT",
        4672: "LOGIN_SUCCESS",  # Special privileges assigned
        4720: "USER_CREATED",
        4722: "USER_MODIFIED",
        4726: "USER_DELETED",
        4728: "GROUP_CHANGE",
        4729: "GROUP_CHANGE",
        4730: "GROUP_CHANGE",
        4732: "GROUP_CHANGE",
        4733: "GROUP_CHANGE",
        4734: "GROUP_CHANGE",
        4740: "ACCOUNT_LOCKOUT",
        4768: "AUTHENTICATION",
        4769: "AUTHENTICATION",
        4776: "AUTHENTICATION",
        4798: "USER_MODIFIED",
        4799: "USER_MODIFIED",
        5140: "FILE_ACCESS",
        5142: "FILE_MODIFIED",
        5144: "FILE_DELETED",
        5145: "FILE_ACCESS",
        5152: "FIREWALL_DENY",
        5154: "FIREWALL_ALLOW",
        5156: "NETWORK_CONNECTION",
        5158: "NETWORK_CONNECTION",
        5159: "NETWORK_DISCONNECTION",
    }
    
    def __init__(self):
        """Initialize event type mapper."""
        super().__init__(normalizer_name="event-type-mapper")
        self.mappings = self.DEFAULT_MAPPINGS.copy()
        self.windows_mappings = self.WINDOWS_EVENT_IDS.copy()
        self._load_mappings_from_file()
    
    def _load_mappings_from_file(self) -> None:
        """Load custom mappings from file if exists."""
        mapping_file = Path("data/mappings/event_type_mappings.json")
        if mapping_file.exists():
            try:
                with open(mapping_file, 'r') as f:
                    custom_mappings = json.load(f)
                    self.mappings.update(custom_mappings)
                    self.logger.info(f"Loaded {len(custom_mappings)} custom event type mappings")
            except Exception as e:
                self.logger.warning(f"Failed to load event type mappings: {e}")
    
    def normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize event type in the data.
        
        Args:
            data: Dictionary containing event type data
            
        Returns:
            Dict[str, Any]: Data with normalized event type
        """
        result = data.copy()
        
        # Find event type field
        event_type = None
        
        # Check for Windows event ID first
        event_id = self._safe_get(data, "event_id")
        if event_id and isinstance(event_id, int):
            if event_id in self.windows_mappings:
                event_type = self.windows_mappings[event_id]
        
        # Check for event type field
        if not event_type:
            type_keys = ["event_type", "type", "category", "log_type", "event"]
            for key in type_keys:
                value = self._safe_get(data, key)
                if value:
                    event_type = value
                    break
        
        if event_type:
            normalized = self._normalize_event_type(event_type)
            if normalized:
                result["event_type"] = normalized
                result["_event_type_normalized"] = True
                self._update_stats(success=True, fields_count=1)
            else:
                result["event_type"] = "UNKNOWN"
                result["_event_type_normalization_error"] = f"Unknown event type: {event_type}"
                self._update_stats(success=False)
        
        return result
    
    def _normalize_event_type(self, event_type: Any) -> Optional[str]:
        """
        Normalize an event type value.
        
        Args:
            event_type: Event type value
            
        Returns:
            Optional[str]: Normalized event type or None
        """
        if event_type is None:
            return None
        
        # Convert to string
        type_str = str(event_type).strip()
        type_lower = type_str.lower().replace(' ', '_')
        
        # Direct mapping
        if type_str in self.mappings:
            return self.mappings[type_str]
        
        if type_lower in self.mappings:
            return self.mappings[type_lower]
        
        # Try partial match
        for key, value in self.mappings.items():
            if key in type_lower or type_lower in key:
                return value
        
        return None
    
    def add_mapping(self, source_type: str, target_type: EventType) -> None:
        """
        Add an event type mapping.
        
        Args:
            source_type: Original event type
            target_type: Canonical event type
        """
        self.mappings[source_type] = target_type
    
    def add_windows_mapping(self, event_id: int, event_type: EventType) -> None:
        """
        Add a Windows Event ID mapping.
        
        Args:
            event_id: Windows Event ID
            event_type: Canonical event type
        """
        self.windows_mappings[event_id] = event_type