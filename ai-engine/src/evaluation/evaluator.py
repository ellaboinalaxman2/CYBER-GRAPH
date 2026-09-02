"""Main evaluator for Member 3 - AI Engine."""

import torch
import numpy as np
import pandas as pd
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from pathlib import Path
import json

from src.core.logging import get_logger
from src.core.config import settings
from src.evaluation.metrics import MetricsCalculator
from src.evaluation.confusion_matrix import ConfusionMatrix
from src.evaluation.roc_curve import ROCCurve
from src.evaluation.model_comparison import ModelComparison, ModelResult


@dataclass
class EvaluationConfig:
    """Configuration for evaluation."""
    
    metrics: List[str] = None
    plot_confusion_matrix: bool = True
    plot_roc: bool = True
    plot_pr: bool = True
    save_results: bool = True
    output_dir: str = './data/models/evaluation'
    
    def __post_init__(self):
        if self.metrics is None:
            self.metrics = [
                'accuracy', 'precision', 'recall', 'f1',
                'roc_auc', 'pr_auc', 'confusion_matrix',
            ]


class Evaluator:
    """
    Main evaluator for ML models.
    
    Features:
    - Comprehensive evaluation
    - Visualization
    - Result saving
    - Model comparison
    """
    
    def __init__(self, config: Optional[EvaluationConfig] = None):
        """
        Initialize the evaluator.
        
        Args:
            config: Evaluation configuration
        """
        self.logger = get_logger("evaluation.evaluator")
        self.config = config or EvaluationConfig()
        
        self.metrics_calculator = MetricsCalculator()
        self.confusion_matrix = ConfusionMatrix()
        self.roc_curve = ROCCurve()
        self.model_comparison = ModelComparison()
        
        # Create output directory
        self.output_dir = Path(self.config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self._results = {}
        self._statistics = {}
    
    def evaluate(
        self,
        model: torch.nn.Module,
        data: Dict[str, torch.Tensor],
        name: str = "model",
        labels: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate a model.
        
        Args:
            model: Model to evaluate
            data: Data dictionary with 'x', 'edge_index', 'y'
            name: Model name
            labels: Class labels
            
        Returns:
            Dict[str, Any]: Evaluation results
        """
        self.logger.info(f"Evaluating model: {name}")
        
        model.eval()
        
        with torch.no_grad():
            # Get predictions
            logits = model(data['x'], data['edge_index'])
            predictions = logits.argmax(dim=1)
            probabilities = torch.softmax(logits, dim=1)
            
            targets = data['y']
        
        # Calculate metrics
        metrics = self.metrics_calculator.calculate(
            predictions,
            targets,
            probabilities,
        )
        
        # Compute confusion matrix
        cm = self.confusion_matrix.compute(predictions, targets, labels)
        
        # Compute ROC curve
        roc_data = self.roc_curve.compute_roc(probabilities, targets)
        
        # Compute PR curve
        pr_data = self.roc_curve.compute_pr(probabilities, targets)
        
        # Compile results
        results = {
            'name': name,
            'metrics': metrics,
            'confusion_matrix': cm,
            'roc_data': roc_data,
            'pr_data': pr_data,
            'predictions': predictions,
            'probabilities': probabilities,
            'targets': targets,
        }
        
        self._results[name] = results
        
        # Add to model comparison
        model_result = ModelResult(
            name=name,
            metrics=metrics,
            predictions=predictions,
            probabilities=probabilities,
            targets=targets,
        )
        self.model_comparison.add_model(model_result)
        
        # Save results
        if self.config.save_results:
            self._save_results(name, results)
        
        # Plot results
        if self.config.plot_confusion_matrix:
            self._plot_confusion_matrix(name, cm, labels)
        
        if self.config.plot_roc:
            self._plot_roc(name, roc_data)
        
        if self.config.plot_pr:
            self._plot_pr(name, pr_data)
        
        # Log metrics
        self._log_metrics(name, metrics)
        
        return results
    
    def _save_results(self, name: str, results: Dict[str, Any]) -> None:
        """Save evaluation results."""
        save_dir = self.output_dir / name
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Save metrics
        metrics_path = save_dir / 'metrics.json'
        with open(metrics_path, 'w') as f:
            json.dump(results['metrics'], f, indent=2, default=str)
        
        # Save confusion matrix
        cm_path = save_dir / 'confusion_matrix.npy'
        np.save(cm_path, results['confusion_matrix'])
        
        # Save predictions
        pred_path = save_dir / 'predictions.pt'
        torch.save(results['predictions'], pred_path)
        
        self.logger.info(f"Saved results to {save_dir}")
    
    def _plot_confusion_matrix(
        self,
        name: str,
        cm: np.ndarray,
        labels: Optional[List[str]] = None,
    ) -> None:
        """Plot and save confusion matrix."""
        save_path = self.output_dir / name / 'confusion_matrix.png'
        
        # Determine if normalized
        normalize = self.config.plot_confusion_matrix == 'normalized'
        
        self.confusion_matrix.plot(
            cm,
            labels=labels,
            normalize=normalize,
            title=f'Confusion Matrix - {name}',
            save_path=str(save_path),
            show=False,
        )
    
    def _plot_roc(self, name: str, roc_data: Dict[str, Any]) -> None:
        """Plot and save ROC curve."""
        save_path = self.output_dir / name / 'roc_curve.png'
        
        self.roc_curve.plot_roc(
            roc_data,
            title=f'ROC Curve - {name}',
            save_path=str(save_path),
            show=False,
        )
    
    def _plot_pr(self, name: str, pr_data: Dict[str, Any]) -> None:
        """Plot and save PR curve."""
        save_path = self.output_dir / name / 'pr_curve.png'
        
        self.roc_curve.plot_pr(
            pr_data,
            title=f'Precision-Recall Curve - {name}',
            save_path=str(save_path),
            show=False,
        )
    
    def _log_metrics(self, name: str, metrics: Dict[str, Any]) -> None:
        """Log evaluation metrics."""
        self.logger.info(f"--- {name} Metrics ---")
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                self.logger.info(f"  {key}: {value:.4f}")
        
        # Log classification report
        if 'classification_report' in metrics:
            report = metrics['classification_report']
            self.logger.info("  Classification Report:")
            for class_name, class_metrics in report.items():
                if isinstance(class_metrics, dict):
                    self.logger.info(
                        f"    {class_name}: "
                        f"P={class_metrics.get('precision', 0):.3f}, "
                        f"R={class_metrics.get('recall', 0):.3f}, "
                        f"F1={class_metrics.get('f1-score', 0):.3f}"
                    )
    
    def compare_models(self) -> Dict[str, Any]:
        """
        Compare all evaluated models.
        
        Returns:
            Dict[str, Any]: Comparison results
        """
        if not self._results:
            self.logger.warning("No models to compare")
            return {}
        
        self.logger.info("Comparing models...")
        
        # Get comparison DataFrame
        comparison_df = self.model_comparison.compare_metrics()
        
        # Get best model
        best_accuracy = self.model_comparison.get_best_model('accuracy')
        
        summary = {
            'comparison_table': comparison_df.to_dict(),
            'best_model': best_accuracy,
            'total_models': len(self._results),
        }
        
        # Save comparison
        if self.config.save_results:
            save_path = self.output_dir / 'model_comparison.json'
            with open(save_path, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
            
            # Also save as CSV
            csv_path = self.output_dir / 'model_comparison.csv'
            comparison_df.to_csv(csv_path)
            
            self.logger.info(f"Saved model comparison to {save_path}")
        
        return summary
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get evaluation statistics."""
        return {
            "total_models": len(self._results),
            "models": list(self._results.keys()),
            "output_dir": str(self.output_dir),
        }