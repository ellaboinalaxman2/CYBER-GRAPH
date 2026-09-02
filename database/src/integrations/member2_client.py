"""Integration client for Member 2 - Ingestion Engine."""

import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime

from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import DatabaseError


class Member2Client:
    """
    Client for integrating with Member 2 (Ingestion Engine).
    
    Features:
    - Get clean security events
    - Get event statistics
    - Subscribe to event stream
    """
    
    def __init__(self):
        """Initialize the Member 2 client."""
        self.logger = get_logger("integrations.member2")
        self.base_url = getattr(settings, 'MEMBER2_URL', 'http://localhost:8001')
        self.timeout = 30.0
    
    async def get_events(
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
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {"limit": limit}
                if source_type:
                    params["source_type"] = source_type
                if start_time:
                    params["start_time"] = start_time
                if end_time:
                    params["end_time"] = end_time
                
                response = await client.get(
                    f"{self.base_url}/api/v1/ingestion/events",
                    params=params,
                )
                response.raise_for_status()
                
                data = response.json()
                events = data.get("events", []) if isinstance(data, dict) else data
                
                self.logger.info(f"Retrieved {len(events)} events from Member 2")
                return events
                
        except httpx.HTTPError as e:
            self.logger.error(f"Failed to get events from Member 2: {e}")
            raise DatabaseError(f"Member 2 connection failed: {e}")
    
    async def get_sources(self) -> Dict[str, Any]:
        """
        Get available data sources from Member 2.
        
        Returns:
            Dict[str, Any]: Available sources
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/ingestion/sources",
                )
                response.raise_for_status()
                
                data = response.json()
                self.logger.info("Retrieved sources from Member 2")
                return data
                
        except httpx.HTTPError as e:
            self.logger.error(f"Failed to get sources from Member 2: {e}")
            return {"sources": {}, "total": 0}
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get Member 2 status.
        
        Returns:
            Dict[str, Any]: Status
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/ingestion/status",
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            self.logger.error(f"Failed to get Member 2 status: {e}")
            return {"status": "unavailable"}