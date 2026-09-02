"""Integration client for Member 6 - Blockchain."""

import httpx
from typing import Optional, Dict, Any
from datetime import datetime

from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import AttackEngineError


class Member6Client:
    """
    Client for integrating with Member 6 (Blockchain).
    
    Features:
    - Send critical alerts to blockchain
    - Verify blockchain records
    - Get blockchain status
    """
    
    def __init__(self):
        """Initialize the Member 6 client."""
        self.logger = get_logger("integrations.member6")
        self.base_url = getattr(settings, 'member6_url', 'http://localhost:8005')
        self.timeout = 30.0
    
    async def send_alert(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a critical alert to blockchain.
        
        Args:
            alert: Alert data
            
        Returns:
            Dict[str, Any]: Blockchain response
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Prepare data for blockchain
                blockchain_data = {
                    "alert_id": alert.get("alert_id"),
                    "timestamp": alert.get("timestamp"),
                    "severity": alert.get("severity"),
                    "risk_score": alert.get("risk_score"),
                    "attack_type": alert.get("attack_type"),
                    "hash": self._generate_hash(alert),
                }
                
                response = await client.post(
                    f"{self.base_url}/api/v1/blockchain/record",
                    json=blockchain_data,
                )
                response.raise_for_status()
                
                result = response.json()
                self.logger.info(f"Sent alert {alert.get('alert_id')} to blockchain")
                return result
                
        except httpx.HTTPError as e:
            self.logger.error(f"Failed to send alert to blockchain: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def verify_alert(self, alert_id: str) -> Dict[str, Any]:
        """
        Verify an alert on blockchain.
        
        Args:
            alert_id: Alert ID
            
        Returns:
            Dict[str, Any]: Verification result
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/blockchain/verify/{alert_id}",
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            self.logger.error(f"Failed to verify alert: {e}")
            return {"verified": False, "error": str(e)}
    
    async def get_status(self) -> Dict[str, Any]:
        """Get blockchain status."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/blockchain/status",
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            self.logger.error(f"Failed to get blockchain status: {e}")
            return {"status": "unavailable"}
    
    def _generate_hash(self, alert: Dict[str, Any]) -> str:
        """Generate a simple hash for the alert."""
        import hashlib
        import json
        
        content = json.dumps({
            "alert_id": alert.get("alert_id"),
            "timestamp": alert.get("timestamp"),
            "severity": alert.get("severity"),
            "risk_score": alert.get("risk_score"),
            "attack_type": alert.get("attack_type"),
        }, sort_keys=True)
        
        return hashlib.sha256(content.encode()).hexdigest()