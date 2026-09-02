"""Confusion matrix for Member 3 - AI Engine."""

import torch
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, List, Optional, Tuple
from sklearn.metrics import confusion_matrix as sk_cm

from src.core.logging import get_logger


class ConfusionMatrix:
    """
    Confusion matrix visualization and analysis.
    
    Features:
    - Plot confusion matrix
    - Calculate metrics per class
    - Error analysis
    """
    
    def __init__(self):
        """Initialize the confusion matrix."""
        self.logger = get_logger("evaluation.confusion_matrix")
        self._matrices = []
    
    def compute(
        self,
        predictions: torch.Tensor,
        targets: torch.Tensor,
        labels: Optional[List[str]] = None,
    ) -> np.ndarray:
        """
        Compute confusion matrix.
        
        Args:
            predictions: Predicted labels
            targets: True labels
            labels: Class labels
            
        Returns:
            np.ndarray: Confusion matrix
        """
        pred_np = predictions.detach().cpu().numpy()
        target_np = targets.detach().cpu().numpy()
        
        cm = sk_cm(target_np, pred_np)
        self._matrices.append({
            'matrix': cm,
            'labels': labels,
            'predictions': pred_np,
            'targets': target_np,
        })
        
        return cm
    
    def plot(
        self,
        cm: np.ndarray,
        labels: Optional[List[str]] = None,
        normalize: bool = False,
        title: str = "Confusion Matrix",
        figsize: Tuple[int, int] = (8, 6),
        save_path: Optional[str] = None,
        show: bool = True,
    ) -> None:
        """
        Plot confusion matrix.
        
        Args:
            cm: Confusion matrix
            labels: Class labels
            normalize: Whether to normalize
            title: Plot title
            figsize: Figure size
            save_path: Path to save figure
            show: Whether to show plot
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        if normalize:
            cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
            cm = np.nan_to_num(cm)
            fmt = '.2f'
        else:
            fmt = 'd'
        
        if labels is None:
            num_classes = cm.shape[0]
            labels = [f'Class {i}' for i in range(num_classes)]
        
        sns.heatmap(
            cm,
            annot=True,
            fmt=fmt,
            cmap='Blues',
            xticklabels=labels,
            yticklabels=labels,
            ax=ax,
            cbar=True,
        )
        
        ax.set_xlabel('Predicted')
        ax.set_ylabel('Actual')
        ax.set_title(title)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Saved confusion matrix to {save_path}")
        
        if show:
            plt.show()
        else:
            plt.close()
    
    def get_per_class_metrics(
        self,
        cm: np.ndarray,
    ) -> Dict[str, Dict[str, float]]:
        """
        Get per-class metrics from confusion matrix.
        
        Args:
            cm: Confusion matrix
            
        Returns:
            Dict[str, Dict[str, float]]: Per-class metrics
        """
        num_classes = cm.shape[0]
        metrics = {}
        
        for i in range(num_classes):
            # True Positives
            tp = cm[i, i]
            
            # False Positives
            fp = cm[:, i].sum() - tp
            
            # False Negatives
            fn = cm[i, :].sum() - tp
            
            # True Negatives
            tn = cm.sum() - tp - fp - fn
            
            # Metrics
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
            
            metrics[f'class_{i}'] = {
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'tp': tp,
                'fp': fp,
                'fn': fn,
                'tn': tn,
                'support': tp + fn,
            }
        
        return metrics
    
    def get_error_analysis(
        self,
        predictions: torch.Tensor,
        targets: torch.Tensor,
        node_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze misclassifications.
        
        Args:
            predictions: Predicted labels
            targets: True labels
            node_ids: Node IDs (optional)
            
        Returns:
            Dict[str, Any]: Error analysis
        """
        pred_np = predictions.detach().cpu().numpy()
        target_np = targets.detach().cpu().numpy()
        
        # Find misclassifications
        misclassified = pred_np != target_np
        misclassified_indices = np.where(misclassified)[0]
        
        error_analysis = {
            'total_misclassified': len(misclassified_indices),
            'misclassification_rate': len(misclassified_indices) / len(target_np),
            'misclassified_indices': misclassified_indices.tolist(),
            'misclassified_predictions': pred_np[misclassified].tolist(),
            'misclassified_targets': target_np[misclassified].tolist(),
        }
        
        if node_ids is not None:
            error_analysis['misclassified_nodes'] = [
                node_ids[i] for i in misclassified_indices
            ]
        
        # Error types
        if len(np.unique(target_np)) == 2:
            # Binary classification
            false_positives = np.where((pred_np == 1) & (target_np == 0))[0]
            false_negatives = np.where((pred_np == 0) & (target_np == 1))[0]
            
            error_analysis['false_positives'] = false_positives.tolist()
            error_analysis['false_negatives'] = false_negatives.tolist()
            error_analysis['fp_count'] = len(false_positives)
            error_analysis['fn_count'] = len(false_negatives)
        
        return error_analysis
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get confusion matrix statistics."""
        return {
            "total_matrices": len(self._matrices),
        }