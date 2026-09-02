"""Base parser interface for all log parsers."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime
import re

from src.core.logging import get_logger
from src.core.exceptions import ParserError
from src.models.raw_event import RawEvent


class BaseParser(ABC):
    """
    Abstract base class for all parsers.
    
    Parsers convert raw log content into structured data.
    They DO NOT normalize or enrich - just parse.
    
    Each parser implements:
    - parse(): Parse a single raw event into structured data
    - parse_batch(): Parse multiple raw events
    - supports(): Check if parser supports a given source type
    """
    
    def __init__(
        self,
        parser_name: Optional[str] = None,
    ):
        """
        Initialize the parser.
        
        Args:
            parser_name: Name of the parser for logging
        """
        self.parser_name = parser_name or self.__class__.__name__
        self.logger = get_logger(f"parser.{self.parser_name}")
        self._stats = {
            "parsed_success": 0,
            "parsed_failed": 0,
            "last_parse_time": None,
        }
    
    @abstractmethod
    def parse(self, raw_event: RawEvent) -> Optional[Dict[str, Any]]:
        """
        Parse a raw event into structured data.
        
        Args:
            raw_event: Raw event to parse
            
        Returns:
            Dict[str, Any]: Parsed structured data
            
        Raises:
            ParserError: If parsing fails critically
        """
        pass
    
    def parse_batch(self, raw_events: List[RawEvent]) -> List[Dict[str, Any]]:
        """
        Parse multiple raw events.
        
        Args:
            raw_events: List of raw events to parse
            
        Returns:
            List[Dict[str, Any]]: Parsed structured data
        """
        results = []
        for event in raw_events:
            try:
                parsed = self.parse(event)
                if parsed:
                    results.append(parsed)
                    self._stats["parsed_success"] += 1
            except Exception as e:
                self.logger.error(f"Failed to parse event: {e}")
                self._stats["parsed_failed"] += 1
                # Continue with next event
        
        return results
    
    @staticmethod
    @abstractmethod
    def supports(source_type: str) -> bool:
        """
        Check if this parser supports the given source type.
        
        Args:
            source_type: Type of source (syslog, firewall, etc.)
            
        Returns:
            bool: True if supported, False otherwise
        """
        pass
    
    def _update_stats(self, success: bool = True) -> None:
        """Update parsing statistics."""
        if success:
            self._stats["parsed_success"] += 1
        else:
            self._stats["parsed_failed"] += 1
        self._stats["last_parse_time"] = datetime.utcnow()
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Get parsing statistics."""
        return self._stats.copy()
    
    def _extract_timestamp(self, text: str) -> Optional[str]:
        """
        Extract timestamp from text using common patterns.
        
        Args:
            text: Text to extract timestamp from
            
        Returns:
            Optional[str]: Extracted timestamp string
        """
        # Common timestamp patterns
        patterns = [
            r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z?)',  # ISO 8601
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d{3})?)',    # MySQL/PostgreSQL
            r'([A-Za-z]{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})',         # Apache/Nginx
            r'(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})',             # US format
            r'(\d{1,2}/\d{1,2}/\d{2,4}\s+\d{2}:\d{2}:\d{2})',       # Short US format
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_ip(self, text: str) -> Optional[str]:
        """
        Extract IP address from text.
        
        Args:
            text: Text to extract IP from
            
        Returns:
            Optional[str]: Extracted IP address
        """
        # IPv4 pattern
        ip_pattern = r'\b(\d{1,3}\.){3}\d{1,3}\b'
        match = re.search(ip_pattern, text)
        if match:
            ip = match.group(0)
            # Validate each octet
            parts = ip.split('.')
            if all(0 <= int(p) <= 255 for p in parts):
                return ip
        return None