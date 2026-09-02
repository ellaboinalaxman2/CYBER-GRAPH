"""Integration client for Member 3 - AI Engine."""

import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime

from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import DatabaseError


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
        self.base_url = getattr(settings, 'MEMBER3_URL', 'http://localhost:8002')
        self.timeout = 30.0
    
    async def get_prediction(
        self,
        node_id: str,
        features: Optional[List[float]] = None,
        neighbors: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Get AI prediction for a node.
        
        Args:
            node_id: Node ID
            features: Node features
            neighbors: Neighbor node IDs
            
        Returns:
            Dict[str, Any]: Prediction result
        """
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
            self.logger.error(f"Failed to get prediction from Member 3: {e}")
            raise DatabaseError(f"Member 3 connection failed: {e}")
    
    async def get_anomaly_score(self, node_id: str) -> Dict[str, Any]:
        """
        Get anomaly score for a node.
        
        Args:
            node_id: Node ID
            
        Returns:
            Dict[str, Any]: Anomaly score result
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/predict/single",
                    json={"node_id": node_id},
                )
                response.raise_for_status()
                
                result = response.json()
                self.logger.info(f"Got anomaly score for node {node_id}")
                return result
                
        except httpx.HTTPError as e:
            self.logger.error(f"Failed to get anomaly score from Member 3: {e}")
            return {"error": str(e)}
    
    async def get_model_status(self) -> Dict[str, Any]:
        """
        Get Member 3 model status.
        
        Returns:
            Dict[str, Any]: Model status
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/model/status",
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            self.logger.error(f"Failed to get Member 3 model status: {e}")
            return {"status": "unavailable"}