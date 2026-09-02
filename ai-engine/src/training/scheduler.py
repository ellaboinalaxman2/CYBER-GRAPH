"""Learning rate scheduler for Member 3 - AI Engine."""

import torch
import torch.optim as optim
from typing import Optional, Dict, Any, Type
from dataclasses import dataclass


@dataclass
class SchedulerConfig:
    """Configuration for learning rate schedulers."""
    
    name: str = 'plateau'
    factor: float = 0.5
    patience: int = 10
    min_lr: float = 1e-6
    step_size: int = 30
    gamma: float = 0.1
    warmup_epochs: int = 5
    warmup_start_lr: float = 1e-6
    total_epochs: int = 200


class SchedulerFactory:
    """
    Factory for creating learning rate schedulers.
    
    Supported schedulers:
    - plateau: ReduceLROnPlateau
    - step: StepLR
    - exponential: ExponentialLR
    - cosine: CosineAnnealingLR
    - cosine_warmup: CosineAnnealingWarmRestarts
    - one_cycle: OneCycleLR
    """
    
    _registry = {
        'plateau': optim.lr_scheduler.ReduceLROnPlateau,
        'step': optim.lr_scheduler.StepLR,
        'exponential': optim.lr_scheduler.ExponentialLR,
        'cosine': optim.lr_scheduler.CosineAnnealingLR,
        'cosine_warmup': optim.lr_scheduler.CosineAnnealingWarmRestarts,
        'one_cycle': optim.lr_scheduler.OneCycleLR,
    }
    
    @classmethod
    def create(
        cls,
        optimizer: torch.optim.Optimizer,
        config: SchedulerConfig,
        **kwargs,
    ) -> torch.optim.lr_scheduler._LRScheduler:
        """
        Create a learning rate scheduler.
        
        Args:
            optimizer: Optimizer to schedule
            config: Scheduler configuration
            **kwargs: Additional arguments
            
        Returns:
            torch.optim.lr_scheduler._LRScheduler: Created scheduler
        """
        if config.name not in cls._registry:
            raise ValueError(
                f"Unknown scheduler: {config.name}. "
                f"Available: {list(cls._registry.keys())}"
            )
        
        scheduler_class = cls._registry[config.name]
        
        if config.name == 'plateau':
            return scheduler_class(
                optimizer,
                mode='min',
                factor=config.factor,
                patience=config.patience,
                min_lr=config.min_lr,
                **kwargs,
            )
        elif config.name == 'step':
            return scheduler_class(
                optimizer,
                step_size=config.step_size,
                gamma=config.gamma,
                **kwargs,
            )
        elif config.name == 'exponential':
            return scheduler_class(
                optimizer,
                gamma=config.gamma,
                **kwargs,
            )
        elif config.name == 'cosine':
            return scheduler_class(
                optimizer,
                T_max=config.total_epochs,
                eta_min=config.min_lr,
                **kwargs,
            )
        elif config.name == 'cosine_warmup':
            return scheduler_class(
                optimizer,
                T_0=config.step_size,
                T_mult=2,
                eta_min=config.min_lr,
                **kwargs,
            )
        elif config.name == 'one_cycle':
            return scheduler_class(
                optimizer,
                max_lr=config.learning_rate,
                epochs=config.total_epochs,
                **kwargs,
            )
        else:
            return scheduler_class(optimizer, **kwargs)
    
    @classmethod
    def register(
        cls,
        name: str,
        scheduler_class: Type[torch.optim.lr_scheduler._LRScheduler],
    ):
        """Register a custom scheduler."""
        cls._registry[name] = scheduler_class
    
    @classmethod
    def get_available(cls) -> List[str]:
        """Get list of available schedulers."""
        return list(cls._registry.keys())