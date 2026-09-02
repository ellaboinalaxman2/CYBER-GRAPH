"""Anomaly scoring for Member 3 - AI Engine."""

import torch
import numpy as np
from typing import Optional, Dict, Any, List, Tuple
from scipy import stats

from src.core.logging import get_logger
from src.core.exceptions import InferenceError


class AnomalyScorer:
    """
    Anomaly scoring with multiple methods.
    
    Methods:
    - Probability-based
    - Distance-based
    - Statistical outlier detection
    - Ensemble scoring
    """
    
    def __init__(
        self,
        method: str = 'probability',
        threshold: float = 0.5,
    ):
        """
        Initialize the anomaly scorer.
        
        Args:
            method: Scoring method ('probability', 'distance', 'statistical', 'ensemble')
            threshold: Anomaly threshold
        """
        self.logger = get_logger("inference.anomaly_scoring")
        self.method = method
        self.threshold = threshold
        self._mean_embedding = None
        self._std_embedding = None
        self._fitted = False
        self._stats = {
            "total_scored": 0,
            "anomalies_detected": 0,
            "method": method,
        }
    
    def fit(self, embeddings: torch.Tensor) -> None:
        """
        Fit the anomaly scorer.
        
        Args:
            embeddings: Embeddings to fit on
        """
        self.logger.info(f"Fitting anomaly scorer with method: {self.method}")
        
        embeddings_np = embeddings.detach().cpu().numpy()
        
        # Calculate mean and std for distance-based methods
        self._mean_embedding = np.mean(embeddings_np, axis=0)
        self._std_embedding = np.std(embeddings_np, axis=0) + 1e-8
        
        self._fitted = True
        self._stats["fitted_samples"] = len(embeddings_np)
    
    def score(
        self,
        embedding: torch.Tensor,
        probability: Optional[torch.Tensor] = None,
    ) -> float:
        """
        Score a single embedding.
        
        Args:
            embedding: Node embedding
            probability: Prediction probability (optional)
            
        Returns:
            float: Anomaly score (0-1)
        """
        self._stats["total_scored"] += 1
        
        if self.method == 'probability':
            score = self._score_probability(probability)
        elif self.method == 'distance':
            score = self._score_distance(embedding)
        elif self.method == 'statistical':
            score = self._score_statistical(embedding)
        elif self.method == 'ensemble':
            score = self._score_ensemble(embedding, probability)
        else:
            raise InferenceError(f"Unknown scoring method: {self.method}")
        
        if score > self.threshold:
            self._stats["anomalies_detected"] += 1
        
        return score
    
    def _score_probability(self, probability: Optional[torch.Tensor]) -> float:
        """
        Score using prediction probability.
        
        Args:
            probability: Prediction probability
            
        Returns:
            float: Anomaly score
        """
        if probability is None:
            return 0.5
        
        # Use probability of positive class
        if len(probability) == 2:
            return float(probability[1].cpu().item())
        else:
            return float(torch.max(probability[1:]).cpu().item())
    
    def _score_distance(self, embedding: torch.Tensor) -> float:
        """
        Score using distance from mean embedding.
        
        Args:
            embedding: Node embedding
            
        Returns:
            float: Anomaly score
        """
        if not self._fitted:
            return 0.5
        
        emb_np = embedding.detach().cpu().numpy()
        
        # Euclidean distance
        distance = np.linalg.norm(emb_np - self._mean_embedding)
        
        # Normalize to 0-1
        max_distance = np.linalg.norm(self._std_embedding * 5)  # 5 standard deviations
        score = min(distance / max_distance, 1.0)
        
        return score
    
    def _score_statistical(self, embedding: torch.Tensor) -> float:
        """
        Score using statistical outlier detection.
        
        Args:
            embedding: Node embedding
            
        Returns:
            float: Anomaly score
        """
        if not self._fitted:
            return 0.5
        
        emb_np = embedding.detach().cpu().numpy()
        
        # Mahalanobis distance
        diff = emb_np - self._mean_embedding
        cov_inv = np.linalg.pinv(np.diag(self._std_embedding ** 2))
        mahalanobis = np.sqrt(diff @ cov_inv @ diff)
        
        # Convert to probability using chi-squared distribution
        p_value = 1 - stats.chi2.cdf(mahalanobis, len(emb_np))
        
        # Convert to 0-1 score
        score = 1 - p_value
        
        return min(max(score, 0.0), 1.0)
    
    def _score_ensemble(
        self,
        embedding: torch.Tensor,
        probability: Optional[torch.Tensor] = None,
    ) -> float:
        """
        Score using ensemble of methods.
        
        Args:
            embedding: Node embedding
            probability: Prediction probability
            
        Returns:
            float: Anomaly score
        """
        scores = []
        
        # Probability score
        if probability is not None:
            scores.append(self._score_probability(probability))
        
        # Distance score
        scores.append(self._score_distance(embedding))
        
        # Statistical score
        scores.append(self._score_statistical(embedding))
        
        # Average scores
        return np.mean(scores)
    
    def score_batch(
        self,
        embeddings: torch.Tensor,
        probabilities: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Score multiple embeddings.
        
        Args:
            embeddings: Node embeddings
            probabilities: Prediction probabilities
            
        Returns:
            torch.Tensor: Anomaly scores
        """
        scores = []
        
        for i in range(embeddings.size(0)):
            prob = probabilities[i] if probabilities is not None else None
            score = self.score(embeddings[i], prob)
            scores.append(score)
        
        return torch.tensor(scores, dtype=torch.float)
    
    def classify(self, score: float) -> Tuple[str, str]:
        """
        Classify anomaly based on score.
        
        Args:
            score: Anomaly score
            
        Returns:
            Tuple[str, str]: (classification, severity)
        """
        if score < 0.3:
            return "NORMAL", "INFO"
        elif score < 0.5:
            return "LOW_RISK", "LOW"
        elif score < 0.7:
            return "MEDIUM_RISK", "MEDIUM"
        elif score < 0.85:
            return "HIGH_RISK", "HIGH"
        else:
            return "CRITICAL", "CRITICAL"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get scoring statistics."""
        return self._stats.copy()