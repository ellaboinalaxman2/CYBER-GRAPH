"""Logging configuration for Member 5 - Attack Engine."""

import logging
import sys
from typing import Optional

from src.core.config import settings


def setup_logging(log_level: Optional[str] = None) -> None:
    """Configure logging for the application."""
    level = (log_level or settings.log_level).upper()
    
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level))
    
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    console_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(f"cybergraph.attack.{name}")