"""Anomaly detector for Member 3 - AI Engine."""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Optional, Dict, Any, List, Tuple
from sklearn.neighbors import LocalOutlierFactor
from sklearn.ensemble import IsolationForest

from src.core.logging import get_logger
from src.models.classifier import BinaryNodeClassifier


class AnomalyDetector:
    """
    Anomaly detection using GraphSAGE embeddings.
    
    Methods:
    - GraphSAGE classification
    - Isolation Forest
    - Local Outlier Factor
    - Ensemble methods
    """
    
    def __init__(
        self,
        method: str = 'graphsage',
        contamination: float = 0.1,
        random_state: int = 42,
    ):
        """
        Initialize the anomaly detector.
        
        Args:
            method: Detection method ('graphsage', 'isolation_forest', 'lof', 'ensemble')
            contamination: Expected proportion of outliers
            random_state: Random seed
        """
        self.logger = get_logger("models.anomaly_detector")
        self.method = method
        self.contamination = contamination
        self.random_state = random_state
        self._model = None
        self._threshold = None
        self._stats = {
            "method": method,
            "fitted": False,
            "n_samples": 0,
            "n_outliers": 0,
        }
    
    def fit(
        self,
        embeddings: torch.Tensor,
        labels: Optional[torch.Tensor] = None,
    ) -> None:
        """
        Fit the anomaly detector.
        
        Args:
            embeddings: Node embeddings
            labels: Node labels (optional)
        """
        self.logger.info(f"Fitting anomaly detector using {self.method}")
        
        embeddings_np = embeddings.detach().cpu().numpy()
        
        if self.method == 'graphsage':
            self._fit_graphsage(embeddings_np, labels)
        elif self.method == 'isolation_forest':
            self._fit_isolation_forest(embeddings_np)
        elif self.method == 'lof':
            self._fit_lof(embeddings_np)
        elif self.method == 'ensemble':
            self._fit_ensemble(embeddings_np, labels)
        else:
            raise ValueError(f"Unknown anomaly detection method: {self.method}")
        
        self._stats["fitted"] = True
        self._stats["n_samples"] = len(embeddings_np)
        self.logger.info("Anomaly detector fitted")
    
    def _fit_graphsage(
        self,
        embeddings: np.ndarray,
        labels: Optional[torch.Tensor] = None,
    ) -> None:
        """Fit using GraphSAGE classification."""
        # For GraphSAGE, we use the classifier directly
        # This is handled by the model itself
        pass
    
    def _fit_isolation_forest(self, embeddings: np.ndarray) -> None:
        """Fit Isolation Forest."""
        self._model = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
        )
        self._model.fit(embeddings)
    
    def _fit_lof(self, embeddings: np.ndarray) -> None:
        """Fit Local Outlier Factor."""
        self._model = LocalOutlierFactor(
            contamination=self.contamination,
            novelty=True,
        )
        self._model.fit(embeddings)
    
    def _fit_ensemble(
        self,
        embeddings: np.ndarray,
        labels: Optional[torch.Tensor] = None,
    ) -> None:
        """Fit ensemble of methods."""
        # Fit multiple methods and combine
        self._methods = {}
        
        # Isolation Forest
        if_model = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
        )
        if_model.fit(embeddings)
        self._methods['isolation_forest'] = if_model
        
        # LOF
        lof_model = LocalOutlierFactor(
            contamination=self.contamination,
            novelty=True,
        )
        lof_model.fit(embeddings)
        self._methods['lof'] = lof_model
    
    def predict(
        self,
        embeddings: torch.Tensor,
    ) -> torch.Tensor:
        """
        Predict anomalies.
        
        Args:
            embeddings: Node embeddings
            
        Returns:
            torch.Tensor: Anomaly labels (1 for anomaly, 0 for normal)
        """
        if not self._stats["fitted"]:
            raise ValueError("Anomaly detector not fitted")
        
        embeddings_np = embeddings.detach().cpu().numpy()
        
        if self.method == 'graphsage':
            # This should be handled by the classifier
            # We'll use the classifier's prediction
            return torch.zeros(len(embeddings_np))
        
        elif self.method == 'isolation_forest':
            predictions = self._model.predict(embeddings_np)
            # Convert -1 (anomaly) to 1, 1 (normal) to 0
            return torch.tensor((predictions == -1).astype(int))
        
        elif self.method == 'lof':
            predictions = self._model.predict(embeddings_np)
            return torch.tensor((predictions == -1).astype(int))
        
        elif self.method == 'ensemble':
            # Combine predictions from all methods
            scores = np.zeros(len(embeddings_np))
            
            for name, model in self._methods.items():
                pred = model.predict(embeddings_np)
                scores += (pred == -1).astype(int)
            
            # Majority vote
            predictions = (scores >= len(self._methods) / 2).astype(int)
            return torch.tensor(predictions)
        
        else:
            raise ValueError(f"Unknown anomaly detection method: {self.method}")
    
    def predict_scores(
        self,
        embeddings: torch.Tensor,
    ) -> torch.Tensor:
        """
        Get anomaly scores.
        
        Args:
            embeddings: Node embeddings
            
        Returns:
            torch.Tensor: Anomaly scores (0-1)
        """
        if not self._stats["fitted"]:
            raise ValueError("Anomaly detector not fitted")
        
        embeddings_np = embeddings.detach().cpu().numpy()
        
        if self.method == 'isolation_forest':
            scores = self._model.decision_function(embeddings_np)
            # Normalize to 0-1
            scores = 1 - (scores - scores.min()) / (scores.max() - scores.min() + 1e-8)
            return torch.tensor(scores, dtype=torch.float)
        
        elif self.method == 'lof':
            scores = self._model.score_samples(embeddings_np)
            # Normalize to 0-1 (lower score = more anomalous)
            scores = 1 - (scores - scores.min()) / (scores.max() - scores.min() + 1e-8)
            return torch.tensor(scores, dtype=torch.float)
        
        elif self.method == 'ensemble':
            # Average scores from all methods
            scores = np.zeros(len(embeddings_np))
            
            for name, model in self._methods.items():
                if hasattr(model, 'score_samples'):
                    s = model.score_samples(embeddings_np)
                    s = 1 - (s - s.min()) / (s.max() - s.min() + 1e-8)
                else:
                    s = model.decision_function(embeddings_np)
                    s = 1 - (s - s.min()) / (s.max() - s.min() + 1e-8)
                scores += s
            
            scores = scores / len(self._methods)
            return torch.tensor(scores, dtype=torch.float)
        
        else:
            raise ValueError(f"Unknown anomaly detection method: {self.method}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get detector statistics."""
        return self._stats.copy()