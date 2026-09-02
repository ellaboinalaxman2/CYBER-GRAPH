"""Tests for inference module."""

import pytest
import torch
import numpy as np
from datetime import datetime

from src.inference import (
    Predictor,
    PredictionResult,
    AnomalyScorer,
    ConfidenceEstimator,
    BatchPredictor,
)


class TestPredictionResult:
    """Tests for PredictionResult."""
    
    def test_creation(self):
        """Test creating a prediction result."""
        result = PredictionResult(
            node_id="NODE-1",
            prediction="ATTACK",
            probability=0.94,
            confidence=0.93,
            anomaly_score=0.94,
        )
        
        assert result.node_id == "NODE-1"
        assert result.prediction == "ATTACK"
        assert result.probability == 0.94
        assert result.confidence == 0.93
        assert result.anomaly_score == 0.94
        assert result.timestamp is not None
    
    def test_to_dict(self):
        """Test converting to dictionary."""
        result = PredictionResult(
            node_id="NODE-1",
            prediction="ATTACK",
            probability=0.94,
            confidence=0.93,
            anomaly_score=0.94,
            embedding=[0.1, 0.2, 0.3],
            explanation={"reasons": ["Test reason"]},
        )
        
        d = result.to_dict()
        assert d["node_id"] == "NODE-1"
        assert d["prediction"] == "ATTACK"
        assert d["embedding"] == [0.1, 0.2, 0.3]
        assert d["explanation"] == {"reasons": ["Test reason"]}


class TestAnomalyScorer:
    """Tests for AnomalyScorer."""
    
    def test_fit_and_score(self):
        """Test fitting and scoring."""
        scorer = AnomalyScorer(method='distance')
        
        embeddings = torch.randn(100, 16)
        scorer.fit(embeddings)
        
        test_embedding = torch.randn(16)
        score = scorer.score(test_embedding)
        
        assert 0 <= score <= 1
    
    def test_classify(self):
        """Test classification."""
        scorer = AnomalyScorer()
        
        classification, severity = scorer.classify(0.2)
        assert classification == "NORMAL"
        assert severity == "INFO"
        
        classification, severity = scorer.classify(0.6)
        assert classification == "MEDIUM_RISK"
        assert severity == "MEDIUM"
        
        classification, severity = scorer.classify(0.9)
        assert classification == "CRITICAL"
        assert severity == "CRITICAL"


class TestConfidenceEstimator:
    """Tests for ConfidenceEstimator."""
    
    def test_max_prob_confidence(self):
        """Test max probability confidence."""
        estimator = ConfidenceEstimator(method='max_prob')
        
        logits = torch.tensor([[0.1, 0.9]])
        confidence = estimator.estimate(logits)
        
        assert 0 <= confidence <= 1
    
    def test_entropy_confidence(self):
        """Test entropy-based confidence."""
        estimator = ConfidenceEstimator(method='entropy')
        
        logits = torch.tensor([[0.1, 0.9]])
        confidence = estimator.estimate(logits)
        
        assert 0 <= confidence <= 1


class TestBatchPredictor:
    """Tests for BatchPredictor."""
    
    def test_batch_prediction(self):
        """Test batch prediction."""
        # Create a simple model and predictor
        class SimpleModel(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.linear = torch.nn.Linear(16, 2)
            
            def forward(self, x, edge_index=None):
                return self.linear(x)
        
        model = SimpleModel()
        predictor = Predictor(model=model)
        batch_predictor = BatchPredictor(predictor)
        
        node_data_list = [
            {"node_id": f"NODE-{i}", "features": torch.randn(16).tolist()}
            for i in range(5)
        ]
        
        results = batch_predictor.predict_batch(node_data_list)
        
        assert len(results) == 5
        for result in results:
            assert result.node_id.startswith("NODE-")