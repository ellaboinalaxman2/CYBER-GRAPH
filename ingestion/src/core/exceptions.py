"""Custom exceptions for the ingestion service."""

from typing import Optional, Any


class IngestionError(Exception):
    """Base exception for ingestion errors."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class CollectorError(IngestionError):
    """Raised when a collector fails to collect data."""
    pass


class ParserError(IngestionError):
    """Raised when parsing fails."""
    pass


class NormalizationError(IngestionError):
    """Raised when normalization fails."""
    pass


class ValidationError(IngestionError):
    """Raised when event validation fails."""
    
    def __init__(self, message: str, errors: list, details: Optional[dict] = None):
        self.errors = errors
        super().__init__(message, details)


class EnrichmentError(IngestionError):
    """Raised when enrichment fails."""
    pass


class SchemaError(IngestionError):
    """Raised when schema validation fails."""
    pass