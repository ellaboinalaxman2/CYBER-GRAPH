"""Node classifier for Member 3 - AI Engine."""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Dict, Any, List

from src.models.graphsage import GraphSAGE, GraphSAGEConfig
from src.core.logging import get_logger


class NodeClassifier(nn.Module):
    """
    Node classifier using GraphSAGE.
    
    Wraps GraphSAGE with additional classification capabilities:
    - Multi-class classification
    - Binary classification
    - Probability calibration
    """
    
    def __init__(
        self,
        in_channels: int,
        hidden_channels: int = 128,
        out_channels: int = 64,
        num_layers: int = 3,
        num_classes: int = 2,
        dropout: float = 0.2,
        aggregator: str = 'mean',
    ):
        """
        Initialize the node classifier.
        
        Args:
            in_channels: Input feature dimension
            hidden_channels: Hidden layer dimension
            out_channels: Output embedding dimension
            num_layers: Number of SAGEConv layers
            num_classes: Number of output classes
            dropout: Dropout probability
            aggregator: Aggregation method
        """
        super().__init__()
        
        self.logger = get_logger("models.classifier")
        
        # Create GraphSAGE config
        config = GraphSAGEConfig(
            in_channels=in_channels,
            hidden_channels=hidden_channels,
            out_channels=out_channels,
            num_layers=num_layers,
            dropout=dropout,
            aggregator=aggregator,
            num_classes=num_classes,
        )
        
        self.graphsage = GraphSAGE(config)
        self.num_classes = num_classes
        
        self.logger.info(f"Initialized NodeClassifier with {num_classes} classes")
    
    def forward(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        edge_attr: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            x: Node features
            edge_index: Edge indices
            edge_attr: Edge features (optional)
            
        Returns:
            torch.Tensor: Logits
        """
        return self.graphsage(x, edge_index, edge_attr)
    
    def predict(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        edge_attr: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Get predictions.
        
        Args:
            x: Node features
            edge_index: Edge indices
            edge_attr: Edge features (optional)
            
        Returns:
            torch.Tensor: Predictions
        """
        logits = self.forward(x, edge_index, edge_attr)
        return logits.argmax(dim=1)
    
    def predict_proba(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        edge_attr: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Get prediction probabilities.
        
        Args:
            x: Node features
            edge_index: Edge indices
            edge_attr: Edge features (optional)
            
        Returns:
            torch.Tensor: Prediction probabilities
        """
        logits = self.forward(x, edge_index, edge_attr)
        return F.softmax(logits, dim=1)
    
    def get_embeddings(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        edge_attr: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Get node embeddings.
        
        Args:
            x: Node features
            edge_index: Edge indices
            edge_attr: Edge features (optional)
            
        Returns:
            torch.Tensor: Node embeddings
        """
        return self.graphsage.get_embeddings(x, edge_index, edge_attr)
    
    def get_config(self) -> Dict[str, Any]:
        """Get model configuration."""
        return self.graphsage.get_config()
    
    def summary(self) -> str:
        """Get model summary."""
        return self.graphsage.summary()


class BinaryNodeClassifier(NodeClassifier):
    """
    Binary node classifier.
    
    Specialized version for binary classification (Normal/Attack).
    """
    
    def __init__(
        self,
        in_channels: int,
        hidden_channels: int = 128,
        out_channels: int = 64,
        num_layers: int = 3,
        dropout: float = 0.2,
        aggregator: str = 'mean',
    ):
        """
        Initialize the binary node classifier.
        
        Args:
            in_channels: Input feature dimension
            hidden_channels: Hidden layer dimension
            out_channels: Output embedding dimension
            num_layers: Number of SAGEConv layers
            dropout: Dropout probability
            aggregator: Aggregation method
        """
        super().__init__(
            in_channels=in_channels,
            hidden_channels=hidden_channels,
            out_channels=out_channels,
            num_layers=num_layers,
            num_classes=2,
            dropout=dropout,
            aggregator=aggregator,
        )
        
        self.logger.info("Initialized BinaryNodeClassifier")
    
    def predict_proba_positive(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        edge_attr: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Get probability of positive class (Attack).
        
        Args:
            x: Node features
            edge_index: Edge indices
            edge_attr: Edge features (optional)
            
        Returns:
            torch.Tensor: Probability of positive class
        """
        proba = self.predict_proba(x, edge_index, edge_attr)
        return proba[:, 1]
    
    def predict_anomaly_score(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        edge_attr: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Get anomaly score (0-1).
        
        Args:
            x: Node features
            edge_index: Edge indices
            edge_attr: Edge features (optional)
            
        Returns:
            torch.Tensor: Anomaly scores
        """
        return self.predict_proba_positive(x, edge_index, edge_attr)