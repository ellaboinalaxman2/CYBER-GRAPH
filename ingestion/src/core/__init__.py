"""Core module for configuration, logging, and exceptions."""

from src.core.config import settings
from src.core.logging import setup_logging, get_logger
from src.core.exceptions import (
    IngestionError,
    CollectorError,
    ParserError,
    NormalizationError,
    ValidationError,
    EnrichmentError,
    SchemaError,
)

__all__ = [
    "settings",
    "setup_logging",
    "get_logger",
    "IngestionError",
    "CollectorError",
    "ParserError",
    "NormalizationError",
    "ValidationError",
    "EnrichmentError",
    "SchemaError",
]