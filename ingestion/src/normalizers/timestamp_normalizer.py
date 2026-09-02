"""Timestamp normalizer for standardizing timestamps."""

from typing import Optional, Dict, Any
from datetime import datetime, timezone
import re
from dateutil import parser

from src.normalizers.base import BaseNormalizer
from src.core.exceptions import NormalizationError


class TimestampNormalizer(BaseNormalizer):
    """
    Normalizes timestamps to UTC ISO format.
    
    Supports:
    - ISO 8601
    - RFC 3164 (syslog)
    - Common log formats
    - Unix timestamps
    - Custom formats
    """
    
    # Common timestamp patterns
    PATTERNS = {
        "iso": r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z?',
        "iso_space": r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d{3})?',
        "rfc3164": r'[A-Za-z]{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}',
        "us_date": r'\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}',
        "short_us": r'\d{1,2}/\d{1,2}/\d{2,4}\s+\d{2}:\d{2}:\d{2}',
        "unix": r'^\d{10}$',  # Unix timestamp (seconds)
        "unix_ms": r'^\d{13}$',  # Unix timestamp (milliseconds)
    }
    
    def __init__(self, default_timezone: str = "UTC"):
        """
        Initialize timestamp normalizer.
        
        Args:
            default_timezone: Default timezone for timestamps without timezone
        """
        super().__init__(normalizer_name="timestamp-normalizer")
        self.default_timezone = default_timezone
    
    def normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize timestamp fields in the data.
        
        Args:
            data: Dictionary containing timestamp data
            
        Returns:
            Dict[str, Any]: Data with normalized timestamp
        """
        result = data.copy()
        
        # Find timestamp fields
        timestamp_keys = ["timestamp", "time", "ts", "event_time", "log_time", "date", "datetime"]
        
        found_timestamp = None
        found_key = None
        
        for key in timestamp_keys:
            value = self._safe_get(data, key)
            if value:
                found_timestamp = value
                found_key = key
                break
        
        if found_timestamp:
            normalized = self._normalize_timestamp(found_timestamp)
            if normalized:
                result["timestamp"] = normalized
                result["_normalized_timestamp_from"] = found_key
                
                # Remove original timestamp field if different
                if found_key != "timestamp" and found_key in result:
                    del result[found_key]
                
                self._update_stats(success=True, fields_count=1)
            else:
                self.logger.warning(f"Failed to normalize timestamp: {found_timestamp}")
                self._update_stats(success=False)
                result["_timestamp_normalization_error"] = f"Could not parse: {found_timestamp}"
        else:
            # No timestamp found, use current time
            result["timestamp"] = datetime.now(timezone.utc).isoformat()
            result["_timestamp_normalization_warning"] = "No timestamp found, using current time"
        
        return result
    
    def _normalize_timestamp(self, value: Any) -> Optional[str]:
        """
        Normalize a timestamp value to ISO 8601 UTC.
        
        Args:
            value: Timestamp value (string, int, datetime)
            
        Returns:
            Optional[str]: Normalized timestamp or None
        """
        if value is None:
            return None
        
        # If already a datetime object
        if isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            return value.isoformat()
        
        # If integer (Unix timestamp)
        if isinstance(value, (int, float)):
            try:
                if value > 10**12:  # Milliseconds
                    dt = datetime.fromtimestamp(value / 1000, tz=timezone.utc)
                else:  # Seconds
                    dt = datetime.fromtimestamp(value, tz=timezone.utc)
                return dt.isoformat()
            except (ValueError, OSError):
                return None
        
        # If string
        if isinstance(value, str):
            # Try to parse with dateutil
            try:
                dt = parser.parse(value)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.isoformat()
            except (ValueError, TypeError):
                pass
            
            # Try common patterns
            for pattern_name, pattern in self.PATTERNS.items():
                if re.match(pattern, value):
                    try:
                        dt = self._parse_known_format(value, pattern_name)
                        if dt:
                            return dt.isoformat()
                    except Exception:
                        continue
            
            return None
        
        return None
    
    def _parse_known_format(self, value: str, format_name: str) -> Optional[datetime]:
        """
        Parse timestamp using known format.
        
        Args:
            value: Timestamp string
            format_name: Name of the format pattern
            
        Returns:
            Optional[datetime]: Parsed datetime or None
        """
        try:
            if format_name == "rfc3164":
                # RFC 3164: "Aug 29 10:30:15"
                current_year = datetime.now().year
                dt = parser.parse(f"{value} {current_year}")
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            
            elif format_name in ["us_date", "short_us"]:
                # US date format
                dt = parser.parse(value)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            
            else:
                dt = parser.parse(value)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
                
        except Exception:
            return None
    
    @staticmethod
    def is_timestamp(value: Any) -> bool:
        """
        Check if value appears to be a timestamp.
        
        Args:
            value: Value to check
            
        Returns:
            bool: True if appears to be timestamp
        """
        if isinstance(value, datetime):
            return True
        
        if isinstance(value, (int, float)):
            # Check if in reasonable range (1970-2100)
            if 0 < value < 4102444800:  # 2100-01-01
                return True
        
        if isinstance(value, str):
            # Check if matches common patterns
            patterns = [
                r'\d{4}-\d{2}-\d{2}',  # Date
                r'\d{2}:\d{2}:\d{2}',  # Time
                r'[A-Za-z]{3}\s+\d{1,2}',  # Month day
                r'\d{10,13}$',  # Unix timestamp
            ]
            for pattern in patterns:
                if re.search(pattern, value):
                    return True
        
        return False