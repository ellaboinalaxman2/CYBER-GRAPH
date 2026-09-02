"""Business rule validator for complex validation rules."""

import re
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta

from src.validators.base import BaseValidator
from src.validators.validation_errors import (
    ValidationResult,
    ValidationError,
    ValidationErrorType,
    ValidationSeverity,
)


class RuleValidator(BaseValidator):
    """
    Validates business rules and relationships between fields.
    
    Supports:
    - Field dependencies
    - Conditional validation
    - Suspicious pattern detection
    - Event correlation rules
    - Custom business rules
    """
    
    def __init__(self, strict_mode: bool = False):
        """
        Initialize rule validator.
        
        Args:
            strict_mode: Whether to fail on warnings
        """
        super().__init__(validator_name="rule-validator", strict_mode=strict_mode)
        self._rules = []
        self._load_rules_from_file()
    
    def _load_rules_from_file(self) -> None:
        """Load business rules from file."""
        import json
        from pathlib import Path
        
        rules_file = Path("data/validation_rules/business_rules.json")
        if rules_file.exists():
            try:
                with open(rules_file, 'r') as f:
                    rules_data = json.load(f)
                    self._rules = rules_data.get("rules", [])
                    self.logger.info(f"Loaded {len(self._rules)} business rules from {rules_file}")
            except Exception as e:
                self.logger.warning(f"Failed to load business rules: {e}")
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """
        Validate business rules.
        
        Args:
            data: Data to validate
            
        Returns:
            ValidationResult: Result of validation
        """
        result = ValidationResult()
        
        # Apply built-in rules
        self._validate_field_dependencies(data, result)
        self._validate_conditional_rules(data, result)
        self._validate_suspicious_patterns(data, result)
        
        # Apply custom rules
        self._apply_custom_rules(data, result)
        
        self._update_stats(result)
        return result
    
    def _validate_field_dependencies(self, data: Dict[str, Any], result: ValidationResult) -> None:
        """
        Validate that dependent fields are present when required.
        
        Rules:
        - If destination_port is present, destination.ip should also be present
        - If source_port is present, source.ip should also be present
        - If action is present, event_type should be present
        """
        dependencies = [
            ("destination_port", "destination", "ip"),
            ("source_port", "source", "ip"),
            ("action", "event_type", None),
            ("protocol", "event_type", None),
        ]
        
        for field, depend_field, sub_field in dependencies:
            if field in data and data[field] is not None:
                if depend_field not in data or data[depend_field] is None:
                    error = self._create_error(
                        field=depend_field,
                        message=f"'{depend_field}' is required when '{field}' is present",
                        value=data.get(depend_field),
                        error_type=ValidationErrorType.INVALID_COMBINATION,
                        severity=ValidationSeverity.ERROR,
                    )
                    result.add_error(error)
                elif sub_field and isinstance(data[depend_field], dict):
                    if sub_field not in data[depend_field] or data[depend_field][sub_field] is None:
                        error = self._create_error(
                            field=f"{depend_field}.{sub_field}",
                            message=f"'{depend_field}.{sub_field}' is required when '{field}' is present",
                            value=data[depend_field].get(sub_field),
                            error_type=ValidationErrorType.INVALID_COMBINATION,
                            severity=ValidationSeverity.ERROR,
                        )
                        result.add_error(error)
    
    def _validate_conditional_rules(self, data: Dict[str, Any], result: ValidationResult) -> None:
        """
        Apply conditional validation rules.
        
        Rules:
        - If action is "DENY" or "BLOCK", severity should be at least "MEDIUM"
        - If event_type is "LOGIN_FAILURE", severity should be at least "LOW"
        - If protocol is "HTTP", action should not be "DENY" for port 443
        """
        # Rule: DENY/BLOCK actions should have higher severity
        if "action" in data and data["action"] in ["DENY", "BLOCK", "DROP"]:
            if "severity" in data and data["severity"] in ["INFO", "LOW"]:
                error = self._create_error(
                    field="severity",
                    message=f"Severity '{data['severity']}' is too low for action '{data['action']}'",
                    value=data["severity"],
                    error_type=ValidationErrorType.INVALID_COMBINATION,
                    severity=ValidationSeverity.WARNING,
                )
                result.add_warning(error)
        
        # Rule: Login failures should have at least LOW severity
        if "event_type" in data and data["event_type"] == "LOGIN_FAILURE":
            if "severity" in data and data["severity"] == "INFO":
                error = self._create_error(
                    field="severity",
                    message=f"Login failures should have at least LOW severity, got '{data['severity']}'",
                    value=data["severity"],
                    error_type=ValidationErrorType.INVALID_COMBINATION,
                    severity=ValidationSeverity.WARNING,
                )
                result.add_warning(error)
        
        # Rule: HTTPS on port 443 shouldn't be denied
        if "destination_port" in data and data["destination_port"] == 443:
            if "protocol" in data and data["protocol"] == "HTTP":
                error = self._create_error(
                    field="protocol",
                    message="HTTPS traffic should use HTTPS protocol, not HTTP",
                    value=data["protocol"],
                    error_type=ValidationErrorType.INVALID_COMBINATION,
                    severity=ValidationSeverity.WARNING,
                )
                result.add_warning(error)
    
    def _validate_suspicious_patterns(self, data: Dict[str, Any], result: ValidationResult) -> None:
        """
        Detect suspicious patterns in events.
        """
        # Check for suspicious IPs
        if "source" in data and isinstance(data["source"], dict):
            ip = data["source"].get("ip")
            if ip:
                # Check for localhost
                if ip == "127.0.0.1":
                    error = self._create_error(
                        field="source.ip",
                        message="Event from localhost detected - suspicious",
                        value=ip,
                        error_type=ValidationErrorType.SUSPICIOUS_PATTERN,
                        severity=ValidationSeverity.WARNING,
                    )
                    result.add_warning(error)
                
                # Check for broadcast
                if ip.endswith(".255"):
                    error = self._create_error(
                        field="source.ip",
                        message=f"Broadcast IP detected: {ip}",
                        value=ip,
                        error_type=ValidationErrorType.SUSPICIOUS_PATTERN,
                        severity=ValidationSeverity.WARNING,
                    )
                    result.add_warning(error)
                
                # Check for suspicious ports
                if "source_port" in data and data["source_port"] == 0:
                    error = self._create_error(
                        field="source_port",
                        message="Source port 0 detected - suspicious",
                        value=0,
                        error_type=ValidationErrorType.SUSPICIOUS_PATTERN,
                        severity=ValidationSeverity.WARNING,
                    )
                    result.add_warning(error)
        
        # Check for privileged port usage (highly suspicious for clients)
        if "source" in data and isinstance(data["source"], dict):
            port = data["source"].get("port")
            if port and 1 <= port <= 1023:
                error = self._create_error(
                    field="source.port",
                    message=f"Privileged source port {port} detected - suspicious",
                    value=port,
                    error_type=ValidationErrorType.SUSPICIOUS_PATTERN,
                    severity=ValidationSeverity.WARNING,
                )
                result.add_warning(error)
        
        # Check for large number of ports (port scanning)
        # This would need correlation with other events
    
    def _apply_custom_rules(self, data: Dict[str, Any], result: ValidationResult) -> None:
        """
        Apply custom business rules from configuration.
        """
        for rule in self._rules:
            rule_type = rule.get("type")
            condition = rule.get("condition", {})
            
            # Check if rule applies
            if self._condition_matches(data, condition):
                message = rule.get("message", "Business rule violation")
                severity = ValidationSeverity(rule.get("severity", "warning"))
                
                error = self._create_error(
                    field=rule.get("field", "general"),
                    message=message,
                    value=data.get(rule.get("field")),
                    error_type=ValidationErrorType.INVALID_COMBINATION,
                    severity=severity,
                )
                
                if severity == ValidationSeverity.ERROR:
                    result.add_error(error)
                else:
                    result.add_warning(error)
    
    def _condition_matches(self, data: Dict[str, Any], condition: Dict[str, Any]) -> bool:
        """
        Check if a condition matches the data.
        
        Args:
            data: Data to check
            condition: Condition dictionary
            
        Returns:
            bool: True if condition matches
        """
        field = condition.get("field")
        operator = condition.get("operator", "equals")
        value = condition.get("value")
        
        if not field or field not in data:
            return False
        
        data_value = data[field]
        
        if operator == "equals":
            return data_value == value
        elif operator == "not_equals":
            return data_value != value
        elif operator == "contains":
            return value in str(data_value)
        elif operator == "not_contains":
            return value not in str(data_value)
        elif operator == "in":
            return data_value in value
        elif operator == "not_in":
            return data_value not in value
        elif operator == "greater_than":
            return data_value > value
        elif operator == "less_than":
            return data_value < value
        elif operator == "greater_or_equal":
            return data_value >= value
        elif operator == "less_or_equal":
            return data_value <= value
        elif operator == "regex_match":
            return bool(re.match(value, str(data_value)))
        
        return False
    
    def add_rule(
        self,
        field: str,
        condition: Dict[str, Any],
        message: str,
        severity: str = "warning",
    ) -> None:
        """
        Add a custom business rule.
        
        Args:
            field: Field to validate
            condition: Condition dictionary
            message: Error message
            severity: Severity of violation
        """
        self._rules.append({
            "field": field,
            "condition": condition,
            "message": message,
            "severity": severity,
            "type": "custom",
        })