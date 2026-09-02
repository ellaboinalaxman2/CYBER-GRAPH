"""Field-level validator for checking individual field values."""

import re
from typing import Dict, Any, Optional, List, Callable, Union
from datetime import datetime

from src.validators.base import BaseValidator
from src.validators.validation_errors import (
    ValidationResult,
    ValidationError,
    ValidationErrorType,
    ValidationSeverity,
)


class FieldValidator(BaseValidator):
    """
    Validates individual field values.
    
    Supports:
    - String length checks
    - Pattern matching (regex)
    - Numeric range checks
    - Custom validation functions
    - Field dependencies
    """
    
    def __init__(
        self,
        strict_mode: bool = False,
        max_string_length: int = 10000,
        min_string_length: int = 1,
    ):
        """
        Initialize field validator.
        
        Args:
            strict_mode: Whether to fail on warnings
            max_string_length: Maximum string length
            min_string_length: Minimum string length
        """
        super().__init__(validator_name="field-validator", strict_mode=strict_mode)
        self.max_string_length = max_string_length
        self.min_string_length = min_string_length
        self._custom_validators: Dict[str, Callable] = {}
        self._load_custom_rules()
    
    def _load_custom_rules(self) -> None:
        """Load custom validation rules from file."""
        import json
        from pathlib import Path
        
        rules_file = Path("data/validation_rules/field_rules.json")
        if rules_file.exists():
            try:
                with open(rules_file, 'r') as f:
                    rules = json.load(f)
                    # Store rules for use in validation
                    self._custom_rules = rules
                    self.logger.info(f"Loaded custom field rules from {rules_file}")
            except Exception as e:
                self.logger.warning(f"Failed to load field rules: {e}")
        else:
            self._custom_rules = {}
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """
        Validate field values.
        
        Args:
            data: Data to validate
            
        Returns:
            ValidationResult: Result of validation
        """
        result = ValidationResult()
        
        # Validate string fields
        self._validate_string_fields(data, result)
        
        # Validate numeric fields
        self._validate_numeric_fields(data, result)
        
        # Validate date/time fields
        self._validate_datetime_fields(data, result)
        
        # Validate list fields
        self._validate_list_fields(data, result)
        
        # Apply custom validators
        self._apply_custom_validators(data, result)
        
        self._update_stats(result)
        return result
    
    def _validate_string_fields(self, data: Dict[str, Any], result: ValidationResult) -> None:
        """Validate string fields."""
        string_fields = [
            "event_id", "event_type", "raw_source", "protocol",
            "action", "severity", "message", "raw_message",
        ]
        
        for field in string_fields:
            if field in data and data[field] is not None:
                value = data[field]
                
                # Check if value is a string
                if not isinstance(value, str):
                    error = self._create_error(
                        field=field,
                        message=f"Field '{field}' must be a string, got {type(value).__name__}",
                        value=value,
                        error_type=ValidationErrorType.INVALID_FIELD_TYPE,
                        severity=ValidationSeverity.ERROR,
                    )
                    result.add_error(error)
                    continue
                
                # Check length
                if len(value) < self.min_string_length:
                    error = self._create_error(
                        field=field,
                        message=f"Field '{field}' is too short (minimum {self.min_string_length} characters)",
                        value=value,
                        error_type=ValidationErrorType.INVALID_LENGTH,
                        severity=ValidationSeverity.WARNING,
                    )
                    result.add_warning(error)
                
                if len(value) > self.max_string_length:
                    error = self._create_error(
                        field=field,
                        message=f"Field '{field}' is too long (maximum {self.max_string_length} characters)",
                        value=value[:100] + "...",
                        error_type=ValidationErrorType.TRUNCATED_FIELD,
                        severity=ValidationSeverity.ERROR,
                    )
                    result.add_error(error)
                
                # Check for empty/whitespace
                if not value.strip():
                    error = self._create_error(
                        field=field,
                        message=f"Field '{field}' is empty or contains only whitespace",
                        value=value,
                        error_type=ValidationErrorType.EMPTY_FIELD,
                        severity=ValidationSeverity.ERROR,
                    )
                    result.add_error(error)
    
    def _validate_numeric_fields(self, data: Dict[str, Any], result: ValidationResult) -> None:
        """Validate numeric fields."""
        numeric_fields = [
            "source_port",
            "destination_port",
        ]
        
        for field in numeric_fields:
            if field in data and data[field] is not None:
                value = data[field]
                
                # Check if value is numeric
                try:
                    num_value = float(value)
                except (ValueError, TypeError):
                    error = self._create_error(
                        field=field,
                        message=f"Field '{field}' must be numeric, got {type(value).__name__}",
                        value=value,
                        error_type=ValidationErrorType.INVALID_FIELD_TYPE,
                        severity=ValidationSeverity.ERROR,
                    )
                    result.add_error(error)
                    continue
                
                # Port range validation
                if "port" in field:
                    if not (0 <= num_value <= 65535):
                        error = self._create_error(
                            field=field,
                            message=f"Port must be between 0 and 65535, got {num_value}",
                            value=value,
                            error_type=ValidationErrorType.INVALID_RANGE,
                            severity=ValidationSeverity.ERROR,
                        )
                        result.add_error(error)
    
    def _validate_datetime_fields(self, data: Dict[str, Any], result: ValidationResult) -> None:
        """Validate datetime fields."""
        datetime_fields = ["timestamp"]
        
        for field in datetime_fields:
            if field in data and data[field] is not None:
                value = data[field]
                
                # Try to parse as datetime
                try:
                    if isinstance(value, str):
                        # Try ISO format
                        datetime.fromisoformat(value.replace('Z', '+00:00'))
                    elif isinstance(value, datetime):
                        # Already a datetime
                        pass
                    else:
                        error = self._create_error(
                            field=field,
                            message=f"Field '{field}' must be a valid timestamp",
                            value=value,
                            error_type=ValidationErrorType.INVALID_TIMESTAMP,
                            severity=ValidationSeverity.ERROR,
                        )
                        result.add_error(error)
                except (ValueError, TypeError):
                    error = self._create_error(
                        field=field,
                        message=f"Invalid timestamp format: {value}",
                        value=value,
                        error_type=ValidationErrorType.INVALID_TIMESTAMP,
                        severity=ValidationSeverity.ERROR,
                    )
                    result.add_error(error)
    
    def _validate_list_fields(self, data: Dict[str, Any], result: ValidationResult) -> None:
        """Validate list fields."""
        list_fields = ["tags", "normalized_fields"]
        
        for field in list_fields:
            if field in data and data[field] is not None:
                value = data[field]
                
                if not isinstance(value, list):
                    error = self._create_error(
                        field=field,
                        message=f"Field '{field}' must be a list, got {type(value).__name__}",
                        value=value,
                        error_type=ValidationErrorType.INVALID_FIELD_TYPE,
                        severity=ValidationSeverity.ERROR,
                    )
                    result.add_error(error)
                    continue
                
                # Validate list items
                if field == "tags":
                    for i, tag in enumerate(value):
                        if not isinstance(tag, str):
                            error = self._create_error(
                                field=f"{field}[{i}]",
                                message=f"Tag must be a string, got {type(tag).__name__}",
                                value=tag,
                                error_type=ValidationErrorType.INVALID_FIELD_TYPE,
                                severity=ValidationSeverity.WARNING,
                            )
                            result.add_warning(error)
                        elif not tag.strip():
                            error = self._create_error(
                                field=f"{field}[{i}]",
                                message="Tag cannot be empty",
                                value=tag,
                                error_type=ValidationErrorType.EMPTY_FIELD,
                                severity=ValidationSeverity.WARNING,
                            )
                            result.add_warning(error)
    
    def _apply_custom_validators(self, data: Dict[str, Any], result: ValidationResult) -> None:
        """Apply custom validation rules."""
        if not self._custom_rules:
            return
        
        for rule in self._custom_rules.get("validations", []):
            field = rule.get("field")
            validation_type = rule.get("type")
            
            if not field or field not in data:
                continue
            
            value = data[field]
            
            if validation_type == "regex":
                pattern = rule.get("pattern")
                if pattern and isinstance(value, str):
                    if not re.match(pattern, value):
                        error = self._create_error(
                            field=field,
                            message=f"Value does not match expected pattern: {rule.get('description', '')}",
                            value=value,
                            error_type=ValidationErrorType.INVALID_PATTERN,
                            severity=ValidationSeverity(rule.get("severity", "warning")),
                        )
                        if rule.get("severity", "warning") == "error":
                            result.add_error(error)
                        else:
                            result.add_warning(error)
            
            elif validation_type == "in_list":
                allowed_values = rule.get("allowed_values", [])
                if value not in allowed_values:
                    error = self._create_error(
                        field=field,
                        message=f"Value '{value}' not in allowed values: {allowed_values}",
                        value=value,
                        error_type=ValidationErrorType.INVALID_FIELD_TYPE,
                        severity=ValidationSeverity(rule.get("severity", "warning")),
                    )
                    if rule.get("severity", "warning") == "error":
                        result.add_error(error)
                    else:
                        result.add_warning(error)
    
    def add_custom_validator(
        self,
        field: str,
        validator: Callable[[Any], bool],
        message: str,
        severity: str = "error",
    ) -> None:
        """
        Add a custom validation function.
        
        Args:
            field: Field to validate
            validator: Function that returns True if valid
            message: Error message if validation fails
            severity: Severity of validation failure
        """
        self._custom_validators[field] = validator
        # Store for later use
        if not hasattr(self, '_custom_rules'):
            self._custom_rules = {"validations": []}
        
        self._custom_rules["validations"].append({
            "field": field,
            "type": "custom",
            "description": message,
            "severity": severity,
        })