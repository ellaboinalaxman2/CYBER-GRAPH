"""Model factory for creating GraphSAGE models."""

from typing import Optional, Dict, Any, Type, List  # Add List here
import torch
import torch.nn as nn

from src.core.logging import get_logger
from src.models.graphsage import GraphSAGE, GraphSAGEConfig
from src.models.classifier import NodeClassifier, BinaryNodeClassifier


class ModelFactory:
    """
    Factory for creating GraphSAGE models.
    
    Features:
    - Create models with different configurations
    - Load models from checkpoints
    - Model registration
    """
    
    _registry = {
        'graphsage': GraphSAGE,
        'node_classifier': NodeClassifier,
        'binary_classifier': BinaryNodeClassifier,
    }
    
    def __init__(self):
        """Initialize the model factory."""
        self.logger = get_logger("models.model_factory")
    
    @classmethod
    def register(cls, name: str, model_class: Type[nn.Module]):
        """
        Register a model class.
        
        Args:
            name: Model name
            model_class: Model class
        """
        cls._registry[name] = model_class
    
    @classmethod
    def create(
        cls,
        model_type: str,
        config: Dict[str, Any],
        **kwargs,
    ) -> nn.Module:
        """
        Create a model.
        
        Args:
            model_type: Type of model to create
            config: Model configuration
            **kwargs: Additional arguments
            
        Returns:
            nn.Module: Created model
        """
        if model_type not in cls._registry:
            raise ValueError(f"Unknown model type: {model_type}. Available: {list(cls._registry.keys())}")
        
        model_class = cls._registry[model_type]
        
        if model_type == 'graphsage':
            config_obj = GraphSAGEConfig(**config)
            return model_class(config_obj)
        else:
            return model_class(**config, **kwargs)
    
    @classmethod
    def create_default_graphsage(
        cls,
        in_channels: int,
        num_classes: int = 2,
        hidden_channels: int = 128,
        num_layers: int = 3,
    ) -> GraphSAGE:
        """
        Create a default GraphSAGE model.
        
        Args:
            in_channels: Input feature dimension
            num_classes: Number of output classes
            hidden_channels: Hidden layer dimension
            num_layers: Number of layers
            
        Returns:
            GraphSAGE: Default GraphSAGE model
        """
        config = GraphSAGEConfig(
            in_channels=in_channels,
            hidden_channels=hidden_channels,
            out_channels=hidden_channels // 2,
            num_layers=num_layers,
            num_classes=num_classes,
        )
        return GraphSAGE(config)
    
    @classmethod
    def create_default_classifier(
        cls,
        in_channels: int,
        num_classes: int = 2,
        hidden_channels: int = 128,
        num_layers: int = 3,
    ) -> NodeClassifier:
        """
        Create a default node classifier.
        
        Args:
            in_channels: Input feature dimension
            num_classes: Number of output classes
            hidden_channels: Hidden layer dimension
            num_layers: Number of layers
            
        Returns:
            NodeClassifier: Default node classifier
        """
        return NodeClassifier(
            in_channels=in_channels,
            hidden_channels=hidden_channels,
            out_channels=hidden_channels // 2,
            num_layers=num_layers,
            num_classes=num_classes,
        )
    
    @classmethod
    def load_from_checkpoint(
        cls,
        checkpoint_path: str,
        model_type: Optional[str] = None,
        device: str = 'cpu',
    ) -> nn.Module:
        """
        Load a model from a checkpoint.
        
        Args:
            checkpoint_path: Path to checkpoint file
            model_type: Type of model (if None, inferred from checkpoint)
            device: Device to load model to
            
        Returns:
            nn.Module: Loaded model
        """
        checkpoint = torch.load(checkpoint_path, map_location=device)
        
        # Extract model type from checkpoint if not provided
        if model_type is None:
            model_type = checkpoint.get('model_type', 'graphsage')
        
        # Extract config
        config = checkpoint.get('config', {})
        
        # Create model
        model = cls.create(model_type, config)
        
        # Load state dict
        model.load_state_dict(checkpoint['model_state_dict'])
        
        logger = get_logger("models.model_factory")
        logger.info(f"Loaded model from {checkpoint_path}")
        
        return model
    
    @classmethod
    def get_available_models(cls) -> List[str]:
        """Get list of available model types."""
        return list(cls._registry.keys())