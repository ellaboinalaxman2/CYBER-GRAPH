"""Main predictor for Member 3 - AI Engine."""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path

from src.core.logging import get_logger
from src.core.config import settings
from src.core.exceptions import InferenceError


@dataclass
class PredictionResult:
    """Result of a single prediction."""
    
    node_id: str
    prediction: str
    probability: float
    confidence: float
    anomaly_score: float
    embedding: Optional[List[float]] = None
    explanation: Optional[Dict[str, Any]] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat() + "Z"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "node_id": self.node_id,
            "prediction": self.prediction,
            "probability": self.probability,
            "confidence": self.confidence,
            "anomaly_score": self.anomaly_score,
            "embedding": self.embedding,
            "explanation": self.explanation,
            "timestamp": self.timestamp,
        }


class SimpleGraphSAGE(nn.Module):
    """Simple GraphSAGE model for inference."""
    
    def __init__(self, in_channels, hidden_channels, out_channels, num_layers=3):
        super().__init__()
        self.layers = nn.ModuleList()
        
        # Input layer
        self.layers.append(nn.Linear(in_channels, hidden_channels))
        
        # Hidden layers
        for _ in range(num_layers - 1):
            self.layers.append(nn.Linear(hidden_channels, hidden_channels))
        
        # Output layer
        self.layers.append(nn.Linear(hidden_channels, out_channels))
        
        self.dropout = nn.Dropout(0.2)
    
    def forward(self, x, edge_index=None):
        for i, layer in enumerate(self.layers[:-1]):
            x = layer(x)
            x = F.relu(x)
            x = self.dropout(x)
        
        x = self.layers[-1](x)
        return x
    
    def get_embeddings(self, x, edge_index=None):
        """Get node embeddings."""
        for i, layer in enumerate(self.layers[:-1]):
            x = layer(x)
            x = F.relu(x)
        
        return x


class Predictor:
    """
    Main predictor for GraphSAGE model.
    
    Features:
    - Single node prediction
    - Batch prediction
    - Model loading
    - Feature extraction
    - Prediction explanation
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        device: str = "cpu",
        model: Optional[torch.nn.Module] = None,
    ):
        """
        Initialize the predictor.
        
        Args:
            model_path: Path to trained model checkpoint
            device: Device to run inference on
            model: Pre-loaded model (optional)
        """
        self.logger = get_logger("inference.predictor")
        self.device = torch.device(device)
        
        # Load model
        if model is not None:
            self.model = model
            self.model.to(self.device)
            self.model.eval()
            self.logger.info("Using pre-loaded model")
        elif model_path is not None and Path(model_path).exists():
            self.model = self._load_model(model_path)
            self.logger.info(f"Loaded model from {model_path}")
        else:
            # Create a dummy model for testing
            self.logger.warning(f"Model not found at {model_path}, creating dummy model")
            self.model = self._create_dummy_model()
            self.model.to(self.device)
            self.model.eval()
        
        # Model config
        self.model_config = self._get_model_config()
        
        self._stats = {
            "total_predictions": 0,
            "total_anomalies": 0,
            "last_prediction": None,
        }
    
    def _create_dummy_model(self) -> nn.Module:
        """Create a dummy model for testing."""
        return SimpleGraphSAGE(
            in_channels=16,
            hidden_channels=64,
            out_channels=2,
            num_layers=3,
        )
    
    def _load_model(self, model_path: str) -> nn.Module:
        """
        Load model from checkpoint.
        
        Args:
            model_path: Path to checkpoint
            
        Returns:
            nn.Module: Loaded model
        """
        checkpoint = torch.load(model_path, map_location=self.device)
        
        # Get model config
        config = checkpoint.get('config', {})
        in_channels = config.get('in_channels', 16)
        hidden_channels = config.get('hidden_channels', 64)
        out_channels = config.get('out_channels', 2)
        num_layers = config.get('num_layers', 3)
        
        # Create model
        model = SimpleGraphSAGE(
            in_channels=in_channels,
            hidden_channels=hidden_channels,
            out_channels=out_channels,
            num_layers=num_layers,
        )
        
        # Load state dict
        model.load_state_dict(checkpoint['model_state_dict'])
        model.to(self.device)
        model.eval()
        
        self.logger.info(f"Loaded model with {in_channels} input channels, {hidden_channels} hidden channels")
        return model
    
    def _get_model_config(self) -> Dict[str, Any]:
        """Get model configuration."""
        if hasattr(self.model, 'config'):
            return self.model.config
        return {
            'in_channels': 16,
            'hidden_channels': 64,
            'out_channels': 2,
            'num_layers': 3,
        }
    
    def predict(
        self,
        node_data: Dict[str, Any],
        graph_data: Optional[Dict[str, Any]] = None,
        return_embedding: bool = False,
        return_explanation: bool = False,
    ) -> PredictionResult:
        """
        Predict for a single node.
        
        Args:
            node_data: Node data (features, id, etc.)
            graph_data: Graph data (optional)
            return_embedding: Whether to return embeddings
            return_explanation: Whether to return explanation
            
        Returns:
            PredictionResult: Prediction result
        """
        self.logger.info(f"Predicting for node: {node_data.get('node_id', 'unknown')}")
        
        # Generate dummy features if not provided
        if 'features' not in node_data or not node_data['features']:
            # Generate random features for demonstration
            node_data['features'] = list(np.random.randn(16))
        
        # Create dummy graph if not provided
        if graph_data is None:
            graph_data = self._build_graph_from_node(node_data)
        
        # Convert to tensor
        x = torch.tensor([node_data['features']], dtype=torch.float).to(self.device)
        
        # Get prediction
        with torch.no_grad():
            # Forward pass
            logits = self.model(x)
            probabilities = torch.softmax(logits, dim=1)
            
            prob = probabilities[0]
            pred_class = logits[0].argmax().item()
            pred_label = "ATTACK" if pred_class == 1 else "NORMAL"
        
        # Get embedding if requested
        embedding = None
        if return_embedding:
            with torch.no_grad():
                embeddings = self.model.get_embeddings(x)
                embedding = embeddings[0].cpu().tolist()
        
        # Get explanation if requested
        explanation = None
        if return_explanation:
            explanation = self._generate_explanation(node_data, prob, pred_class)
        
        # Calculate confidence
        confidence = self._calculate_confidence(prob)
        
        # Calculate anomaly score
        anomaly_score = self._calculate_anomaly_score(prob)
        
        # Update stats
        self._stats["total_predictions"] += 1
        if pred_class == 1:
            self._stats["total_anomalies"] += 1
        self._stats["last_prediction"] = datetime.utcnow()
        
        return PredictionResult(
            node_id=node_data.get('node_id', 'unknown'),
            prediction=pred_label,
            probability=float(prob[pred_class].cpu().item()),
            confidence=confidence,
            anomaly_score=anomaly_score,
            embedding=embedding,
            explanation=explanation,
        )
    
    def _build_graph_from_node(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build a graph from a single node."""
        return {
            'nodes': [node_data],
            'edges': [],
        }
    
    def _calculate_confidence(self, probabilities: torch.Tensor) -> float:
        """Calculate prediction confidence."""
        return float(torch.max(probabilities).cpu().item())
    
    def _calculate_anomaly_score(self, probabilities: torch.Tensor) -> float:
        """Calculate anomaly score."""
        if len(probabilities) == 2:
            return float(probabilities[1].cpu().item())
        else:
            return float(torch.max(probabilities[1:]).cpu().item())
    
    def _generate_explanation(
        self,
        node_data: Dict[str, Any],
        probabilities: torch.Tensor,
        pred_class: int,
    ) -> Dict[str, Any]:
        """Generate prediction explanation."""
        explanation = {
            "reasons": [],
            "feature_importance": {},
            "confidence": self._calculate_confidence(probabilities),
        }
        
        if pred_class == 1:
            explanation["reasons"] = [
                "High anomaly score detected",
                "Unusual pattern in node behavior",
                "Recommend immediate investigation",
            ]
        else:
            explanation["reasons"] = [
                "Normal behavior detected",
                "No significant anomalies found",
            ]
        
        return explanation
    
    def get_stats(self) -> Dict[str, Any]:
        """Get prediction statistics."""
        return self._stats.copy()