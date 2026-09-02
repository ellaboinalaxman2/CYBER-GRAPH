"""Attack Engine client for Member 3 - AI Engine."""

import requests
from typing import Optional, Dict, Any, List
from datetime import datetime

from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import InferenceError


class AttackEngineClient:
    """
    Client for Member 5 - Attack Engine.
    
    Features:
    - Send predictions to Attack Engine
    - Get attack paths
    - Get risk scores
    """
    
    def __init__(self):
        """Initialize the attack engine client."""
        self.logger = get_logger("integrations.attack_engine")
        self.base_url = settings.attack_engine_url
    
    def send_prediction(
        self,
        node_id: str,
        prediction: str,
        anomaly_score: float,
        confidence: float,
        details: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Send prediction to Attack Engine.
        
        Args:
            node_id: Node identifier
            prediction: Predicted class
            anomaly_score: Anomaly score
            confidence: Confidence score
            details: Additional details
            
        Returns:
            bool: True if successful
        """
        try:
            payload = {
                "node_id": node_id,
                "prediction": prediction,
                "anomaly_score": anomaly_score,
                "confidence": confidence,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
            
            if details:
                payload["details"] = details
            
            response = requests.post(
                f"{self.base_url}/attack/predictions",
                json=payload,
                timeout=10,
            )
            response.raise_for_status()
            
            self.logger.info(f"Sent prediction for {node_id} to Attack Engine")
            return True
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to send prediction to Attack Engine: {e}")
            return False
    
    def get_attack_path(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Get attack path for a node.
        
        Args:
            node_id: Node identifier
            
        Returns:
            Optional[Dict[str, Any]]: Attack path
        """
        try:
            response = requests.get(
                f"{self.base_url}/attack/path/{node_id}",
                timeout=10,
            )
            response.raise_for_status()
            
            data = response.json()
            self.logger.info(f"Retrieved attack path for {node_id}")
            return data
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to get attack path: {e}")
            return None
    
    def get_risk_score(self, node_id: str) -> Optional[float]:
        """
        Get risk score for a node.
        
        Args:
            node_id: Node identifier
            
        Returns:
            Optional[float]: Risk score
        """
        try:
            response = requests.get(
                f"{self.base_url}/attack/risk/{node_id}",
                timeout=10,
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("risk_score", 0.0)
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to get risk score: {e}")
            return None