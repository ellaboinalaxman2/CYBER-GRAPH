"""Custom exceptions for Member 3 - AI Engine."""

from typing import Optional, Any


class AIEngineError(Exception):
    """Base exception for AI Engine errors."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class DataLoaderError(AIEngineError):
    """Raised when data loading fails."""
    pass


class PreprocessingError(AIEngineError):
    """Raised when preprocessing fails."""
    pass


class FeatureEngineeringError(AIEngineError):
    """Raised when feature engineering fails."""
    pass


class GraphConstructionError(AIEngineError):
    """Raised when graph construction fails."""
    pass


class ModelError(AIEngineError):
    """Raised when model operations fail."""
    pass


class TrainingError(AIEngineError):
    """Raised when training fails."""
    pass


class InferenceError(AIEngineError):
    """Raised when inference fails."""
    pass


class ModelNotFoundError(AIEngineError):
    """Raised when a model is not found."""
    pass


class ValidationError(AIEngineError):
    """Raised when validation fails."""
    pass


class ExplainabilityError(AIEngineError):
    """Raised when explainability operations fail."""
    pass


class EvaluationError(AIEngineError):
    """Raised when evaluation fails."""
    pass