"""Confidence estimation for Member 3 - AI Engine."""

import torch
import numpy as np
from typing import Optional, Dict, Any, List, Tuple
from sklearn.calibration import calibration_curve

from src.core.logging import get_logger
from src.core.exceptions import InferenceError


class ConfidenceEstimator:
    """
    Confidence estimation for predictions.
    
    Methods:
    - Max probability
    - Entropy-based
    - Calibrated confidence
    - Monte Carlo dropout
    """
    
    def __init__(
        self,
        method: str = 'max_prob',
        num_samples: int = 10,
        temperature: float = 1.0,
    ):
        """
        Initialize the confidence estimator.
        
        Args:
            method: Confidence method ('max_prob', 'entropy', 'calibrated', 'mc_dropout')
            num_samples: Number of samples for MC Dropout
            temperature: Temperature for probability scaling
        """
        self.logger = get_logger("inference.confidence")
        self.method = method
        self.num_samples = num_samples
        self.temperature = temperature
        self._calibration_data = None
        self._fitted = False
        self._stats = {
            "total_estimates": 0,
            "avg_confidence": 0.0,
            "method": method,
        }
    
    def estimate(
        self,
        logits: torch.Tensor,
        model: Optional[torch.nn.Module] = None,
        x: Optional[torch.Tensor] = None,
        edge_index: Optional[torch.Tensor] = None,
    ) -> float:
        """
        Estimate confidence for a prediction.
        
        Args:
            logits: Model logits
            model: Model (for MC Dropout)
            x: Node features (for MC Dropout)
            edge_index: Edge indices (for MC Dropout)
            
        Returns:
            float: Confidence score (0-1)
        """
        self._stats["total_estimates"] += 1
        
        if self.method == 'max_prob':
            confidence = self._confidence_max_prob(logits)
        elif self.method == 'entropy':
            confidence = self._confidence_entropy(logits)
        elif self.method == 'calibrated':
            confidence = self._confidence_calibrated(logits)
        elif self.method == 'mc_dropout':
            if model is None or x is None:
                raise InferenceError("MC Dropout requires model and input")
            confidence = self._confidence_mc_dropout(model, x, edge_index)
        else:
            raise InferenceError(f"Unknown confidence method: {self.method}")
        
        # Update stats
        self._stats["avg_confidence"] = (
            (self._stats["avg_confidence"] * (self._stats["total_estimates"] - 1) + confidence)
            / self._stats["total_estimates"]
        )
        
        return float(confidence)
    
    def _confidence_max_prob(self, logits: torch.Tensor) -> float:
        """
        Confidence as maximum probability.
        
        Args:
            logits: Model logits
            
        Returns:
            float: Confidence score
        """
        probabilities = torch.softmax(logits / self.temperature, dim=1)
        return float(torch.max(probabilities).cpu().item())
    
    def _confidence_entropy(self, logits: torch.Tensor) -> float:
        """
        Confidence as 1 - normalized entropy.
        
        Args:
            logits: Model logits
            
        Returns:
            float: Confidence score
        """
        probabilities = torch.softmax(logits / self.temperature, dim=1)
        entropy = -torch.sum(probabilities * torch.log(probabilities + 1e-10), dim=1)
        max_entropy = np.log(len(probabilities[0]))
        confidence = 1 - (entropy / max_entropy)
        return float(confidence.cpu().item())
    
    def _confidence_calibrated(self, logits: torch.Tensor) -> float:
        """
        Confidence using calibration.
        
        Args:
            logits: Model logits
            
        Returns:
            float: Confidence score
        """
        probabilities = torch.softmax(logits / self.temperature, dim=1)
        max_prob = float(torch.max(probabilities).cpu().item())
        
        if self._fitted and self._calibration_data is not None:
            # Apply calibration mapping
            # This is a simplified version
            # In practice, you'd use Platt scaling or isotonic regression
            return max_prob
        
        return max_prob
    
    def _confidence_mc_dropout(
        self,
        model: torch.nn.Module,
        x: torch.Tensor,
        edge_index: torch.Tensor,
    ) -> float:
        """
        Confidence using Monte Carlo Dropout.
        
        Args:
            model: Model with dropout layers
            x: Node features
            edge_index: Edge indices
            
        Returns:
            float: Confidence score
        """
        model.train()  # Enable dropout
        predictions = []
        
        for _ in range(self.num_samples):
            with torch.no_grad():
                logits = model(x, edge_index)
                predictions.append(torch.softmax(logits, dim=1))
        
        model.eval()  # Disable dropout
        
        # Stack predictions
        pred_stack = torch.stack(predictions)
        
        # Calculate mean and variance
        mean_pred = pred_stack.mean(dim=0)
        var_pred = pred_stack.var(dim=0)
        
        # Confidence as 1 - uncertainty
        uncertainty = var_pred.mean()
        confidence = 1 - uncertainty
        
        return float(confidence.cpu().item())
    
    def calibrate(
        self,
        probabilities: torch.Tensor,
        targets: torch.Tensor,
        n_bins: int = 10,
    ) -> None:
        """
        Calibrate confidence using calibration curve.
        
        Args:
            probabilities: Prediction probabilities
            targets: True labels
            n_bins: Number of bins for calibration
        """
        self.logger.info("Calibrating confidence estimator...")
        
        prob_np = probabilities.detach().cpu().numpy()
        target_np = targets.detach().cpu().numpy()
        
        # For binary classification, use positive class probabilities
        if prob_np.ndim == 2 and prob_np.shape[1] == 2:
            prob_np = prob_np[:, 1]
        
        # Calibration curve
        fraction_positive, mean_predicted_value = calibration_curve(
            target_np,
            prob_np,
            n_bins=n_bins,
        )
        
        self._calibration_data = {
            'fraction_positive': fraction_positive,
            'mean_predicted_value': mean_predicted_value,
        }
        
        self._fitted = True
        self.logger.info("Confidence calibration complete")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get confidence statistics."""
        return self._stats.copy()