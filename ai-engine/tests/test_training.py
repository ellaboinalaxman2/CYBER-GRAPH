"""Tests for training module."""

import pytest
import torch
import numpy as np
from datetime import datetime

from src.training import (
    Trainer,
    TrainingConfig,
    LossFactory,
    LossConfig,
    OptimizerFactory,
    OptimizerConfig,
    SchedulerFactory,
    SchedulerConfig,
    EarlyStopping,
)


class TestLossFactory:
    """Tests for LossFactory."""
    
    def test_cross_entropy(self):
        """Test cross entropy loss."""
        config = LossConfig(name='cross_entropy')
        loss_fn = LossFactory.create(config)
        
        assert isinstance(loss_fn, torch.nn.CrossEntropyLoss)
    
    def test_binary_cross_entropy(self):
        """Test binary cross entropy loss."""
        config = LossConfig(name='binary_cross_entropy')
        loss_fn = LossFactory.create(config)
        
        assert isinstance(loss_fn, torch.nn.BCEWithLogitsLoss)
    
    def test_focal_loss(self):
        """Test focal loss."""
        config = LossConfig(name='focal_loss')
        loss_fn = LossFactory.create(config)
        
        from src.training.loss import FocalLoss
        assert isinstance(loss_fn, FocalLoss)


class TestOptimizerFactory:
    """Tests for OptimizerFactory."""
    
    def test_adam(self):
        """Test Adam optimizer."""
        model = torch.nn.Linear(10, 2)
        config = OptimizerConfig(name='adam', learning_rate=0.001)
        optimizer = OptimizerFactory.create(model, config)
        
        assert isinstance(optimizer, torch.optim.Adam)
    
    def test_sgd(self):
        """Test SGD optimizer."""
        model = torch.nn.Linear(10, 2)
        config = OptimizerConfig(name='sgd', learning_rate=0.001)
        optimizer = OptimizerFactory.create(model, config)
        
        assert isinstance(optimizer, torch.optim.SGD)
    
    def test_available_optimizers(self):
        """Test available optimizers."""
        available = OptimizerFactory.get_available()
        assert 'adam' in available
        assert 'sgd' in available


class TestSchedulerFactory:
    """Tests for SchedulerFactory."""
    
    def test_plateau(self):
        """Test plateau scheduler."""
        model = torch.nn.Linear(10, 2)
        optimizer = torch.optim.Adam(model.parameters())
        config = SchedulerConfig(name='plateau', patience=10)
        scheduler = SchedulerFactory.create(optimizer, config)
        
        assert isinstance(scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau)
    
    def test_step(self):
        """Test step scheduler."""
        model = torch.nn.Linear(10, 2)
        optimizer = torch.optim.Adam(model.parameters())
        config = SchedulerConfig(name='step', step_size=30, gamma=0.1)
        scheduler = SchedulerFactory.create(optimizer, config)
        
        assert isinstance(scheduler, torch.optim.lr_scheduler.StepLR)


class TestEarlyStopping:
    """Tests for EarlyStopping."""
    
    def test_early_stopping(self):
        """Test early stopping."""
        early_stopping = EarlyStopping(patience=3, verbose=False)
        
        # Simulate training with no improvement
        for epoch in range(5):
            score = 1.0 - epoch * 0.1  # Improving
            should_stop = early_stopping(epoch, score)
            if should_stop:
                break
        
        assert early_stopping.best_score is not None
    
    def test_best_state(self):
        """Test best state tracking."""
        early_stopping = EarlyStopping(patience=3, verbose=False)
        
        state1 = {'param': 1}
        state2 = {'param': 2}
        
        early_stopping(0, 1.0, state1)
        early_stopping(1, 2.0, state2)  # Worse
        
        best_state = early_stopping.get_best_state()
        assert best_state == state1


class TestTrainer:
    """Tests for Trainer."""
    
    def test_trainer_initialization(self):
        """Test trainer initialization."""
        model = torch.nn.Linear(10, 2)
        config = TrainingConfig(max_epochs=10, save_dir='./test_checkpoints')
        trainer = Trainer(model, config)
        
        assert trainer.model is not None
        assert trainer.optimizer is not None
        assert trainer.device is not None