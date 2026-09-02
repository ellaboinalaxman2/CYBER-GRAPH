"""Custom exceptions for Member 5 - Attack Engine."""

from typing import Optional, Dict, Any


class AttackEngineError(Exception):
    """Base exception for Attack Engine errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class CorrelationError(AttackEngineError):
    """Raised when correlation fails."""
    pass


class ReconstructionError(AttackEngineError):
    """Raised when reconstruction fails."""
    pass


class RiskError(AttackEngineError):
    """Raised when risk calculation fails."""
    pass


class MitreError(AttackEngineError):
    """Raised when MITRE mapping fails."""
    pass


class AlertError(AttackEngineError):
    """Raised when alert generation fails."""
    pass