"""Integration client for Member 3 - AI Engine."""

import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime

from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import AttackEngineError


class Member3Client:
    """
    Client for integrating with Member 3 (AI Engine).
    
    Features:
    - Get AI predictions
    - Get anomaly scores
    - Get model status
    """
    
    def __init__(self):
        """Initialize the Member 3 client."""
        self.logger = get_logger("integrations.member3")
        self.base_url = getattr(settings, 'member3_url', 'http://localhost:8002')
        self.timeout = 30.0
    
    async def get_prediction(
        self,
        node_id: str,
        features: Optional[List[float]] = None,
        neighbors: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Get AI prediction for a node."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "node_id": node_id,
                    "include_explanation": True,
                }
                if features:
                    payload["features"] = features
                if neighbors:
                    payload["neighbors"] = neighbors
                
                response = await client.post(
                    f"{self.base_url}/api/v1/predict/single",
                    json=payload,
                )
                response.raise_for_status()
                
                result = response.json()
                self.logger.info(f"Got prediction for node {node_id}")
                return result
                
        except httpx.HTTPError as e:
            self.logger.error(f"Failed to get prediction: {e}")
            raise AttackEngineError(f"Member 3 connection failed: {e}")
    
    async def get_model_status(self) -> Dict[str, Any]:
        """Get Member 3 model status."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/model/status",
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            self.logger.error(f"Failed to get model status: {e}")
            return {"status": "unavailable"}