"""Main event normalizer that orchestrates all normalization."""

from typing import Dict, Any, Optional, List

from src.normalizers.base import BaseNormalizer
from src.normalizers.field_mapper import FieldMapper
from src.normalizers.timestamp_normalizer import TimestampNormalizer
from src.normalizers.ip_normalizer import IPNormalizer
from src.normalizers.protocol_normalizer import ProtocolNormalizer
from src.normalizers.event_type_mapper import EventTypeMapper
from src.core.exceptions import NormalizationError
from src.core.logging import get_logger


class EventNormalizer(BaseNormalizer):
    """
    Main event normalizer that orchestrates all normalization steps.
    
    Combines:
    - Field mapping
    - Timestamp normalization
    - IP normalization
    - Protocol normalization
    - Event type mapping
    """
    
    def __init__(self):
        """Initialize the event normalizer with all sub-normalizers."""
        super().__init__(normalizer_name="event-normalizer")
        
        self.field_mapper = FieldMapper()
        self.timestamp_normalizer = TimestampNormalizer()
        self.ip_normalizer = IPNormalizer()
        self.protocol_normalizer = ProtocolNormalizer()
        self.event_type_mapper = EventTypeMapper()
        
        self.logger = get_logger("normalizer.event")
    
    def normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize an event through all normalization steps.
        
        Args:
            data: Parsed event data
            
        Returns:
            Dict[str, Any]: Fully normalized event
            
        Raises:
            NormalizationError: If normalization fails
        """
        try:
            result = data.copy()
            
            # Track normalization steps
            normalization_steps = []
            
            # Step 1: Field mapping
            result = self.field_mapper.normalize(result)
            normalization_steps.append("field_mapping")
            
            # Step 2: Timestamp normalization
            result = self.timestamp_normalizer.normalize(result)
            normalization_steps.append("timestamp_normalization")
            
            # Step 3: IP normalization
            result = self.ip_normalizer.normalize(result)
            normalization_steps.append("ip_normalization")
            
            # Step 4: Protocol normalization
            result = self.protocol_normalizer.normalize(result)
            normalization_steps.append("protocol_normalization")
            
            # Step 5: Event type mapping
            result = self.event_type_mapper.normalize(result)
            normalization_steps.append("event_type_mapping")
            
            # Add metadata
            result["_normalization_steps"] = normalization_steps
            result["_normalized_at"] = "auto"
            
            self._update_stats(success=True, fields_count=len(normalization_steps))
            
            return result
            
        except Exception as e:
            self.logger.error(f"Event normalization failed: {e}")
            self._update_stats(success=False)
            raise NormalizationError(f"Failed to normalize event: {e}")
    
    def normalize_batch(self, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize multiple events.
        
        Args:
            data_list: List of parsed events
            
        Returns:
            List[Dict[str, Any]]: Normalized events
        """
        results = []
        for data in data_list:
            try:
                normalized = self.normalize(data)
                results.append(normalized)
            except Exception as e:
                self.logger.error(f"Failed to normalize event: {e}")
                data["_normalization_error"] = str(e)
                results.append(data)
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get combined statistics from all normalizers.
        
        Returns:
            Dict[str, Any]: Combined statistics
        """
        return {
            "event_normalizer": self.stats,
            "field_mapper": self.field_mapper.stats,
            "timestamp_normalizer": self.timestamp_normalizer.stats,
            "ip_normalizer": self.ip_normalizer.stats,
            "protocol_normalizer": self.protocol_normalizer.stats,
            "event_type_mapper": self.event_type_mapper.stats,
        }