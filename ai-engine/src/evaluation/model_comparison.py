"""Model comparison for Member 3 - AI Engine."""

import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field

from src.core.logging import get_logger


@dataclass
class ModelResult:
    """Results for a single model."""
    
    name: str
    metrics: Dict[str, float]
    predictions: Optional[torch.Tensor] = None
    probabilities: Optional[torch.Tensor] = None
    targets: Optional[torch.Tensor] = None
    history: Optional[Dict[str, List[float]]] = None
    config: Optional[Dict[str, Any]] = None


class ModelComparison:
    """
    Compare multiple models.
    
    Features:
    - Metric comparison
    - Training history comparison
    - Statistical tests
    - Visualization
    """
    
    def __init__(self):
        """Initialize the model comparison."""
        self.logger = get_logger("evaluation.model_comparison")
        self.models: List[ModelResult] = []
    
    def add_model(self, result: ModelResult) -> None:
        """
        Add a model result for comparison.
        
        Args:
            result: ModelResult object
        """
        self.models.append(result)
        self.logger.info(f"Added model: {result.name}")
    
    def compare_metrics(self) -> pd.DataFrame:
        """
        Compare metrics across models.
        
        Returns:
            pd.DataFrame: Comparison table
        """
        if not self.models:
            self.logger.warning("No models to compare")
            return pd.DataFrame()
        
        data = {}
        
        for model in self.models:
            data[model.name] = {}
            for key, value in model.metrics.items():
                if isinstance(value, (int, float)):
                    data[model.name][key] = value
        
        df = pd.DataFrame(data).T
        return df
    
    def plot_metric_comparison(
        self,
        metric_name: str,
        title: Optional[str] = None,
        figsize: Tuple[int, int] = (10, 6),
        save_path: Optional[str] = None,
        show: bool = True,
    ) -> None:
        """
        Plot comparison of a single metric.
        
        Args:
            metric_name: Metric to compare
            title: Plot title
            figsize: Figure size
            save_path: Path to save figure
            show: Whether to show plot
        """
        if not self.models:
            self.logger.warning("No models to compare")
            return
        
        values = []
        names = []
        
        for model in self.models:
            if metric_name in model.metrics:
                values.append(model.metrics[metric_name])
                names.append(model.name)
        
        if not values:
            self.logger.warning(f"Metric '{metric_name}' not found in any model")
            return
        
        fig, ax = plt.subplots(figsize=figsize)
        
        colors = plt.cm.viridis(np.linspace(0, 0.8, len(values)))
        
        bars = ax.bar(names, values, color=colors)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.,
                height + 0.01,
                f'{value:.4f}',
                ha='center',
                va='bottom',
            )
        
        ax.set_ylabel(metric_name)
        ax.set_title(title or f'Comparison of {metric_name}')
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Saved metric comparison to {save_path}")
        
        if show:
            plt.show()
        else:
            plt.close()
    
    def plot_training_history(
        self,
        metric: str = 'loss',
        title: Optional[str] = None,
        figsize: Tuple[int, int] = (10, 6),
        save_path: Optional[str] = None,
        show: bool = True,
    ) -> None:
        """
        Plot training history comparison.
        
        Args:
            metric: Metric to plot ('loss', 'accuracy')
            title: Plot title
            figsize: Figure size
            save_path: Path to save figure
            show: Whether to show plot
        """
        if not self.models:
            self.logger.warning("No models to compare")
            return
        
        fig, ax = plt.subplots(figsize=figsize)
        
        for model in self.models:
            if model.history is not None:
                if metric in model.history:
                    ax.plot(
                        model.history[metric],
                        label=model.name,
                        linewidth=2,
                    )
        
        ax.set_xlabel('Epoch')
        ax.set_ylabel(metric)
        ax.set_title(title or f'Training History ({metric})')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Saved training history to {save_path}")
        
        if show:
            plt.show()
        else:
            plt.close()
    
    def get_best_model(self, metric: str) -> Optional[str]:
        """
        Get the best model for a given metric.
        
        Args:
            metric: Metric to optimize
            
        Returns:
            Optional[str]: Best model name
        """
        if not self.models:
            return None
        
        best_name = None
        best_value = -float('inf')
        
        for model in self.models:
            if metric in model.metrics:
                value = model.metrics[metric]
                if value > best_value:
                    best_value = value
                    best_name = model.name
        
        return best_name
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get comparison summary.
        
        Returns:
            Dict[str, Any]: Comparison summary
        """
        if not self.models:
            return {"total_models": 0}
        
        summary = {
            "total_models": len(self.models),
            "model_names": [m.name for m in self.models],
            "metrics": {},
        }
        
        # Collect all metrics
        all_metrics = set()
        for model in self.models:
            all_metrics.update(model.metrics.keys())
        
        for metric in all_metrics:
            values = []
            names = []
            for model in self.models:
                if metric in model.metrics:
                    values.append(model.metrics[metric])
                    names.append(model.name)
            
            if values:
                best_idx = np.argmax(values)
                summary["metrics"][metric] = {
                    "values": dict(zip(names, values)),
                    "best": names[best_idx],
                    "best_value": values[best_idx],
                    "mean": np.mean(values),
                    "std": np.std(values),
                }
        
        return summary