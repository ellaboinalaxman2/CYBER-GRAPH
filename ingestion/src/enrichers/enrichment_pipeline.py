"""Enrichment pipeline that orchestrates all enrichers."""

from typing import Dict, Any, Optional, List
from datetime import datetime

from src.enrichers.base import BaseEnricher
from src.enrichers.asset_enricher import AssetEnricher
from src.enrichers.geo_enricher import GeoEnricher
from src.enrichers.threat_intel_enricher import ThreatIntelEnricher
from src.enrichers.protocol_enricher import ProtocolEnricher
from src.enrichers.context_enricher import ContextEnricher
from src.core.logging import get_logger
from src.models.enriched_event import EnrichedEvent


class EnrichmentPipeline:
    """
    Orchestrates all enrichers in the correct order.
    
    Pipeline order:
    1. Protocol enrichment (first - adds protocol info)
    2. Asset enrichment
    3. Geographic enrichment
    4. Threat intelligence enrichment
    5. Contextual enrichment
    """
    
    def __init__(self, enabled_enrichers: Optional[List[str]] = None):
        """
        Initialize the enrichment pipeline.
        
        Args:
            enabled_enrichers: List of enricher names to enable
                              (None = enable all)
        """
        self.logger = get_logger("enricher.pipeline")
        
        # Initialize all enrichers
        self.enrichers = {
            "protocol": ProtocolEnricher(),
            "asset": AssetEnricher(),
            "geo": GeoEnricher(),
            "threat_intel": ThreatIntelEnricher(),
            "context": ContextEnricher(),
        }
        
        # Disable enrichers not in the list
        if enabled_enrichers is not None:
            for name in self.enrichers:
                self.enrichers[name].enabled = name in enabled_enrichers
        
        self._stats = {
            "events_enriched": 0,
            "events_with_enrichment": 0,
            "total_enrichments": 0,
            "last_enrich_time": None,
        }
    
    def enrich(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run all enrichers on the event.
        
        Args:
            event: Event data to enrich
            
        Returns:
            Dict[str, Any]: Enriched event
        """
        result = event.copy()
        enrichments_applied = []
        
        # Run each enricher in order
        for name, enricher in self.enrichers.items():
            if enricher.enabled:
                try:
                    result = enricher.enrich(result)
                    # Track enrichments from metadata
                    if "enrichment_applied" in result:
                        new_enrichments = [e for e in result["enrichment_applied"] 
                                         if e not in enrichments_applied]
                        enrichments_applied.extend(new_enrichments)
                except Exception as e:
                    self.logger.error(f"Enricher '{name}' failed: {e}")
                    result[f"_enrichment_error_{name}"] = str(e)
        
        # Update statistics
        self._stats["events_enriched"] += 1
        if enrichments_applied:
            self._stats["events_with_enrichment"] += 1
            self._stats["total_enrichments"] += len(enrichments_applied)
        
        self._stats["last_enrich_time"] = datetime.utcnow()
        
        return result
    
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
            enriched = self.enrich(event)
            results.append(enriched)
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get combined statistics from all enrichers.
        
        Returns:
            Dict[str, Any]: Combined statistics
        """
        stats = {
            "pipeline": self._stats.copy(),
        }
        
        for name, enricher in self.enrichers.items():
            stats[name] = enricher.stats
        
        return stats
    
    def enable_enricher(self, name: str) -> None:
        """
        Enable an enricher.
        
        Args:
            name: Name of the enricher to enable
        """
        if name in self.enrichers:
            self.enrichers[name].enabled = True
            self.logger.info(f"Enabled enricher: {name}")
    
    def disable_enricher(self, name: str) -> None:
        """
        Disable an enricher.
        
        Args:
            name: Name of the enricher to disable
        """
        if name in self.enrichers:
            self.enrichers[name].enabled = False
            self.logger.info(f"Disabled enricher: {name}")
    
    def is_enriched(self, event: Dict[str, Any]) -> bool:
        """
        Check if an event has been enriched.
        
        Args:
            event: Event to check
            
        Returns:
            bool: True if event has enrichment
        """
        return "enrichment_applied" in event and len(event["enrichment_applied"]) > 0