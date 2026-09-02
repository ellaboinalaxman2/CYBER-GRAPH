"""Optimizer configuration for Member 3 - AI Engine."""

import torch
import torch.optim as optim
from typing import Optional, Dict, Any, Type
from dataclasses import dataclass


@dataclass
class OptimizerConfig:
    """Configuration for optimizers."""
    
    name: str = 'adam'
    learning_rate: float = 0.001
    weight_decay: float = 5e-4
    momentum: float = 0.9
    betas: tuple = (0.9, 0.999)
    eps: float = 1e-8
    amsgrad: bool = False
    nesterov: bool = False


class OptimizerFactory:
    """
    Factory for creating optimizers.
    
    Supported optimizers:
    - adam
    - sgd
    - adamw
    - rmsprop
    - adagrad
    - adamax
    """
    
    _registry = {
        'adam': optim.Adam,
        'sgd': optim.SGD,
        'adamw': optim.AdamW,
        'rmsprop': optim.RMSprop,
        'adagrad': optim.Adagrad,
        'adamax': optim.Adamax,
    }
    
    @classmethod
    def create(
        cls,
        model: torch.nn.Module,
        config: OptimizerConfig,
        **kwargs,
    ) -> torch.optim.Optimizer:
        """
        Create an optimizer.
        
        Args:
            model: Model to optimize
            config: Optimizer configuration
            **kwargs: Additional arguments
            
        Returns:
            torch.optim.Optimizer: Created optimizer
        """
        if config.name not in cls._registry:
            raise ValueError(
                f"Unknown optimizer: {config.name}. "
                f"Available: {list(cls._registry.keys())}"
            )
        
        optimizer_class = cls._registry[config.name]
        
        # Prepare parameters
        params = model.parameters()
        
        # Create optimizer with appropriate parameters
        if config.name == 'sgd':
            return optimizer_class(
                params,
                lr=config.learning_rate,
                momentum=config.momentum,
                weight_decay=config.weight_decay,
                nesterov=config.nesterov,
                **kwargs,
            )
        elif config.name in ['adam', 'adamw', 'adamax']:
            return optimizer_class(
                params,
                lr=config.learning_rate,
                betas=config.betas,
                eps=config.eps,
                weight_decay=config.weight_decay,
                amsgrad=config.amsgrad,
                **kwargs,
            )
        else:
            return optimizer_class(
                params,
                lr=config.learning_rate,
                weight_decay=config.weight_decay,
                **kwargs,
            )
    
    @classmethod
    def register(cls, name: str, optimizer_class: Type[torch.optim.Optimizer]):
        """
        Register a custom optimizer.
        
        Args:
            name: Optimizer name
            optimizer_class: Optimizer class
        """
        cls._registry[name] = optimizer_class
    
    @classmethod
    def get_available(cls) -> List[str]:
        """Get list of available optimizers."""
        return list(cls._registry.keys())