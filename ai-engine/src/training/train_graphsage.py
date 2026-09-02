"""GraphSAGE training for Member 3 - AI Engine."""

import torch
import torch.nn as nn
from typing import Optional, Dict, Any, Tuple
from pathlib import Path

from src.core.logging import get_logger
from src.core.config import settings
from src.models import ModelFactory
from src.training.trainer import Trainer, TrainingConfig
from src.training.loss import LossFactory, LossConfig
from src.training.optimizer import OptimizerFactory, OptimizerConfig
from src.training.scheduler import SchedulerFactory, SchedulerConfig
from src.training.early_stopping import EarlyStopping


class GraphSAGETrainer:
    """
    Specialized trainer for GraphSAGE models.
    
    Features:
    - Graph-specific data handling
    - Node classification training
    - Embedding visualization
    - Model versioning
    """
    
    def __init__(
        self,
        model: Optional[nn.Module] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the GraphSAGE trainer.
        
        Args:
            model: Pre-initialized model (optional)
            config: Training configuration (optional)
        """
        self.logger = get_logger("training.graphsage")
        self.config = config or self._default_config()
        
        # Create or use model
        if model is None:
            self.model = self._create_model()
        else:
            self.model = model
        
        # Create trainer
        self.trainer = Trainer(
            model=self.model,
            config=self._create_trainer_config(),
        )
        
        self.logger.info("GraphSAGE trainer initialized")
    
    def _default_config(self) -> Dict[str, Any]:
        """Default training configuration."""
        return {
            'in_channels': 128,
            'hidden_channels': 128,
            'out_channels': 64,
            'num_layers': 3,
            'num_classes': 2,
            'dropout': 0.2,
            'aggregator': 'mean',
            'max_epochs': 200,
            'learning_rate': 0.001,
            'weight_decay': 5e-4,
            'optimizer': 'adam',
            'scheduler': 'plateau',
            'loss': 'cross_entropy',
            'patience': 20,
            'device': 'cuda' if torch.cuda.is_available() else 'cpu',
            'save_dir': str(Path(settings.model_save_dir) / 'checkpoints'),
        }
    
    def _create_model(self) -> nn.Module:
        """Create GraphSAGE model."""
        return ModelFactory.create_default_classifier(
            in_channels=self.config['in_channels'],
            num_classes=self.config['num_classes'],
            hidden_channels=self.config['hidden_channels'],
            num_layers=self.config['num_layers'],
        )
    
    def _create_trainer_config(self) -> TrainingConfig:
        """Create trainer configuration."""
        return TrainingConfig(
            max_epochs=self.config['max_epochs'],
            learning_rate=self.config['learning_rate'],
            weight_decay=self.config['weight_decay'],
            optimizer=self.config['optimizer'],
            scheduler=self.config['scheduler'],
            loss=self.config['loss'],
            patience=self.config['patience'],
            device=self.config['device'],
            save_dir=self.config['save_dir'],
        )
    
    def train(
        self,
        data: torch_geometric.data.Data,  # noqa: F821
        train_mask: torch.Tensor,
        val_mask: Optional[torch.Tensor] = None,
        test_mask: Optional[torch.Tensor] = None,
    ) -> Dict[str, Any]:
        """
        Train the GraphSAGE model.
        
        Args:
            data: PyTorch Geometric Data object
            train_mask: Training node mask
            val_mask: Validation node mask (optional)
            test_mask: Test node mask (optional)
            
        Returns:
            Dict[str, Any]: Training results
        """
        self.logger.info("Starting GraphSAGE training...")
        
        # Prepare data for training
        train_data = self._prepare_batch(data, train_mask)
        
        if val_mask is not None:
            val_data = self._prepare_batch(data, val_mask)
        else:
            val_data = None
        
        # Train
        results = self.trainer.train(train_data, val_data)
        
        # Evaluate on test set
        if test_mask is not None:
            test_data = self._prepare_batch(data, test_mask)
            test_loss, test_metrics = self.trainer._validate_epoch(test_data)
            results['test_loss'] = test_loss
            results['test_metrics'] = test_metrics
        
        self.logger.info("GraphSAGE training complete!")
        return results
    
    def _prepare_batch(
        self,
        data: torch_geometric.data.Data,  # noqa: F821
        mask: torch.Tensor,
    ) -> Dict[str, Any]:
        """
        Prepare data for training/validation.
        
        Args:
            data: PyTorch Geometric Data object
            mask: Node mask
            
        Returns:
            Dict[str, Any]: Prepared batch
        """
        return {
            'x': data.x[mask],
            'edge_index': data.edge_index,
            'edge_attr': data.edge_attr if hasattr(data, 'edge_attr') else None,
            'y': data.y[mask],
        }
    
    def get_model(self) -> nn.Module:
        """Get the trained model."""
        return self.model
    
    def get_embeddings(
        self,
        data: torch_geometric.data.Data,  # noqa: F821
    ) -> torch.Tensor:
        """
        Get node embeddings.
        
        Args:
            data: PyTorch Geometric Data object
            
        Returns:
            torch.Tensor: Node embeddings
        """
        self.model.eval()
        with torch.no_grad():
            embeddings = self.model.get_embeddings(
                data.x,
                data.edge_index,
                data.edge_attr if hasattr(data, 'edge_attr') else None,
            )
        return embeddings
    
    def predict(
        self,
        data: torch_geometric.data.Data,  # noqa: F821
    ) -> torch.Tensor:
        """
        Make predictions.
        
        Args:
            data: PyTorch Geometric Data object
            
        Returns:
            torch.Tensor: Predictions
        """
        self.model.eval()
        with torch.no_grad():
            predictions = self.model.predict(
                data.x,
                data.edge_index,
                data.edge_attr if hasattr(data, 'edge_attr') else None,
            )
        return predictions
    
    def predict_proba(
        self,
        data: torch_geometric.data.Data,  # noqa: F821
    ) -> torch.Tensor:
        """
        Get prediction probabilities.
        
        Args:
            data: PyTorch Geometric Data object
            
        Returns:
            torch.Tensor: Prediction probabilities
        """
        self.model.eval()
        with torch.no_grad():
            proba = self.model.predict_proba(
                data.x,
                data.edge_index,
                data.edge_attr if hasattr(data, 'edge_attr') else None,
            )
        return proba