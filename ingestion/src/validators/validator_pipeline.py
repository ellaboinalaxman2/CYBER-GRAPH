"""Validator pipeline that orchestrates all validators."""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import os

from src.validators.base import BaseValidator
from src.validators.schema_validator import SchemaValidator
from src.validators.field_validator import FieldValidator
from src.validators.rule_validator import RuleValidator
from src.validators.validation_errors import ValidationResult, ValidationSeverity
from src.core.logging import get_logger
from src.core.config import settings


class ValidatorPipeline:
    """
    Orchestrates all validators in the correct order.
    
    Pipeline order:
    1. Schema validation (always first)
    2. Field validation
    3. Business rule validation
    """
    
    def __init__(
        self,
        strict_mode: bool = False,
        save_failed_events: bool = True,
    ):
        """
        Initialize the validator pipeline.
        
        Args:
            strict_mode: Whether to fail on warnings
            save_failed_events: Whether to save failed events to disk
        """
        self.logger = get_logger("validator.pipeline")
        self.strict_mode = strict_mode
        self.save_failed_events = save_failed_events
        
        # Initialize validators
        self.schema_validator = SchemaValidator(strict_mode=strict_mode)
        self.field_validator = FieldValidator(strict_mode=strict_mode)
        self.rule_validator = RuleValidator(strict_mode=strict_mode)
        
        self._stats = {
            "events_validated": 0,
            "events_passed": 0,
            "events_failed": 0,
            "events_with_warnings": 0,
            "total_errors": 0,
            "total_warnings": 0,
            "last_validation_time": None,
        }
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """
        Run all validators on the data.
        
        Args:
            data: Data to validate
            
        Returns:
            ValidationResult: Combined validation result
        """
        from datetime import datetime
        
        result = ValidationResult()
        result.metadata["validation_timestamp"] = datetime.utcnow().isoformat() + "Z"
        
        # Step 1: Schema validation
        schema_result = self.schema_validator.validate(data)
        result.merge(schema_result)
        
        # Step 2: Field validation
        field_result = self.field_validator.validate(data)
        result.merge(field_result)
        
        # Step 3: Rule validation
        rule_result = self.rule_validator.validate(data)
        result.merge(rule_result)
        
        # Update pipeline statistics
        self._update_stats(result)
        
        # Save failed events if configured
        if not result.is_valid and self.save_failed_events:
            self._save_failed_event(data, result)
        
        return result
    
    def validate_batch(self, data_list: List[Dict[str, Any]]) -> List[ValidationResult]:
        """
        Validate multiple events.
        
        Args:
            data_list: List of events to validate
            
        Returns:
            List[ValidationResult]: Results of validation
        """
        results = []
        for data in data_list:
            result = self.validate(data)
            results.append(result)
        
        return results
    
    def _update_stats(self, result: ValidationResult) -> None:
        """Update validation statistics."""
        from datetime import datetime
        
        self._stats["events_validated"] += 1
        
        if result.is_valid:
            self._stats["events_passed"] += 1
        else:
            self._stats["events_failed"] += 1
        
        if result.warnings:
            self._stats["events_with_warnings"] += 1
        
        self._stats["total_errors"] += len(result.errors)
        self._stats["total_warnings"] += len(result.warnings)
        self._stats["last_validation_time"] = datetime.utcnow()
    
    def _save_failed_event(self, data: Dict[str, Any], result: ValidationResult) -> None:
        """
        Save a failed event to disk for later inspection.
        
        Args:
            data: The event data
            result: The validation result
        """
        try:
            failed_dir = settings.failed_events_dir
            os.makedirs(failed_dir, exist_ok=True)
            
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            event_id = data.get("event_id", "unknown")
            filename = f"failed_{event_id}_{timestamp}.json"
            filepath = os.path.join(failed_dir, filename)
            
            failed_data = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "event": data,
                "validation_result": result.to_dict(),
            }
            
            with open(filepath, 'w') as f:
                json.dump(failed_data, f, indent=2, default=str)
            
            self.logger.info(f"Saved failed event to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Failed to save failed event: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get combined statistics from all validators.
        
        Returns:
            Dict[str, Any]: Combined statistics
        """
        return {
            "pipeline": self._stats.copy(),
            "schema_validator": self.schema_validator.stats,
            "field_validator": self.field_validator.stats,
            "rule_validator": self.rule_validator.stats,
        }
    
    def is_valid(self, data: Dict[str, Any]) -> bool:
        """
        Quick check if data is valid.
        
        Args:
            data: Data to check
            
        Returns:
            bool: True if valid
        """
        result = self.validate(data)
        return result.is_valid
    
    def add_custom_rule(
        self,
        field: str,
        condition: Dict[str, Any],
        message: str,
        severity: str = "warning",
    ) -> None:
        """
        Add a custom business rule to the pipeline.
        
        Args:
            field: Field to validate
            condition: Condition dictionary
            message: Error message
            severity: Severity of violation
        """
        self.rule_validator.add_rule(field, condition, message, severity)
        self.logger.info(f"Added custom rule for field '{field}'")