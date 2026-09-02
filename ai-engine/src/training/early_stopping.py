"""Early stopping for Member 3 - AI Engine."""

import numpy as np
from typing import Optional, Dict, Any
from collections import deque

from src.core.logging import get_logger


class EarlyStopping:
    """
    Early stopping to prevent overfitting.
    
    Stops training when validation performance stops improving.
    """
    
    def __init__(
        self,
        patience: int = 20,
        min_delta: float = 1e-4,
        mode: str = 'min',
        restore_best: bool = True,
        verbose: bool = True,
    ):
        """
        Initialize early stopping.
        
        Args:
            patience: Number of epochs to wait for improvement
            min_delta: Minimum change to qualify as improvement
            mode: 'min' for minimizing loss, 'max' for maximizing metric
            restore_best: Whether to restore the best model
            verbose: Whether to print messages
        """
        self.patience = patience
        self.min_delta = min_delta
        self.mode = mode
        self.restore_best = restore_best
        self.verbose = verbose
        
        self.logger = get_logger("training.early_stopping")
        
        self.counter = 0
        self.best_score = None
        self.early_stop = False
        self.best_epoch = 0
        self.best_state = None
        self.best_metrics = {}
        
        self.history = {
            'epoch': [],
            'score': [],
            'is_improvement': [],
        }
    
    def __call__(
        self,
        epoch: int,
        score: float,
        model_state: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, float]] = None,
    ) -> bool:
        """
        Check if training should stop.
        
        Args:
            epoch: Current epoch
            score: Validation score (loss or metric)
            model_state: Model state dict (optional)
            metrics: Additional metrics (optional)
            
        Returns:
            bool: True if training should stop
        """
        if self.best_score is None:
            self.best_score = score
            self.best_epoch = epoch
            self.best_metrics = metrics or {}
            
            if model_state:
                self.best_state = model_state
            
            self.logger.info(f"Initial best score: {score:.4f}")
            return False
        
        # Check for improvement
        if self.mode == 'min':
            is_improvement = score < self.best_score - self.min_delta
        else:  # max
            is_improvement = score > self.best_score + self.min_delta
        
        # Update history
        self.history['epoch'].append(epoch)
        self.history['score'].append(score)
        self.history['is_improvement'].append(is_improvement)
        
        if is_improvement:
            self.best_score = score
            self.best_epoch = epoch
            self.best_metrics = metrics or {}
            self.counter = 0
            
            if model_state and self.restore_best:
                self.best_state = model_state
            
            if self.verbose:
                self.logger.info(f"New best score: {score:.4f} at epoch {epoch}")
        else:
            self.counter += 1
            
            if self.verbose:
                self.logger.info(
                    f"No improvement for {self.counter} epochs. "
                    f"Best: {self.best_score:.4f}"
                )
        
        # Check early stopping condition
        if self.counter >= self.patience:
            self.early_stop = True
            
            if self.verbose:
                self.logger.info(
                    f"Early stopping triggered at epoch {epoch}. "
                    f"Best epoch: {self.best_epoch} with score: {self.best_score:.4f}"
                )
            
            return True
        
        return False
    
    def get_best_state(self) -> Optional[Dict[str, Any]]:
        """Get the best model state."""
        return self.best_state
    
    def get_best_epoch(self) -> int:
        """Get the best epoch."""
        return self.best_epoch
    
    def get_best_metrics(self) -> Dict[str, float]:
        """Get the best metrics."""
        return self.best_metrics
    
    def get_summary(self) -> Dict[str, Any]:
        """Get early stopping summary."""
        return {
            'best_score': self.best_score,
            'best_epoch': self.best_epoch,
            'best_metrics': self.best_metrics,
            'patience': self.patience,
            'counter': self.counter,
            'early_stop': self.early_stop,
            'history': self.history,
        }
    
    def reset(self) -> None:
        """Reset early stopping state."""
        self.counter = 0
        self.best_score = None
        self.early_stop = False
        self.best_epoch = 0
        self.best_state = None
        self.best_metrics = {}
        self.history = {
            'epoch': [],
            'score': [],
            'is_improvement': [],
        }