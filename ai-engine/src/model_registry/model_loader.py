"""Model loader for Member 3 - AI Engine."""

import torch
import torch.nn as nn
from typing import Optional, Dict, Any, Type
from pathlib import Path

from src.core.logging import get_logger
from src.core.exceptions import ModelNotFoundError
from src.models import ModelFactory
from src.model_registry.registry import ModelRegistry


class ModelLoader:
    """
    Loads models from registry or file system.
    
    Features:
    - Load from registry
    - Load from file
    - Load active model
    - Load specific version
    """
    
    def __init__(self, registry: Optional[ModelRegistry] = None):
        """
        Initialize the model loader.
        
        Args:
            registry: Model registry instance
        """
        self.logger = get_logger("model_registry.model_loader")
        self.registry = registry or ModelRegistry()
    
    def load_active_model(self, device: str = "cpu") -> nn.Module:
        """
        Load the active model from registry.
        
        Args:
            device: Device to load model on
            
        Returns:
            nn.Module: Loaded model
        """
        model_version = self.registry.get_model()  # Gets active model
        
        if model_version is None:
            self.logger.warning("No active model found in registry")
            return self._create_dummy_model()
        
        return self.load_from_file(model_version.path, device)
    
    def load_version(self, version: str, device: str = "cpu") -> nn.Module:
        """
        Load a specific model version from registry.
        
        Args:
            version: Version string
            device: Device to load model on
            
        Returns:
            nn.Module: Loaded model
        """
        model_version = self.registry.get_model(version)
        
        if model_version is None:
            raise ModelNotFoundError(f"Model version {version} not found in registry")
        
        return self.load_from_file(model_version.path, device)
    
    def load_from_file(self, model_path: str, device: str = "cpu") -> nn.Module:
        """
        Load model from file.
        
        Args:
            model_path: Path to model file
            device: Device to load model on
            
        Returns:
            nn.Module: Loaded model
        """
        if not Path(model_path).exists():
            self.logger.warning(f"Model file not found: {model_path}")
            return self._create_dummy_model()
        
        try:
            checkpoint = torch.load(model_path, map_location=device)
            
            # Get model config
            config = checkpoint.get('config', {})
            in_channels = config.get('in_channels', 16)
            hidden_channels = config.get('hidden_channels', 64)
            out_channels = config.get('out_channels', 2)
            num_layers = config.get('num_layers', 3)
            
            # Create model
            model = ModelFactory.create_default_classifier(
                in_channels=in_channels,
                num_classes=out_channels,
                hidden_channels=hidden_channels,
                num_layers=num_layers,
            )
            
            # Load state dict
            model.load_state_dict(checkpoint['model_state_dict'])
            model.to(device)
            model.eval()
            
            self.logger.info(f"Loaded model from {model_path}")
            return model
            
        except Exception as e:
            self.logger.error(f"Failed to load model from {model_path}: {e}")
            return self._create_dummy_model()
    
    def _create_dummy_model(self) -> nn.Module:
        """Create a dummy model for testing."""
        import torch.nn as nn
        import torch.nn.functional as F
        
        class DummyModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.linear = nn.Linear(16, 2)
            
            def forward(self, x, edge_index=None):
                return self.linear(x)
            
            def predict(self, x, edge_index=None):
                logits = self.forward(x, edge_index)
                return logits.argmax(dim=1)
            
            def predict_proba(self, x, edge_index=None):
                logits = self.forward(x, edge_index)
                return F.softmax(logits, dim=1)
            
            def get_embeddings(self, x, edge_index=None):
                return self.forward(x, edge_index)
            
            def count_parameters(self):
                return sum(p.numel() for p in self.parameters() if p.requires_grad)
        
        self.logger.warning("Using dummy model")
        return DummyModel()
    
    def load_for_inference(self, model_path: Optional[str] = None, device: str = "cpu") -> nn.Module:
        """
        Load model for inference.
        
        Args:
            model_path: Path to model file (optional)
            device: Device to load model on
            
        Returns:
            nn.Module: Loaded model
        """
        if model_path:
            return self.load_from_file(model_path, device)
        else:
            return self.load_active_model(device)