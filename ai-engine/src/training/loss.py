"""Loss functions for Member 3 - AI Engine."""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class LossConfig:
    """Configuration for loss functions."""
    
    name: str = 'cross_entropy'
    weight: Optional[torch.Tensor] = None
    reduction: str = 'mean'
    label_smoothing: float = 0.0
    pos_weight: Optional[float] = None
    margin: float = 1.0
    temperature: float = 1.0


class LossFactory:
    """
    Factory for creating loss functions.
    
    Supported losses:
    - cross_entropy: Standard cross entropy
    - binary_cross_entropy: Binary cross entropy
    - focal_loss: Focal loss for imbalanced data
    - contrastive_loss: Contrastive loss for embeddings
    - triplet_loss: Triplet loss
    """
    
    @staticmethod
    def create(config: LossConfig) -> nn.Module:
        """
        Create a loss function.
        
        Args:
            config: Loss configuration
            
        Returns:
            nn.Module: Loss function
        """
        if config.name == 'cross_entropy':
            return nn.CrossEntropyLoss(
                weight=config.weight,
                reduction=config.reduction,
                label_smoothing=config.label_smoothing,
            )
        
        elif config.name == 'binary_cross_entropy':
            return nn.BCEWithLogitsLoss(
                weight=config.weight,
                reduction=config.reduction,
                pos_weight=config.pos_weight,
            )
        
        elif config.name == 'focal_loss':
            return FocalLoss(
                alpha=config.weight,
                gamma=2.0,
                reduction=config.reduction,
            )
        
        elif config.name == 'contrastive_loss':
            return ContrastiveLoss(
                margin=config.margin,
            )
        
        elif config.name == 'triplet_loss':
            return nn.TripletMarginLoss(
                margin=config.margin,
                reduction=config.reduction,
            )
        
        else:
            raise ValueError(f"Unknown loss: {config.name}")


class FocalLoss(nn.Module):
    """
    Focal Loss for imbalanced datasets.
    
    Focal Loss focuses training on hard examples by down-weighting easy examples.
    """
    
    def __init__(
        self,
        alpha: Optional[torch.Tensor] = None,
        gamma: float = 2.0,
        reduction: str = 'mean',
    ):
        """
        Initialize Focal Loss.
        
        Args:
            alpha: Class weights
            gamma: Focusing parameter
            reduction: Reduction method
        """
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction
    
    def forward(
        self,
        inputs: torch.Tensor,
        targets: torch.Tensor,
    ) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            inputs: Model outputs
            targets: Target labels
            
        Returns:
            torch.Tensor: Loss value
        """
        ce_loss = F.cross_entropy(
            inputs,
            targets,
            weight=self.alpha,
            reduction='none',
        )
        
        pt = torch.exp(-ce_loss)
        focal_loss = (1 - pt) ** self.gamma * ce_loss
        
        if self.reduction == 'mean':
            return focal_loss.mean()
        elif self.reduction == 'sum':
            return focal_loss.sum()
        else:
            return focal_loss


class ContrastiveLoss(nn.Module):
    """
    Contrastive Loss for embedding learning.
    
    Encourages embeddings of similar samples to be close,
    and embeddings of different samples to be far apart.
    """
    
    def __init__(
        self,
        margin: float = 1.0,
        reduction: str = 'mean',
    ):
        """
        Initialize Contrastive Loss.
        
        Args:
            margin: Margin for separating different classes
            reduction: Reduction method
        """
        super().__init__()
        self.margin = margin
        self.reduction = reduction
    
    def forward(
        self,
        embeddings1: torch.Tensor,
        embeddings2: torch.Tensor,
        labels: torch.Tensor,
    ) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            embeddings1: First set of embeddings
            embeddings2: Second set of embeddings
            labels: Labels (1 for similar, 0 for different)
            
        Returns:
            torch.Tensor: Loss value
        """
        # Calculate Euclidean distance
        distances = F.pairwise_distance(embeddings1, embeddings2)
        
        # Contrastive loss
        loss = labels * distances ** 2 + (1 - labels) * torch.clamp(
            self.margin - distances, min=0
        ) ** 2
        
        if self.reduction == 'mean':
            return loss.mean()
        elif self.reduction == 'sum':
            return loss.sum()
        else:
            return loss


class CombinedLoss(nn.Module):
    """
    Combined loss function for multi-task learning.
    
    Combines multiple loss functions with weights.
    """
    
    def __init__(
        self,
        losses: Dict[str, nn.Module],
        weights: Dict[str, float],
    ):
        """
        Initialize Combined Loss.
        
        Args:
            losses: Dictionary of loss functions
            weights: Dictionary of weights for each loss
        """
        super().__init__()
        self.losses = nn.ModuleDict(losses)
        self.weights = weights
    
    def forward(
        self,
        predictions: Dict[str, torch.Tensor],
        targets: Dict[str, torch.Tensor],
    ) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            predictions: Dictionary of predictions
            targets: Dictionary of targets
            
        Returns:
            torch.Tensor: Combined loss
        """
        total_loss = 0.0
        
        for name, loss_fn in self.losses.items():
            if name in predictions and name in targets:
                loss = loss_fn(predictions[name], targets[name])
                total_loss += self.weights.get(name, 1.0) * loss
        
        return total_loss