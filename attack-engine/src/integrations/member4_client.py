"""Integration client for Member 4 - Database Engine."""

import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime

from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import AttackEngineError


class Member4Client:
    """
    Client for integrating with Member 4 (Database Engine).
    
    Features:
    - Get events from MongoDB
    - Get graph from Neo4j
    - Store alerts and incidents
    """
    
    def __init__(self):
        """Initialize the Member 4 client."""
        self.logger = get_logger("integrations.member4")
        self.base_url = getattr(settings, 'member4_url', 'http://localhost:8003')
        self.timeout = 30.0
    
    async def get_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get events from Member 4."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/events/",
                    params={"limit": limit},
                )
                response.raise_for_status()
                
                data = response.json()
                events = data.get("events", [])
                self.logger.info(f"Retrieved {len(events)} events from Member 4")
                return events
                
        except httpx.HTTPError as e:
            self.logger.error(f"Failed to get events: {e}")
            raise AttackEngineError(f"Member 4 connection failed: {e}")
    
    async def get_graph(self) -> Dict[str, Any]:
        """Get graph from Member 4."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/graph/statistics",
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            self.logger.error(f"Failed to get graph: {e}")
            return {}
    
    async def store_alert(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """Store an alert in Member 4."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/alerts/",
                    json=alert,
                )
                response.raise_for_status()
                self.logger.info(f"Stored alert {alert.get('alert_id')} in Member 4")
                return response.json()
        except httpx.HTTPError as e:
            self.logger.error(f"Failed to store alert: {e}")
            raise AttackEngineError(f"Failed to store alert: {e}")
    
    async def store_incident(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """Store an incident in Member 4."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/incidents/",
                    json=incident,
                )
                response.raise_for_status()
                self.logger.info(f"Stored incident {incident.get('incident_id')} in Member 4")
                return response.json()
        except httpx.HTTPError as e:
            self.logger.error(f"Failed to store incident: {e}")
            raise AttackEngineError(f"Failed to store incident: {e}")