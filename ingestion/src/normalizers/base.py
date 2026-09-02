"""Base normalizer interface."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime

from src.core.logging import get_logger
from src.core.exceptions import NormalizationError


class BaseNormalizer(ABC):
    """
    Abstract base class for all normalizers.
    
    Normalizers convert parsed data into canonical formats.
    They standardize field names, values, formats, and types.
    """
    
    def __init__(
        self,
        normalizer_name: Optional[str] = None,
    ):
        """
        Initialize the normalizer.
        
        Args:
            normalizer_name: Name of the normalizer for logging
        """
        self.normalizer_name = normalizer_name or self.__class__.__name__
        self.logger = get_logger(f"normalizer.{self.normalizer_name}")
        self._stats = {
            "normalized_success": 0,
            "normalized_failed": 0,
            "fields_normalized": 0,
            "last_normalize_time": None,
        }
    
    @abstractmethod
    def normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize the input data.
        
        Args:
            data: Raw/parsed data to normalize
            
        Returns:
            Dict[str, Any]: Normalized data
            
        Raises:
            NormalizationError: If normalization fails
        """
        pass
    
    def normalize_batch(self, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize multiple items.
        
        Args:
            data_list: List of data to normalize
            
        Returns:
            List[Dict[str, Any]]: Normalized data
        """
        results = []
        for data in data_list:
            try:
                normalized = self.normalize(data)
                results.append(normalized)
                self._stats["normalized_success"] += 1
            except Exception as e:
                self.logger.error(f"Failed to normalize data: {e}")
                self._stats["normalized_failed"] += 1
                # Return original data with error flag
                data["_normalization_error"] = str(e)
                results.append(data)
        
        return results
    
    def _update_stats(self, success: bool = True, fields_count: int = 0) -> None:
        """Update normalization statistics."""
        if success:
            self._stats["normalized_success"] += 1
        else:
            self._stats["normalized_failed"] += 1
        self._stats["fields_normalized"] += fields_count
        self._stats["last_normalize_time"] = datetime.utcnow()
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Get normalization statistics."""
        return self._stats.copy()
    
    def _safe_get(self, data: Dict[str, Any], key: str, default: Any = None) -> Any:
        """
        Safely get a value from dict with case-insensitive key matching.
        
        Args:
            data: Dictionary to search
            key: Key to look for
            default: Default value if not found
            
        Returns:
            Any: Value found or default
        """
        # Direct match
        if key in data:
            return data[key]
        
        # Case-insensitive match
        key_lower = key.lower()
        for k, v in data.items():
            if k.lower() == key_lower:
                return v
        
        return default