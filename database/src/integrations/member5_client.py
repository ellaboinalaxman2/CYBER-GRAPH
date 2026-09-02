"""Integration client for Member 5 - Attack Engine."""

import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime

from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import DatabaseError


class Member5Client:
    """
    Client for integrating with Member 5 (Attack Engine).
    
    Features:
    - Send attack paths
    - Get attack analysis
    - Get MITRE mapping
    """
    
    def __init__(self):
        """Initialize the Member 5 client."""
        self.logger = get_logger("integrations.member5")
        self.base_url = getattr(settings, 'MEMBER5_URL', 'http://localhost:8004')
        self.timeout = 30.0
    
    async def send_attack_path(
        self,
        source_id: str,
        target_id: str,
        path: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Send attack path to Member 5.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            path: Attack path data
            
        Returns:
            Dict[str, Any]: Analysis result
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "source_id": source_id,
                    "target_id": target_id,
                    "path": path,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                }
                
                response = await client.post(
                    f"{self.base_url}/api/v1/attack/path",
                    json=payload,
                )
                response.raise_for_status()
                
                result = response.json()
                self.logger.info(f"Sent attack path from {source_id} to {target_id}")
                return result
                
        except httpx.HTTPError as e:
            self.logger.error(f"Failed to send attack path to Member 5: {e}")
            raise DatabaseError(f"Member 5 connection failed: {e}")
    
    async def get_attack_analysis(self, incident_id: str) -> Dict[str, Any]:
        """
        Get attack analysis for an incident.
        
        Args:
            incident_id: Incident ID
            
        Returns:
            Dict[str, Any]: Attack analysis
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/attack/analysis/{incident_id}",
                )
                response.raise_for_status()
                
                result = response.json()
                self.logger.info(f"Got attack analysis for incident {incident_id}")
                return result
                
        except httpx.HTTPError as e:
            self.logger.error(f"Failed to get attack analysis from Member 5: {e}")
            return {"error": str(e)}
    
    async def get_mitre_mapping(self, technique_ids: List[str]) -> Dict[str, Any]:
        """
        Get MITRE ATT&CK mapping for techniques.
        
        Args:
            technique_ids: List of MITRE technique IDs
            
        Returns:
            Dict[str, Any]: MITRE mapping
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/attack/mitre",
                    json={"techniques": technique_ids},
                )
                response.raise_for_status()
                
                result = response.json()
                self.logger.info(f"Got MITRE mapping for {len(technique_ids)} techniques")
                return result
                
        except httpx.HTTPError as e:
            self.logger.error(f"Failed to get MITRE mapping from Member 5: {e}")
            return {"error": str(e)}