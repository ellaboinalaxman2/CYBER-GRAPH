"""GraphSAGE model for Member 3 - AI Engine."""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass

from src.models.layers import SAGEConv, GraphSAGELayer
from src.core.logging import get_logger


@dataclass
class GraphSAGEConfig:
    """Configuration for GraphSAGE model."""
    
    in_channels: int
    hidden_channels: int = 128
    out_channels: int = 64
    num_layers: int = 3
    dropout: float = 0.2
    aggregator: str = 'mean'
    num_classes: int = 2
    use_edge_attr: bool = False
    edge_channels: int = 8
    normalize: bool = True


class GraphSAGE(nn.Module):
    """
    GraphSAGE model for node classification.
    
    Implements the GraphSAGE architecture with:
    - Multiple SAGEConv layers
    - Skip connections
    - Dropout regularization
    - Batch normalization
    """
    
    def __init__(self, config: GraphSAGEConfig):
        """
        Initialize the GraphSAGE model.
        
        Args:
            config: Model configuration
        """
        super().__init__()
        
        self.logger = get_logger("models.graphsage")
        self.config = config
        self.num_layers = config.num_layers
        
        # Input layer
        self.input_layer = nn.Linear(config.in_channels, config.hidden_channels)
        
        # SAGEConv layers
        self.convs = nn.ModuleList()
        in_channels = config.hidden_channels
        
        for i in range(config.num_layers):
            out_channels = config.hidden_channels if i < config.num_layers - 1 else config.out_channels
            self.convs.append(
                SAGEConv(
                    in_channels,
                    out_channels,
                    aggregator=config.aggregator,
                    normalize=config.normalize,
                    dropout=config.dropout,
                )
            )
            in_channels = out_channels
        
        # Output layer
        self.classifier = nn.Linear(config.out_channels, config.num_classes)
        
        # Dropout
        self.dropout = nn.Dropout(config.dropout)
        
        self._reset_parameters()
        self.logger.info(f"Initialized GraphSAGE with {self.num_layers} layers")
    
    def _reset_parameters(self):
        """Reset model parameters."""
        # Parameters are reset in each layer
        pass
    
    def forward(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        edge_attr: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            x: Node features [num_nodes, in_channels]
            edge_index: Edge indices [2, num_edges]
            edge_attr: Edge features [num_edges, edge_channels] (optional)
            
        Returns:
            torch.Tensor: Node logits [num_nodes, num_classes]
        """
        # Input projection
        x = self.input_layer(x)
        x = F.relu(x)
        x = self.dropout(x)
        
        # SAGEConv layers
        for i, conv in enumerate(self.convs):
            x = conv(x, edge_index)
            if i < len(self.convs) - 1:
                x = F.relu(x)
                x = self.dropout(x)
        
        # Classification
        x = self.classifier(x)
        
        return x
    
    def get_embeddings(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        edge_attr: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Get node embeddings (without classification).
        
        Args:
            x: Node features
            edge_index: Edge indices
            edge_attr: Edge features (optional)
            
        Returns:
            torch.Tensor: Node embeddings
        """
        # Input projection
        x = self.input_layer(x)
        x = F.relu(x)
        
        # SAGEConv layers
        for i, conv in enumerate(self.convs):
            x = conv(x, edge_index)
            if i < len(self.convs) - 1:
                x = F.relu(x)
        
        return x
    
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
    
    def get_config(self) -> Dict[str, Any]:
        """Get model configuration."""
        return {
            "in_channels": self.config.in_channels,
            "hidden_channels": self.config.hidden_channels,
            "out_channels": self.config.out_channels,
            "num_layers": self.config.num_layers,
            "dropout": self.config.dropout,
            "aggregator": self.config.aggregator,
            "num_classes": self.config.num_classes,
            "use_edge_attr": self.config.use_edge_attr,
            "edge_channels": self.config.edge_channels,
            "normalize": self.config.normalize,
        }
    
    def count_parameters(self) -> int:
        """Count the number of trainable parameters."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)
    
    def summary(self) -> str:
        """Get model summary."""
        return f"""
        GraphSAGE Model Summary
        ========================
        Input Channels: {self.config.in_channels}
        Hidden Channels: {self.config.hidden_channels}
        Output Channels: {self.config.out_channels}
        Number of Layers: {self.config.num_layers}
        Dropout: {self.config.dropout}
        Aggregator: {self.config.aggregator}
        Number of Classes: {self.config.num_classes}
        Total Parameters: {self.count_parameters():,}
        """