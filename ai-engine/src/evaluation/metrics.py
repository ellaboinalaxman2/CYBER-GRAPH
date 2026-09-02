"""Metrics computation for Member 3 - AI Engine."""

import torch
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    classification_report,
)

from src.core.logging import get_logger


class MetricsCalculator:
    """
    Calculates various evaluation metrics.
    
    Metrics:
    - Accuracy
    - Precision (macro, micro, weighted)
    - Recall (macro, micro, weighted)
    - F1 Score (macro, micro, weighted)
    - ROC-AUC
    - PR-AUC
    - Confusion Matrix
    - Classification Report
    """
    
    def __init__(self):
        """Initialize the metrics calculator."""
        self.logger = get_logger("evaluation.metrics")
        self._metrics_history = []
    
    def calculate(
        self,
        predictions: torch.Tensor,
        targets: torch.Tensor,
        probabilities: Optional[torch.Tensor] = None,
        average: str = 'weighted',
        multi_class: str = 'ovr',
    ) -> Dict[str, Any]:
        """
        Calculate all metrics.
        
        Args:
            predictions: Predicted labels
            targets: True labels
            probabilities: Prediction probabilities (for AUC)
            average: Averaging method for multi-class
            multi_class: Multi-class strategy for ROC-AUC
            
        Returns:
            Dict[str, Any]: Computed metrics
        """
        # Convert to numpy
        pred_np = predictions.detach().cpu().numpy()
        target_np = targets.detach().cpu().numpy()
        
        prob_np = None
        if probabilities is not None:
            prob_np = probabilities.detach().cpu().numpy()
        
        # Calculate metrics
        metrics = {}
        
        # Accuracy
        metrics['accuracy'] = accuracy_score(target_np, pred_np)
        
        # Number of classes
        num_classes = len(np.unique(target_np))
        
        # Precision, Recall, F1
        if num_classes == 2:
            # Binary classification
            metrics['precision'] = precision_score(target_np, pred_np)
            metrics['recall'] = recall_score(target_np, pred_np)
            metrics['f1'] = f1_score(target_np, pred_np)
            
            # AUC
            if prob_np is not None:
                if prob_np.ndim == 2:
                    prob_np = prob_np[:, 1]
                metrics['roc_auc'] = roc_auc_score(target_np, prob_np)
                metrics['pr_auc'] = average_precision_score(target_np, prob_np)
        else:
            # Multi-class classification
            metrics['precision_macro'] = precision_score(target_np, pred_np, average='macro')
            metrics['recall_macro'] = recall_score(target_np, pred_np, average='macro')
            metrics['f1_macro'] = f1_score(target_np, pred_np, average='macro')
            
            metrics['precision_weighted'] = precision_score(target_np, pred_np, average='weighted')
            metrics['recall_weighted'] = recall_score(target_np, pred_np, average='weighted')
            metrics['f1_weighted'] = f1_score(target_np, pred_np, average='weighted')
            
            # AUC for multi-class
            if prob_np is not None:
                metrics['roc_auc_ovr'] = roc_auc_score(
                    target_np,
                    prob_np,
                    multi_class=multi_class,
                    average='weighted',
                )
                metrics['roc_auc_ovo'] = roc_auc_score(
                    target_np,
                    prob_np,
                    multi_class='ovo',
                    average='weighted',
                )
        
        # Classification report
        report = classification_report(target_np, pred_np, output_dict=True)
        metrics['classification_report'] = report
        
        # Confusion matrix
        cm = confusion_matrix(target_np, pred_np)
        metrics['confusion_matrix'] = cm
        
        # Record history
        self._metrics_history.append({
            'metrics': metrics.copy(),
            'num_samples': len(target_np),
            'num_classes': num_classes,
        })
        
        return metrics
    
    def calculate_batch(
        self,
        batch_results: List[Tuple[torch.Tensor, torch.Tensor, Optional[torch.Tensor]]],
    ) -> Dict[str, Any]:
        """
        Calculate metrics over multiple batches.
        
        Args:
            batch_results: List of (predictions, targets, probabilities) tuples
            
        Returns:
            Dict[str, Any]: Aggregate metrics
        """
        all_predictions = []
        all_targets = []
        all_probabilities = []
        
        for pred, target, prob in batch_results:
            all_predictions.append(pred)
            all_targets.append(target)
            if prob is not None:
                all_probabilities.append(prob)
        
        # Concatenate
        all_predictions = torch.cat(all_predictions, dim=0)
        all_targets = torch.cat(all_targets, dim=0)
        
        if all_probabilities:
            all_probabilities = torch.cat(all_probabilities, dim=0)
        else:
            all_probabilities = None
        
        return self.calculate(all_predictions, all_targets, all_probabilities)
    
    def get_best_threshold(
        self,
        probabilities: torch.Tensor,
        targets: torch.Tensor,
        metric: str = 'f1',
    ) -> float:
        """
        Find the best threshold for binary classification.
        
        Args:
            probabilities: Prediction probabilities
            targets: True labels
            metric: Metric to optimize ('f1', 'precision', 'recall', 'accuracy')
            
        Returns:
            float: Best threshold
        """
        prob_np = probabilities.detach().cpu().numpy()
        target_np = targets.detach().cpu().numpy()
        
        thresholds = np.linspace(0.1, 0.9, 50)
        best_score = -1
        best_threshold = 0.5
        
        for threshold in thresholds:
            preds = (prob_np >= threshold).astype(int)
            
            if metric == 'f1':
                score = f1_score(target_np, preds)
            elif metric == 'precision':
                score = precision_score(target_np, preds, zero_division=0)
            elif metric == 'recall':
                score = recall_score(target_np, preds, zero_division=0)
            elif metric == 'accuracy':
                score = accuracy_score(target_np, preds)
            else:
                raise ValueError(f"Unknown metric: {metric}")
            
            if score > best_score:
                best_score = score
                best_threshold = threshold
        
        self.logger.info(f"Best threshold for {metric}: {best_threshold:.3f} (score: {best_score:.4f})")
        return best_threshold
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get metrics statistics."""
        return {
            "total_evaluations": len(self._metrics_history),
            "last_evaluation": self._metrics_history[-1] if self._metrics_history else None,
        }