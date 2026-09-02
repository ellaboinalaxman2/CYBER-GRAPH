"""Tests for evaluation module."""

import pytest
import torch
import numpy as np

from src.evaluation import (
    Evaluator,
    EvaluationConfig,
    MetricsCalculator,
    ConfusionMatrix,
    ROCCurve,
    ModelComparison,
    ModelResult,
)


class TestMetricsCalculator:
    """Tests for MetricsCalculator."""
    
    def test_binary_metrics(self):
        """Test binary classification metrics."""
        calculator = MetricsCalculator()
        
        predictions = torch.tensor([0, 1, 1, 0, 1])
        targets = torch.tensor([0, 1, 0, 0, 1])
        probabilities = torch.tensor([0.1, 0.9, 0.8, 0.2, 0.7])
        
        metrics = calculator.calculate(predictions, targets, probabilities)
        
        assert 'accuracy' in metrics
        assert 'precision' in metrics
        assert 'recall' in metrics
        assert 'f1' in metrics
        assert 'roc_auc' in metrics
    
    def test_multi_class_metrics(self):
        """Test multi-class classification metrics."""
        calculator = MetricsCalculator()
        
        predictions = torch.tensor([0, 1, 2, 1, 0])
        targets = torch.tensor([0, 1, 2, 0, 1])
        
        metrics = calculator.calculate(predictions, targets)
        
        assert 'accuracy' in metrics
        assert 'precision_macro' in metrics
        assert 'recall_macro' in metrics
        assert 'f1_macro' in metrics


class TestConfusionMatrix:
    """Tests for ConfusionMatrix."""
    
    def test_compute(self):
        """Test confusion matrix computation."""
        cm = ConfusionMatrix()
        
        predictions = torch.tensor([0, 1, 1, 0, 1])
        targets = torch.tensor([0, 1, 0, 0, 1])
        
        matrix = cm.compute(predictions, targets)
        
        assert matrix.shape == (2, 2)
        assert matrix[0, 0] + matrix[0, 1] == 2  # Total class 0
        assert matrix[1, 0] + matrix[1, 1] == 2  # Total class 1
    
    def test_per_class_metrics(self):
        """Test per-class metrics."""
        cm = ConfusionMatrix()
        
        matrix = np.array([[8, 2], [1, 9]])
        metrics = cm.get_per_class_metrics(matrix)
        
        assert 'class_0' in metrics
        assert 'class_1' in metrics
        assert 'precision' in metrics['class_0']


class TestModelComparison:
    """Tests for ModelComparison."""
    
    def test_add_model(self):
        """Test adding models."""
        comparison = ModelComparison()
        
        result = ModelResult(
            name="model_1",
            metrics={"accuracy": 0.95, "f1": 0.93},
        )
        comparison.add_model(result)
        
        assert len(comparison.models) == 1
    
    def test_compare_metrics(self):
        """Test metric comparison."""
        comparison = ModelComparison()
        
        comparison.add_model(ModelResult("model_1", {"accuracy": 0.95}))
        comparison.add_model(ModelResult("model_2", {"accuracy": 0.92}))
        
        df = comparison.compare_metrics()
        assert not df.empty
        assert 'model_1' in df.index
        assert 'model_2' in df.index


class TestEvaluator:
    """Tests for Evaluator."""
    
    def test_evaluate(self):
        """Test evaluation."""
        # Create simple model
        class SimpleModel(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.linear = torch.nn.Linear(10, 2)
            
            def forward(self, x, edge_index=None):
                return self.linear(x)
        
        model = SimpleModel()
        
        data = {
            'x': torch.randn(20, 10),
            'y': torch.randint(0, 2, (20,)),
            'edge_index': torch.randint(0, 20, (2, 30)),
        }
        
        evaluator = Evaluator(EvaluationConfig(save_results=False))
        results = evaluator.evaluate(model, data, name="test_model")
        
        assert 'metrics' in results
        assert 'confusion_matrix' in results
        assert 'predictions' in results
        assert 'probabilities' in results