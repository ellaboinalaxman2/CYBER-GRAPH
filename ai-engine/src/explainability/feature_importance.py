"""Feature importance for Member 3 - AI Engine."""

import torch
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple

from src.core.logging import get_logger
from src.core.exceptions import ExplainabilityError


class FeatureImportance:
    """
    Calculates feature importance for predictions.
    
    Methods:
    - Permutation importance
    - Gradient-based importance
    - Integrated gradients
    - Feature ablation
    """
    
    def __init__(self, method: str = 'permutation'):
        """
        Initialize the feature importance calculator.
        
        Args:
            method: Importance method ('permutation', 'gradient', 'ablation')
        """
        self.logger = get_logger("explainability.feature_importance")
        self.method = method
        self._feature_names = []
        self._stats = {
            "total_calculations": 0,
            "method": method,
        }
    
    def calculate(
        self,
        model: torch.nn.Module,
        x: torch.Tensor,
        y: torch.Tensor,
        edge_index: Optional[torch.Tensor] = None,
        feature_names: Optional[List[str]] = None,
        node_idx: Optional[int] = None,
    ) -> Dict[str, float]:
        """
        Calculate feature importance.
        
        Args:
            model: Trained model
            x: Node features
            y: Target labels
            edge_index: Edge indices
            feature_names: Feature names
            node_idx: Specific node index
            
        Returns:
            Dict[str, float]: Feature importance scores
        """
        self.logger.info(f"Calculating feature importance using {self.method}")
        
        self._feature_names = feature_names or [f"feature_{i}" for i in range(x.size(1))]
        
        if self.method == 'permutation':
            importance = self._permutation_importance(model, x, y, edge_index, node_idx)
        elif self.method == 'gradient':
            importance = self._gradient_importance(model, x, edge_index, node_idx)
        elif self.method == 'ablation':
            importance = self._ablation_importance(model, x, edge_index, node_idx)
        else:
            raise ExplainabilityError(f"Unknown importance method: {self.method}")
        
        self._stats["total_calculations"] += 1
        
        return importance
    
    def _permutation_importance(
        self,
        model: torch.nn.Module,
        x: torch.Tensor,
        y: torch.Tensor,
        edge_index: Optional[torch.Tensor] = None,
        node_idx: Optional[int] = None,
    ) -> Dict[str, float]:
        """
        Calculate permutation importance.
        
        Args:
            model: Trained model
            x: Node features
            y: Target labels
            edge_index: Edge indices
            node_idx: Specific node index
            
        Returns:
            Dict[str, float]: Feature importance scores
        """
        model.eval()
        
        # Get baseline performance
        with torch.no_grad():
            logits = model(x, edge_index)
            pred = logits.argmax(dim=1)
            
            if node_idx is not None:
                pred = pred[node_idx].unsqueeze(0)
                y = y[node_idx].unsqueeze(0)
            
            base_accuracy = (pred == y).float().mean().item()
        
        importance_scores = {}
        x_np = x.detach().cpu().numpy()
        
        for i in range(x.size(1)):
            # Permute feature i
            x_permuted = x.clone()
            permuted_values = x_np[:, i].copy()
            np.random.shuffle(permuted_values)
            x_permuted[:, i] = torch.tensor(permuted_values, dtype=x.dtype)
            
            with torch.no_grad():
                logits = model(x_permuted, edge_index)
                pred = logits.argmax(dim=1)
                
                if node_idx is not None:
                    pred = pred[node_idx].unsqueeze(0)
                
                perm_accuracy = (pred == y).float().mean().item()
            
            # Importance is drop in accuracy
            importance = base_accuracy - perm_accuracy
            feature_name = self._feature_names[i] if i < len(self._feature_names) else f"feature_{i}"
            importance_scores[feature_name] = max(0, importance)
        
        # Normalize to sum to 1
        total = sum(importance_scores.values())
        if total > 0:
            importance_scores = {k: v / total for k, v in importance_scores.items()}
        
        return importance_scores
    
    def _gradient_importance(
        self,
        model: torch.nn.Module,
        x: torch.Tensor,
        edge_index: Optional[torch.Tensor] = None,
        node_idx: Optional[int] = None,
    ) -> Dict[str, float]:
        """
        Calculate gradient-based importance.
        
        Args:
            model: Trained model
            x: Node features
            edge_index: Edge indices
            node_idx: Specific node index
            
        Returns:
            Dict[str, float]: Feature importance scores
        """
        model.eval()
        
        x.requires_grad_(True)
        
        # Forward pass
        logits = model(x, edge_index)
        
        if node_idx is not None:
            logits = logits[node_idx].unsqueeze(0)
            pred_class = logits.argmax(dim=1)
        else:
            pred_class = logits.argmax(dim=1)
        
        # Backward pass
        loss = torch.sum(logits.gather(1, pred_class.unsqueeze(1)))
        loss.backward()
        
        # Gradients as importance
        gradients = x.grad.abs().detach().cpu().numpy()
        
        if node_idx is not None:
            gradients = gradients[node_idx]
        else:
            gradients = gradients.mean(axis=0)
        
        # Normalize
        total = gradients.sum()
        if total > 0:
            gradients = gradients / total
        
        importance_scores = {}
        for i, score in enumerate(gradients):
            feature_name = self._feature_names[i] if i < len(self._feature_names) else f"feature_{i}"
            importance_scores[feature_name] = float(score)
        
        return importance_scores
    
    def _ablation_importance(
        self,
        model: torch.nn.Module,
        x: torch.Tensor,
        edge_index: Optional[torch.Tensor] = None,
        node_idx: Optional[int] = None,
    ) -> Dict[str, float]:
        """
        Calculate ablation-based importance.
        
        Args:
            model: Trained model
            x: Node features
            edge_index: Edge indices
            node_idx: Specific node index
            
        Returns:
            Dict[str, float]: Feature importance scores
        """
        model.eval()
        
        # Get baseline prediction
        with torch.no_grad():
            logits = model(x, edge_index)
            
            if node_idx is not None:
                logits = logits[node_idx].unsqueeze(0)
                pred_class = logits.argmax(dim=1)
                base_prob = torch.softmax(logits, dim=1)[0, pred_class].item()
            else:
                pred_class = logits.argmax(dim=1)
                base_prob = torch.softmax(logits, dim=1)[range(len(pred_class)), pred_class].mean().item()
        
        importance_scores = {}
        
        for i in range(x.size(1)):
            # Ablate feature i (set to 0)
            x_ablated = x.clone()
            x_ablated[:, i] = 0
            
            with torch.no_grad():
                logits = model(x_ablated, edge_index)
                
                if node_idx is not None:
                    logits = logits[node_idx].unsqueeze(0)
                    prob = torch.softmax(logits, dim=1)[0, pred_class].item()
                else:
                    prob = torch.softmax(logits, dim=1)[range(len(pred_class)), pred_class].mean().item()
            
            # Importance is drop in probability
            importance = base_prob - prob
            feature_name = self._feature_names[i] if i < len(self._feature_names) else f"feature_{i}"
            importance_scores[feature_name] = max(0, importance)
        
        # Normalize to sum to 1
        total = sum(importance_scores.values())
        if total > 0:
            importance_scores = {k: v / total for k, v in importance_scores.items()}
        
        return importance_scores
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get feature importance statistics."""
        return self._stats.copy()