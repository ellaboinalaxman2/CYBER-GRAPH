"""Base trainer for Member 3 - AI Engine."""

import torch
import torch.nn as nn
import torch.optim as optim
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
from datetime import datetime
import os
import json
from pathlib import Path
import numpy as np

from src.core.logging import get_logger
from src.core.config import settings
from src.training.loss import LossFactory, LossConfig
from src.training.optimizer import OptimizerFactory, OptimizerConfig
from src.training.scheduler import SchedulerFactory, SchedulerConfig
from src.training.early_stopping import EarlyStopping


@dataclass
class TrainingConfig:
    """Configuration for training."""
    
    max_epochs: int = 200
    batch_size: int = 32
    learning_rate: float = 0.001
    weight_decay: float = 5e-4
    optimizer: str = 'adam'
    scheduler: str = 'plateau'
    loss: str = 'cross_entropy'
    patience: int = 20
    device: str = 'cuda' if torch.cuda.is_available() else 'cpu'
    save_dir: str = './data/models/checkpoints'
    save_every: int = 10
    log_every: int = 10
    validation_every: int = 1
    grad_clip: Optional[float] = None
    accumulate_gradients: int = 1
    mixed_precision: bool = False
    seed: int = 42


class Trainer:
    """
    Base trainer for PyTorch models.
    
    Features:
    - Training loop
    - Validation
    - Checkpointing
    - Logging
    - Early stopping
    - Learning rate scheduling
    """
    
    def __init__(
        self,
        model: nn.Module,
        config: TrainingConfig,
        loss_fn: Optional[nn.Module] = None,
        optimizer: Optional[torch.optim.Optimizer] = None,
        scheduler: Optional[torch.optim.lr_scheduler._LRScheduler] = None,
    ):
        """
        Initialize the trainer.
        
        Args:
            model: Model to train
            config: Training configuration
            loss_fn: Loss function (optional)
            optimizer: Optimizer (optional)
            scheduler: Learning rate scheduler (optional)
        """
        self.logger = get_logger("training.trainer")
        self.model = model
        self.config = config
        self.device = torch.device(config.device)
        
        # Setup loss function
        if loss_fn is None:
            loss_config = LossConfig(name=config.loss)
            self.loss_fn = LossFactory.create(loss_config)
        else:
            self.loss_fn = loss_fn
        
        # Setup optimizer
        if optimizer is None:
            opt_config = OptimizerConfig(
                name=config.optimizer,
                learning_rate=config.learning_rate,
                weight_decay=config.weight_decay,
            )
            self.optimizer = OptimizerFactory.create(model, opt_config)
        else:
            self.optimizer = optimizer
        
        # Setup scheduler
        if scheduler is None:
            sch_config = SchedulerConfig(
                name=config.scheduler,
                patience=config.patience // 2,
                total_epochs=config.max_epochs,
                learning_rate=config.learning_rate,
            )
            self.scheduler = SchedulerFactory.create(self.optimizer, sch_config)
        else:
            self.scheduler = scheduler
        
        # Setup early stopping
        self.early_stopping = EarlyStopping(
            patience=config.patience,
            mode='min',
            verbose=True,
        )
        
        # Setup directories
        self.save_dir = Path(config.save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        # Move model to device
        self.model.to(self.device)
        
        # Training state
        self.current_epoch = 0
        self.best_loss = float('inf')
        self.training_history = {
            'epochs': [],
            'train_loss': [],
            'val_loss': [],
            'train_metrics': [],
            'val_metrics': [],
            'learning_rates': [],
        }
        
        self.logger.info(f"Trainer initialized on {self.device}")
        self.logger.info(f"Model has {model.count_parameters():,} parameters")
    
    def train(
        self,
        train_loader: torch.utils.data.DataLoader,
        val_loader: Optional[torch.utils.data.DataLoader] = None,
    ) -> Dict[str, Any]:
        """
        Train the model.
        
        Args:
            train_loader: Training data loader
            val_loader: Validation data loader (optional)
            
        Returns:
            Dict[str, Any]: Training results
        """
        self.logger.info("Starting training...")
        start_time = datetime.utcnow()
        
        for epoch in range(self.current_epoch, self.config.max_epochs):
            self.current_epoch = epoch
            
            # Train
            train_loss, train_metrics = self._train_epoch(train_loader)
            
            # Validate
            val_loss = None
            val_metrics = {}
            
            if val_loader and (epoch % self.config.validation_every == 0):
                val_loss, val_metrics = self._validate_epoch(val_loader)
            
            # Update scheduler
            if self.scheduler is not None:
                if isinstance(self.scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau):
                    self.scheduler.step(val_loss if val_loss is not None else train_loss)
                else:
                    self.scheduler.step()
            
            # Record history
            self.training_history['epochs'].append(epoch)
            self.training_history['train_loss'].append(train_loss)
            self.training_history['train_metrics'].append(train_metrics)
            
            if val_loss is not None:
                self.training_history['val_loss'].append(val_loss)
                self.training_history['val_metrics'].append(val_metrics)
            
            # Get current learning rate
            current_lr = self.optimizer.param_groups[0]['lr']
            self.training_history['learning_rates'].append(current_lr)
            
            # Log progress
            if epoch % self.config.log_every == 0:
                log_msg = f"Epoch {epoch}/{self.config.max_epochs} | "
                log_msg += f"Train Loss: {train_loss:.4f}"
                
                if val_loss is not None:
                    log_msg += f" | Val Loss: {val_loss:.4f}"
                
                log_msg += f" | LR: {current_lr:.6f}"
                self.logger.info(log_msg)
            
            # Save checkpoint
            if epoch % self.config.save_every == 0:
                self._save_checkpoint(epoch)
            
            # Early stopping
            if val_loss is not None:
                should_stop = self.early_stopping(
                    epoch,
                    val_loss,
                    self.model.state_dict(),
                    {'train_loss': train_loss, 'val_loss': val_loss},
                )
                
                if should_stop:
                    break
        
        # Restore best model
        if self.early_stopping.best_state is not None:
            self.model.load_state_dict(self.early_stopping.best_state)
            self.logger.info(f"Restored best model from epoch {self.early_stopping.best_epoch}")
        
        # Save final model
        self._save_checkpoint('final')
        
        # Calculate duration
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        results = {
            'status': 'completed',
            'epochs_trained': self.current_epoch + 1,
            'best_loss': self.early_stopping.best_score,
            'best_epoch': self.early_stopping.best_epoch,
            'training_duration_seconds': duration,
            'history': self.training_history,
            'early_stopping': self.early_stopping.get_summary(),
        }
        
        self.logger.info(f"Training completed in {duration:.2f}s")
        return results
    
    def _train_epoch(
        self,
        loader: torch.utils.data.DataLoader,
    ) -> tuple:
        """
        Train for one epoch.
        
        Args:
            loader: Data loader
            
        Returns:
            tuple: (average_loss, metrics)
        """
        self.model.train()
        total_loss = 0.0
        total_samples = 0
        all_predictions = []
        all_targets = []
        
        for batch_idx, batch in enumerate(loader):
            # Move batch to device
            batch = self._move_batch_to_device(batch)
            
            # Forward pass
            predictions = self.model(**batch)
            
            # Calculate loss
            loss = self.loss_fn(predictions, batch['y'])
            
            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()
            
            # Gradient clipping
            if self.config.grad_clip is not None:
                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(),
                    self.config.grad_clip,
                )
            
            self.optimizer.step()
            
            # Accumulate statistics
            total_loss += loss.item() * batch['y'].size(0)
            total_samples += batch['y'].size(0)
            
            # Store predictions for metrics
            all_predictions.append(predictions.detach().cpu())
            all_targets.append(batch['y'].detach().cpu())
        
        # Calculate metrics
        avg_loss = total_loss / total_samples
        metrics = self._calculate_metrics(
            torch.cat(all_predictions, dim=0),
            torch.cat(all_targets, dim=0),
        )
        
        return avg_loss, metrics
    
    def _validate_epoch(
        self,
        loader: torch.utils.data.DataLoader,
    ) -> tuple:
        """
        Validate for one epoch.
        
        Args:
            loader: Data loader
            
        Returns:
            tuple: (average_loss, metrics)
        """
        self.model.eval()
        total_loss = 0.0
        total_samples = 0
        all_predictions = []
        all_targets = []
        
        with torch.no_grad():
            for batch in loader:
                # Move batch to device
                batch = self._move_batch_to_device(batch)
                
                # Forward pass
                predictions = self.model(**batch)
                
                # Calculate loss
                loss = self.loss_fn(predictions, batch['y'])
                
                # Accumulate statistics
                total_loss += loss.item() * batch['y'].size(0)
                total_samples += batch['y'].size(0)
                
                # Store predictions
                all_predictions.append(predictions.detach().cpu())
                all_targets.append(batch['y'].detach().cpu())
        
        avg_loss = total_loss / total_samples
        metrics = self._calculate_metrics(
            torch.cat(all_predictions, dim=0),
            torch.cat(all_targets, dim=0),
        )
        
        return avg_loss, metrics
    
    def _move_batch_to_device(self, batch: Dict[str, Any]) -> Dict[str, Any]:
        """Move batch to device."""
        moved_batch = {}
        for key, value in batch.items():
            if isinstance(value, torch.Tensor):
                moved_batch[key] = value.to(self.device)
            else:
                moved_batch[key] = value
        return moved_batch
    
    def _calculate_metrics(
        self,
        predictions: torch.Tensor,
        targets: torch.Tensor,
    ) -> Dict[str, float]:
        """Calculate metrics."""
        metrics = {}
        
        # Accuracy
        _, predicted = torch.max(predictions, 1)
        correct = (predicted == targets).sum().item()
        total = targets.size(0)
        metrics['accuracy'] = correct / total
        
        return metrics
    
    def _save_checkpoint(self, epoch: int) -> None:
        """Save a checkpoint."""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict() if self.scheduler else None,
            'best_loss': self.early_stopping.best_score,
            'config': self.config.__dict__,
            'history': self.training_history,
        }
        
        # Save best model
        if epoch == 'final' or epoch % self.config.save_every == 0:
            filename = f"checkpoint_epoch_{epoch}.pt"
            filepath = self.save_dir / filename
            torch.save(checkpoint, filepath)
            self.logger.info(f"Saved checkpoint: {filepath}")
    
    def load_checkpoint(self, checkpoint_path: str) -> None:
        """Load a checkpoint."""
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        
        if 'scheduler_state_dict' in checkpoint and self.scheduler is not None:
            self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        
        self.current_epoch = checkpoint.get('epoch', 0) + 1
        self.best_loss = checkpoint.get('best_loss', float('inf'))
        
        self.logger.info(f"Loaded checkpoint from {checkpoint_path}")