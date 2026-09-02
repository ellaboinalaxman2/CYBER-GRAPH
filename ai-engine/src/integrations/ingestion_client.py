"""Ingestion client for Member 3 - AI Engine."""

import requests
from typing import Optional, Dict, Any, List
from datetime import datetime

from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import DataLoaderError


class IngestionClient:
    """
    Client for Member 2 - Ingestion Engine.
    
    Features:
    - Get clean events
    - Get event statistics
    - Subscribe to event stream
    """
    
    def __init__(self):
        """Initialize the ingestion client."""
        self.logger = get_logger("integrations.ingestion")
        self.base_url = settings.ingestion_api_url
    
    def get_events(
        self,
        limit: int = 100,
        source_type: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get events from Member 2.
        
        Args:
            limit: Maximum number of events
            source_type: Filter by source type
            start_time: Start time filter
            end_time: End time filter
            
        Returns:
            List[Dict[str, Any]]: Events
        """
        try:
            params = {"limit": limit}
            
            if source_type:
                params["source_type"] = source_type
            if start_time:
                params["start_time"] = start_time
            if end_time:
                params["end_time"] = end_time
            
            response = requests.get(
                f"{self.base_url}/ingestion/events",
                params=params,
                timeout=10,
            )
            response.raise_for_status()
            
            data = response.json()
            events = data.get("events", []) if isinstance(data, dict) else data
            
            self.logger.info(f"Retrieved {len(events)} events from Member 2")
            return events
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to get events from Member 2: {e}")
            raise DataLoaderError(f"Event retrieval failed: {e}")
    
    def get_sources(self) -> Dict[str, Any]:
        """
        Get available data sources.
        
        Returns:
            Dict[str, Any]: Available sources
        """
        try:
            response = requests.get(
                f"{self.base_url}/ingestion/sources",
                timeout=10,
            )
            response.raise_for_status()
            
            data = response.json()
            self.logger.info("Retrieved sources from Member 2")
            return data
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to get sources: {e}")
            return {"sources": {}, "total": 0}
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get ingestion status.
        
        Returns:
            Dict[str, Any]: Status
        """
        try:
            response = requests.get(
                f"{self.base_url}/ingestion/status",
                timeout=10,
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to get status: {e}")
            return {"pipeline_status": "unknown"}