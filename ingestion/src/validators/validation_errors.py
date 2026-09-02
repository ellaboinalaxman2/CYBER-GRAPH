"""Validation error definitions."""

from typing import List, Dict, Any, Optional
from enum import Enum


class ValidationSeverity(str, Enum):
    """Validation severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationErrorType(str, Enum):
    """Types of validation errors."""
    # Schema errors
    MISSING_REQUIRED_FIELD = "missing_required_field"
    INVALID_FIELD_TYPE = "invalid_field_type"
    INVALID_FIELD_FORMAT = "invalid_field_format"
    EXTRA_FIELD = "extra_field"
    
    # Field value errors
    INVALID_IP = "invalid_ip"
    INVALID_PORT = "invalid_port"
    INVALID_MAC = "invalid_mac"
    INVALID_TIMESTAMP = "invalid_timestamp"
    INVALID_PROTOCOL = "invalid_protocol"
    INVALID_EVENT_TYPE = "invalid_event_type"
    INVALID_ACTION = "invalid_action"
    INVALID_SEVERITY = "invalid_severity"
    INVALID_HOSTNAME = "invalid_hostname"
    
    # Business rule errors
    INVALID_COMBINATION = "invalid_combination"
    INVALID_RANGE = "invalid_range"
    INVALID_LENGTH = "invalid_length"
    INVALID_PATTERN = "invalid_pattern"
    SUSPICIOUS_PATTERN = "suspicious_pattern"
    
    # Quality errors
    EMPTY_FIELD = "empty_field"
    TRUNCATED_FIELD = "truncated_field"
    MALFORMED_DATA = "malformed_data"


class ValidationError:
    """Represents a validation error."""
    
    def __init__(
        self,
        error_type: ValidationErrorType,
        field: Optional[str] = None,
        message: str = "",
        value: Any = None,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a validation error.
        
        Args:
            error_type: Type of validation error
            field: Field that failed validation
            message: Error message
            value: The value that failed validation
            severity: Severity of the error
            details: Additional error details
        """
        self.error_type = error_type
        self.field = field
        self.message = message
        self.value = value
        self.severity = severity
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "error_type": self.error_type.value if isinstance(self.error_type, ValidationErrorType) else str(self.error_type),
            "field": self.field,
            "message": self.message,
            "value": self.value,
            "severity": self.severity.value if isinstance(self.severity, ValidationSeverity) else str(self.severity),
            "details": self.details,
        }
    
    def __str__(self) -> str:
        return f"[{self.severity.value.upper()}] {self.field}: {self.message}"


class ValidationResult:
    """Result of a validation operation."""
    
    def __init__(self, is_valid: bool = True):
        """
        Initialize validation result.
        
        Args:
            is_valid: Whether validation passed
        """
        self.is_valid = is_valid
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
        self.info_messages: List[ValidationError] = []
        self.metadata: Dict[str, Any] = {}
    
    def add_error(self, error: ValidationError) -> None:
        """Add an error to the result."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: ValidationError) -> None:
        """Add a warning to the result."""
        self.warnings.append(warning)
    
    def add_info(self, info: ValidationError) -> None:
        """Add an info message to the result."""
        self.info_messages.append(info)
    
    def merge(self, other: 'ValidationResult') -> None:
        """Merge another validation result into this one."""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.info_messages.extend(other.info_messages)
        self.metadata.update(other.metadata)
        if not other.is_valid:
            self.is_valid = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [w.to_dict() for w in self.warnings],
            "info": [i.to_dict() for i in self.info_messages],
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "info_count": len(self.info_messages),
            "metadata": self.metadata,
        }
    
    def get_error_messages(self) -> List[str]:
        """Get all error messages."""
        return [str(e) for e in self.errors]
    
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0