"""Base enricher interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime

from src.core.logging import get_logger
from src.models.enriched_event import EnrichedEvent


class BaseEnricher(ABC):
    """
    Abstract base class for all enrichers.
    
    Enrichers add contextual information to events.
    They do not modify the core event data, only add to it.
    """
    
    def __init__(
        self,
        enricher_name: Optional[str] = None,
        enabled: bool = True,
    ):
        """
        Initialize the enricher.
        
        Args:
            enricher_name: Name of the enricher for logging
            enabled: Whether the enricher is enabled
        """
        self.enricher_name = enricher_name or self.__class__.__name__
        self.logger = get_logger(f"enricher.{self.enricher_name}")
        self.enabled = enabled
        self._stats = {
            "enriched_success": 0,
            "enriched_failed": 0,
            "enrichments_applied": 0,
            "last_enrich_time": None,
        }
    
    @abstractmethod
    def enrich(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich the event with additional context.
        
        Args:
            event: Event data to enrich
            
        Returns:
            Dict[str, Any]: Enriched event data
            
        Raises:
            EnrichmentError: If enrichment fails critically
        """
        pass
    
    def enrich_batch(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich multiple events.
        
        Args:
            events: List of events to enrich
            
        Returns:
            List[Dict[str, Any]]: Enriched events
        """
        results = []
        for event in events:
            try:
                enriched = self.enrich(event)
                results.append(enriched)
                self._stats["enriched_success"] += 1
            except Exception as e:
                self.logger.error(f"Failed to enrich event: {e}")
                self._stats["enriched_failed"] += 1
                event["_enrichment_error"] = str(e)
                results.append(event)
        
        return results
    
    def _update_stats(self, success: bool = True, enrichments_count: int = 0) -> None:
        """Update enrichment statistics."""
        if success:
            self._stats["enriched_success"] += 1
        else:
            self._stats["enriched_failed"] += 1
        self._stats["enrichments_applied"] += enrichments_count
        self._stats["last_enrich_time"] = datetime.utcnow()
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Get enrichment statistics."""
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