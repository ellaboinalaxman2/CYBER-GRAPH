"""Contextual enrichment."""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from src.enrichers.base import BaseEnricher


class ContextEnricher(BaseEnricher):
    """
    Enriches events with contextual information.
    
    Adds:
    - Event context (time of day, day of week)
    - Behavioral context
    - Historical context (if available)
    """
    
    def __init__(self):
        """Initialize context enricher."""
        super().__init__(enricher_name="context-enricher")
    
    def enrich(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich event with contextual information.
        
        Args:
            event: Event data to enrich
            
        Returns:
            Dict[str, Any]: Event with context enrichment
        """
        if not self.enabled:
            return event
        
        result = event.copy()
        enrichments_applied = []
        
        # Add temporal context
        timestamp = self._get_timestamp(event)
        if timestamp:
            context = self._get_temporal_context(timestamp)
            result["temporal_context"] = context
            enrichments_applied.append("temporal_context")
        
        # Add event type context
        event_type = self._safe_get(event, "event_type")
        if event_type:
            context = self._get_event_type_context(event_type)
            if context:
                result["event_type_context"] = context
                enrichments_applied.append("event_type_context")
        
        # Update metadata
        if enrichments_applied:
            if "enrichment_applied" not in result:
                result["enrichment_applied"] = []
            result["enrichment_applied"].extend(enrichments_applied)
        
        self._update_stats(success=True, enrichments_count=len(enrichments_applied))
        return result
    
    def _get_timestamp(self, event: Dict[str, Any]) -> Optional[datetime]:
        """Get timestamp from event."""
        timestamp = self._safe_get(event, "timestamp")
        if timestamp:
            if isinstance(timestamp, datetime):
                return timestamp
            if isinstance(timestamp, str):
                try:
                    return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except ValueError:
                    pass
        return None
    
    def _get_temporal_context(self, timestamp: datetime) -> Dict[str, Any]:
        """Get temporal context for a timestamp."""
        # Time of day
        hour = timestamp.hour
        if 5 <= hour < 12:
            time_of_day = "morning"
        elif 12 <= hour < 17:
            time_of_day = "afternoon"
        elif 17 <= hour < 21:
            time_of_day = "evening"
        else:
            time_of_day = "night"
        
        # Day of week
        day_of_week = timestamp.strftime("%A")
        is_weekend = day_of_week in ["Saturday", "Sunday"]
        
        # Business hours
        is_business_hours = 9 <= hour < 17 and not is_weekend
        
        return {
            "time_of_day": time_of_day,
            "day_of_week": day_of_week,
            "is_weekend": is_weekend,
            "is_business_hours": is_business_hours,
            "hour": hour,
            "minute": timestamp.minute,
        }
    
    def _get_event_type_context(self, event_type: str) -> Optional[Dict[str, Any]]:
        """Get context for event type."""
        contexts = {
            "LOGIN_FAILURE": {
                "description": "Authentication failure",
                "suspicious": True,
                "requires_investigation": True,
                "category": "authentication",
            },
            "LOGIN_SUCCESS": {
                "description": "Authentication success",
                "suspicious": False,
                "requires_investigation": False,
                "category": "authentication",
            },
            "FIREWALL_DENY": {
                "description": "Firewall blocked connection",
                "suspicious": True,
                "requires_investigation": True,
                "category": "network",
            },
            "FIREWALL_ALLOW": {
                "description": "Firewall allowed connection",
                "suspicious": False,
                "requires_investigation": False,
                "category": "network",
            },
            "NETWORK_CONNECTION": {
                "description": "Network connection established",
                "suspicious": False,
                "requires_investigation": False,
                "category": "network",
            },
            "ALERT": {
                "description": "Security alert triggered",
                "suspicious": True,
                "requires_investigation": True,
                "category": "security",
            },
        }
        
        return contexts.get(event_type)