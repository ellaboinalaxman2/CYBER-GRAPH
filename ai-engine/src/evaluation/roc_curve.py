"""ROC/PR curves for Member 3 - AI Engine."""

import torch
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any, List, Optional, Tuple
from sklearn.metrics import roc_curve, roc_auc_score, precision_recall_curve, average_precision_score

from src.core.logging import get_logger


class ROCCurve:
    """
    ROC and PR curve generation and visualization.
    
    Features:
    - ROC curve
    - PR curve
    - AUC calculation
    - Threshold selection
    """
    
    def __init__(self):
        """Initialize the ROC curve generator."""
        self.logger = get_logger("evaluation.roc_curve")
        self._curves = []
    
    def compute_roc(
        self,
        probabilities: torch.Tensor,
        targets: torch.Tensor,
    ) -> Dict[str, Any]:
        """
        Compute ROC curve.
        
        Args:
            probabilities: Prediction probabilities
            targets: True labels
            
        Returns:
            Dict[str, Any]: ROC curve data
        """
        prob_np = probabilities.detach().cpu().numpy()
        target_np = targets.detach().cpu().numpy()
        
        # Binary vs multi-class
        if prob_np.ndim == 2:
            # Multi-class: use one-vs-rest
            num_classes = prob_np.shape[1]
            fpr = {}
            tpr = {}
            thresholds = {}
            auc = {}
            
            for i in range(num_classes):
                fpr[i], tpr[i], thresholds[i] = roc_curve(
                    (target_np == i).astype(int),
                    prob_np[:, i],
                )
                auc[i] = roc_auc_score(
                    (target_np == i).astype(int),
                    prob_np[:, i],
                )
            
            # Macro average
            fpr_macro = np.linspace(0, 1, 100)
            tpr_macro = np.zeros_like(fpr_macro)
            
            for i in range(num_classes):
                tpr_macro += np.interp(fpr_macro, fpr[i], tpr[i])
            tpr_macro /= num_classes
            
            result = {
                'type': 'multi_class',
                'fpr_macro': fpr_macro,
                'tpr_macro': tpr_macro,
                'per_class': {
                    'fpr': fpr,
                    'tpr': tpr,
                    'thresholds': thresholds,
                    'auc': auc,
                },
                'auc_macro': np.mean(list(auc.values())),
                'auc_weighted': np.mean(list(auc.values())),
            }
        else:
            # Binary
            fpr, tpr, thresholds = roc_curve(target_np, prob_np)
            auc = roc_auc_score(target_np, prob_np)
            
            result = {
                'type': 'binary',
                'fpr': fpr,
                'tpr': tpr,
                'thresholds': thresholds,
                'auc': auc,
            }
        
        self._curves.append({
            'type': 'roc',
            'data': result,
        })
        
        return result
    
    def compute_pr(
        self,
        probabilities: torch.Tensor,
        targets: torch.Tensor,
    ) -> Dict[str, Any]:
        """
        Compute PR curve.
        
        Args:
            probabilities: Prediction probabilities
            targets: True labels
            
        Returns:
            Dict[str, Any]: PR curve data
        """
        prob_np = probabilities.detach().cpu().numpy()
        target_np = targets.detach().cpu().numpy()
        
        # Binary vs multi-class
        if prob_np.ndim == 2:
            # Multi-class: use one-vs-rest
            num_classes = prob_np.shape[1]
            precision = {}
            recall = {}
            thresholds = {}
            auc = {}
            
            for i in range(num_classes):
                precision[i], recall[i], thresholds[i] = precision_recall_curve(
                    (target_np == i).astype(int),
                    prob_np[:, i],
                )
                auc[i] = average_precision_score(
                    (target_np == i).astype(int),
                    prob_np[:, i],
                )
            
            result = {
                'type': 'multi_class',
                'per_class': {
                    'precision': precision,
                    'recall': recall,
                    'thresholds': thresholds,
                    'auc': auc,
                },
                'auc_macro': np.mean(list(auc.values())),
            }
        else:
            # Binary
            precision, recall, thresholds = precision_recall_curve(target_np, prob_np)
            auc = average_precision_score(target_np, prob_np)
            
            result = {
                'type': 'binary',
                'precision': precision,
                'recall': recall,
                'thresholds': thresholds,
                'auc': auc,
            }
        
        self._curves.append({
            'type': 'pr',
            'data': result,
        })
        
        return result
    
    def plot_roc(
        self,
        roc_data: Dict[str, Any],
        title: str = "ROC Curve",
        figsize: Tuple[int, int] = (8, 6),
        save_path: Optional[str] = None,
        show: bool = True,
    ) -> None:
        """
        Plot ROC curve.
        
        Args:
            roc_data: ROC curve data from compute_roc
            title: Plot title
            figsize: Figure size
            save_path: Path to save figure
            show: Whether to show plot
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        if roc_data['type'] == 'binary':
            ax.plot(roc_data['fpr'], roc_data['tpr'], label=f'ROC (AUC = {roc_data["auc"]:.3f})')
            ax.plot([0, 1], [0, 1], 'k--', label='Random')
        else:
            # Multi-class
            for i in roc_data['per_class']['fpr'].keys():
                fpr = roc_data['per_class']['fpr'][i]
                tpr = roc_data['per_class']['tpr'][i]
                auc = roc_data['per_class']['auc'][i]
                ax.plot(fpr, tpr, label=f'Class {i} (AUC = {auc:.3f})')
            
            # Macro average
            if 'fpr_macro' in roc_data:
                ax.plot(
                    roc_data['fpr_macro'],
                    roc_data['tpr_macro'],
                    'k--',
                    linewidth=2,
                    label=f'Macro avg (AUC = {roc_data["auc_macro"]:.3f})',
                )
        
        ax.set_xlabel('False Positive Rate')
        ax.set_ylabel('True Positive Rate')
        ax.set_title(title)
        ax.legend(loc='lower right')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Saved ROC curve to {save_path}")
        
        if show:
            plt.show()
        else:
            plt.close()
    
    def plot_pr(
        self,
        pr_data: Dict[str, Any],
        title: str = "Precision-Recall Curve",
        figsize: Tuple[int, int] = (8, 6),
        save_path: Optional[str] = None,
        show: bool = True,
    ) -> None:
        """
        Plot PR curve.
        
        Args:
            pr_data: PR curve data from compute_pr
            title: Plot title
            figsize: Figure size
            save_path: Path to save figure
            show: Whether to show plot
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        if pr_data['type'] == 'binary':
            ax.plot(
                pr_data['recall'],
                pr_data['precision'],
                label=f'PR (AUC = {pr_data["auc"]:.3f})',
            )
        else:
            # Multi-class
            for i in pr_data['per_class']['recall'].keys():
                recall = pr_data['per_class']['recall'][i]
                precision = pr_data['per_class']['precision'][i]
                auc = pr_data['per_class']['auc'][i]
                ax.plot(recall, precision, label=f'Class {i} (AUC = {auc:.3f})')
        
        ax.set_xlabel('Recall')
        ax.set_ylabel('Precision')
        ax.set_title(title)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Saved PR curve to {save_path}")
        
        if show:
            plt.show()
        else:
            plt.close()
    
    def find_best_threshold(
        self,
        roc_data: Dict[str, Any],
        criterion: str = 'youden',
    ) -> float:
        """
        Find best threshold using various criteria.
        
        Args:
            roc_data: ROC curve data
            criterion: Threshold selection criterion ('youden', 'gmean', 'distance')
            
        Returns:
            float: Best threshold
        """
        if roc_data['type'] != 'binary':
            self.logger.warning("Threshold selection only supported for binary classification")
            return 0.5
        
        fpr = roc_data['fpr']
        tpr = roc_data['tpr']
        thresholds = roc_data['thresholds']
        
        if criterion == 'youden':
            # Youden's J statistic: max(tpr - fpr)
            idx = np.argmax(tpr - fpr)
        elif criterion == 'gmean':
            # Geometric mean: sqrt(tpr * (1 - fpr))
            gmean = np.sqrt(tpr * (1 - fpr))
            idx = np.argmax(gmean)
        elif criterion == 'distance':
            # Minimum distance to (0, 1)
            distance = np.sqrt((1 - tpr)**2 + fpr**2)
            idx = np.argmin(distance)
        else:
            raise ValueError(f"Unknown criterion: {criterion}")
        
        best_threshold = thresholds[idx]
        self.logger.info(f"Best threshold ({criterion}): {best_threshold:.3f}")
        
        return best_threshold
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get ROC curve statistics."""
        return {
            "total_curves": len(self._curves),
        }