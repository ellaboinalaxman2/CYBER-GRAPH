"""Schema validator for checking event structure."""

import json
import os
from typing import Dict, Any, Optional, List, Set, get_args
from pathlib import Path
from datetime import datetime

from src.validators.base import BaseValidator
from src.validators.validation_errors import (
    ValidationResult,
    ValidationError,
    ValidationErrorType,
    ValidationSeverity,
)
from src.models.common import EventType, Protocol, Action, Severity


class SchemaValidator(BaseValidator):
    """
    Validates that events conform to the required schema.
    
    Checks:
    - Required fields are present
    - Field types are correct
    - Field formats are valid
    - No extra fields (optional)
    """
    
    # Core schema definition
    REQUIRED_FIELDS = [
        "event_id",
        "timestamp",
        "event_type",
        "raw_source",
        "source",
        "destination",
    ]
    
    OPTIONAL_FIELDS = [
        "protocol",
        "action",
        "severity",
        "message",
        "tags",
        "raw_message",
        "normalized_fields",
    ]
    
    FIELD_TYPES = {
        "event_id": str,
        "timestamp": str,  # Will be datetime after normalization
        "event_type": str,
        "raw_source": str,
        "source": dict,
        "destination": dict,
        "protocol": str,
        "action": str,
        "severity": str,
        "message": str,
        "tags": list,
        "raw_message": str,
        "normalized_fields": list,
    }
    
    # Get valid values from Literal types
    VALID_EVENT_TYPES = list(get_args(EventType))
    VALID_PROTOCOLS = list(get_args(Protocol))
    VALID_ACTIONS = list(get_args(Action))
    VALID_SEVERITIES = list(get_args(Severity))
    
    SOURCE_FIELDS = ["ip", "hostname", "port", "user", "mac", "device_type"]
    DESTINATION_FIELDS = ["ip", "hostname", "port", "user", "device_type"]
    
    def __init__(
        self,
        strict_mode: bool = False,
        allow_extra_fields: bool = True,
    ):
        """
        Initialize schema validator.
        
        Args:
            strict_mode: Whether to fail on warnings
            allow_extra_fields: Whether to allow fields not in schema
        """
        super().__init__(validator_name="schema-validator", strict_mode=strict_mode)
        self.allow_extra_fields = allow_extra_fields
        self._load_custom_schema()
    
    def _load_custom_schema(self) -> None:
        """Load custom schema rules from file."""
        schema_file = Path("data/validation_rules/schema_rules.json")
        if schema_file.exists():
            try:
                with open(schema_file, 'r') as f:
                    custom_rules = json.load(f)
                    if "required_fields" in custom_rules:
                        self.REQUIRED_FIELDS = custom_rules["required_fields"]
                    if "optional_fields" in custom_rules:
                        self.OPTIONAL_FIELDS = custom_rules["optional_fields"]
                    if "field_types" in custom_rules:
                        self.FIELD_TYPES.update(custom_rules["field_types"])
                    self.logger.info(f"Loaded custom schema rules from {schema_file}")
            except Exception as e:
                self.logger.warning(f"Failed to load schema rules: {e}")
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """
        Validate the event against the schema.
        
        Args:
            data: Event data to validate
            
        Returns:
            ValidationResult: Result of validation
        """
        result = ValidationResult()
        
        # Check for required fields
        self._validate_required_fields(data, result)
        
        # Check field types
        self._validate_field_types(data, result)
        
        # Check field values (enums)
        self._validate_enum_values(data, result)
        
        # Check source and destination
        self._validate_source_destination(data, result)
        
        # Check for extra fields
        if not self.allow_extra_fields:
            self._validate_extra_fields(data, result)
        
        self._update_stats(result)
        return result
    
    def _validate_required_fields(self, data: Dict[str, Any], result: ValidationResult) -> None:
        """Validate that all required fields are present."""
        for field in self.REQUIRED_FIELDS:
            if field not in data or data[field] is None or data[field] == "":
                error = self._create_error(
                    field=field,
                    message=f"Required field '{field}' is missing or empty",
                    value=data.get(field),
                    error_type=ValidationErrorType.MISSING_REQUIRED_FIELD,
                    severity=ValidationSeverity.ERROR,
                )
                result.add_error(error)
    
    def _validate_field_types(self, data: Dict[str, Any], result: ValidationResult) -> None:
        """Validate that fields have correct types."""
        for field, expected_type in self.FIELD_TYPES.items():
            if field in data and data[field] is not None:
                value = data[field]
                
                # Special case for timestamp (can be string or datetime)
                if field == "timestamp" and expected_type == str:
                    if not isinstance(value, (str, datetime)):
                        error = self._create_error(
                            field=field,
                            message=f"Field '{field}' should be a timestamp (string or datetime)",
                            value=value,
                            error_type=ValidationErrorType.INVALID_FIELD_TYPE,
                            severity=ValidationSeverity.ERROR,
                        )
                        result.add_error(error)
                    continue
                
                # Check type
                if not isinstance(value, expected_type):
                    error = self._create_error(
                        field=field,
                        message=f"Field '{field}' should be of type {expected_type.__name__}, got {type(value).__name__}",
                        value=value,
                        error_type=ValidationErrorType.INVALID_FIELD_TYPE,
                        severity=ValidationSeverity.ERROR,
                    )
                    result.add_error(error)
    
    def _validate_enum_values(self, data: Dict[str, Any], result: ValidationResult) -> None:
        """Validate that enum fields have valid values."""
        # Validate event_type
        if "event_type" in data and data["event_type"]:
            value = data["event_type"]
            if value not in self.VALID_EVENT_TYPES:
                error = self._create_error(
                    field="event_type",
                    message=f"Invalid event_type '{value}'. Must be one of: {', '.join(self.VALID_EVENT_TYPES[:10])}...",
                    value=value,
                    error_type=ValidationErrorType.INVALID_EVENT_TYPE,
                    severity=ValidationSeverity.WARNING,
                )
                result.add_warning(error)
        
        # Validate protocol
        if "protocol" in data and data["protocol"]:
            value = data["protocol"]
            if value not in self.VALID_PROTOCOLS:
                error = self._create_error(
                    field="protocol",
                    message=f"Invalid protocol '{value}'. Must be one of: {', '.join(self.VALID_PROTOCOLS)}",
                    value=value,
                    error_type=ValidationErrorType.INVALID_PROTOCOL,
                    severity=ValidationSeverity.WARNING,
                )
                result.add_warning(error)
        
        # Validate action
        if "action" in data and data["action"]:
            value = data["action"]
            if value not in self.VALID_ACTIONS:
                error = self._create_error(
                    field="action",
                    message=f"Invalid action '{value}'. Must be one of: {', '.join(self.VALID_ACTIONS)}",
                    value=value,
                    error_type=ValidationErrorType.INVALID_ACTION,
                    severity=ValidationSeverity.WARNING,
                )
                result.add_warning(error)
        
        # Validate severity
        if "severity" in data and data["severity"]:
            value = data["severity"]
            if value not in self.VALID_SEVERITIES:
                error = self._create_error(
                    field="severity",
                    message=f"Invalid severity '{value}'. Must be one of: {', '.join(self.VALID_SEVERITIES)}",
                    value=value,
                    error_type=ValidationErrorType.INVALID_SEVERITY,
                    severity=ValidationSeverity.WARNING,
                )
                result.add_warning(error)
    
    def _validate_source_destination(self, data: Dict[str, Any], result: ValidationResult) -> None:
        """Validate source and destination objects."""
        # Validate source
        if "source" in data and data["source"]:
            source = data["source"]
            if isinstance(source, dict):
                for field in self.SOURCE_FIELDS:
                    if field in source and source[field] is not None:
                        # Validate specific fields
                        if field == "ip":
                            self._validate_ip(source[field], "source.ip", result)
                        elif field == "port":
                            self._validate_port(source[field], "source.port", result)
                        elif field == "mac":
                            self._validate_mac(source[field], "source.mac", result)
            else:
                error = self._create_error(
                    field="source",
                    message="Source must be an object",
                    value=source,
                    error_type=ValidationErrorType.INVALID_FIELD_TYPE,
                    severity=ValidationSeverity.ERROR,
                )
                result.add_error(error)
        
        # Validate destination
        if "destination" in data and data["destination"]:
            dest = data["destination"]
            if isinstance(dest, dict):
                for field in self.DESTINATION_FIELDS:
                    if field in dest and dest[field] is not None:
                        if field == "ip":
                            self._validate_ip(dest[field], "destination.ip", result)
                        elif field == "port":
                            self._validate_port(dest[field], "destination.port", result)
            else:
                error = self._create_error(
                    field="destination",
                    message="Destination must be an object",
                    value=dest,
                    error_type=ValidationErrorType.INVALID_FIELD_TYPE,
                    severity=ValidationSeverity.ERROR,
                )
                result.add_error(error)
    
    def _validate_ip(self, ip: str, field: str, result: ValidationResult) -> None:
        """Validate IP address."""
        import re
        if not isinstance(ip, str):
            error = self._create_error(
                field=field,
                message=f"IP must be a string, got {type(ip).__name__}",
                value=ip,
                error_type=ValidationErrorType.INVALID_IP,
                severity=ValidationSeverity.ERROR,
            )
            result.add_error(error)
            return
        
        # Simple IPv4 validation
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, ip):
            error = self._create_error(
                field=field,
                message=f"Invalid IP address format: {ip}",
                value=ip,
                error_type=ValidationErrorType.INVALID_IP,
                severity=ValidationSeverity.ERROR,
            )
            result.add_error(error)
            return
        
        # Check octets
        parts = ip.split('.')
        if not all(0 <= int(p) <= 255 for p in parts):
            error = self._create_error(
                field=field,
                message=f"IP address octet out of range: {ip}",
                value=ip,
                error_type=ValidationErrorType.INVALID_IP,
                severity=ValidationSeverity.ERROR,
            )
            result.add_error(error)
    
    def _validate_port(self, port: Any, field: str, result: ValidationResult) -> None:
        """Validate port number."""
        try:
            port_int = int(port)
            if not (0 <= port_int <= 65535):
                error = self._create_error(
                    field=field,
                    message=f"Port must be between 0 and 65535, got {port_int}",
                    value=port,
                    error_type=ValidationErrorType.INVALID_PORT,
                    severity=ValidationSeverity.ERROR,
                )
                result.add_error(error)
        except (ValueError, TypeError):
            error = self._create_error(
                field=field,
                message=f"Port must be a number, got {type(port).__name__}",
                value=port,
                error_type=ValidationErrorType.INVALID_PORT,
                severity=ValidationSeverity.ERROR,
            )
            result.add_error(error)
    
    def _validate_mac(self, mac: str, field: str, result: ValidationResult) -> None:
        """Validate MAC address."""
        import re
        if not isinstance(mac, str):
            error = self._create_error(
                field=field,
                message=f"MAC must be a string, got {type(mac).__name__}",
                value=mac,
                error_type=ValidationErrorType.INVALID_MAC,
                severity=ValidationSeverity.WARNING,
            )
            result.add_warning(error)
            return
        
        # MAC address validation
        pattern = r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$'
        if not re.match(pattern, mac):
            error = self._create_error(
                field=field,
                message=f"Invalid MAC address format: {mac}",
                value=mac,
                error_type=ValidationErrorType.INVALID_MAC,
                severity=ValidationSeverity.WARNING,
            )
            result.add_warning(error)
    
    def _validate_extra_fields(self, data: Dict[str, Any], result: ValidationResult) -> None:
        """Validate that there are no extra fields."""
        allowed_fields = set(self.REQUIRED_FIELDS + self.OPTIONAL_FIELDS)
        extra_fields = set(data.keys()) - allowed_fields
        
        # Skip internal fields starting with _
        extra_fields = {f for f in extra_fields if not f.startswith('_')}
        
        for field in extra_fields:
            error = self._create_error(
                field=field,
                message=f"Extra field '{field}' not in schema",
                value=data[field],
                error_type=ValidationErrorType.EXTRA_FIELD,
                severity=ValidationSeverity.WARNING,
            )
            result.add_warning(error)