"""Base validator interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

from src.core.logging import get_logger
from src.validators.validation_errors import ValidationResult, ValidationError, ValidationSeverity


class BaseValidator(ABC):
    """
    Abstract base class for all validators.
    
    Validators check that data meets quality standards.
    They can validate schema, field values, business rules, etc.
    """
    
    def __init__(
        self,
        validator_name: Optional[str] = None,
        strict_mode: bool = False,
    ):
        """
        Initialize the validator.
        
        Args:
            validator_name: Name of the validator for logging
            strict_mode: Whether to fail on warnings
        """
        self.validator_name = validator_name or self.__class__.__name__
        self.logger = get_logger(f"validator.{self.validator_name}")
        self.strict_mode = strict_mode
        self._stats = {
            "validated_success": 0,
            "validated_failed": 0,
            "validated_warning": 0,
            "total_errors": 0,
            "total_warnings": 0,
            "last_validation_time": None,
        }
    
    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """
        Validate the input data.
        
        Args:
            data: Data to validate
            
        Returns:
            ValidationResult: Result of validation
        """
        pass
    
    def validate_batch(self, data_list: List[Dict[str, Any]]) -> List[ValidationResult]:
        """
        Validate multiple items.
        
        Args:
            data_list: List of data to validate
            
        Returns:
            List[ValidationResult]: Results of validation
        """
        results = []
        for data in data_list:
            result = self.validate(data)
            results.append(result)
        
        return results
    
    def _create_error(
        self,
        field: str,
        message: str,
        value: Any = None,
        error_type: str = "validation_error",
        severity: ValidationSeverity = ValidationSeverity.ERROR,
    ) -> ValidationError:
        """Create a validation error."""
        return ValidationError(
            error_type=error_type,
            field=field,
            message=message,
            value=value,
            severity=severity,
        )
    
    def _update_stats(self, result: ValidationResult) -> None:
        """Update validation statistics."""
        from datetime import datetime
        
        if result.is_valid:
            self._stats["validated_success"] += 1
        else:
            self._stats["validated_failed"] += 1
        
        if result.warnings:
            self._stats["validated_warning"] += 1
        
        self._stats["total_errors"] += len(result.errors)
        self._stats["total_warnings"] += len(result.warnings)
        self._stats["last_validation_time"] = datetime.utcnow()
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Get validation statistics."""
        return self._stats.copy()