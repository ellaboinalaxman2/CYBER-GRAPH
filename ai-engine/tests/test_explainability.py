"""Tests for explainability module."""

import pytest
import torch
import numpy as np
from datetime import datetime

from src.explainability import (
    FeatureImportance,
    NodeExplanation,
    PredictionExplanation,
    ExplanationVisualizer,
)


class TestFeatureImportance:
    """Tests for FeatureImportance."""
    
    def test_permutation_importance(self):
        """Test permutation importance."""
        class SimpleModel(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.linear = torch.nn.Linear(5, 2)
            
            def forward(self, x, edge_index=None):
                return self.linear(x)
        
        model = SimpleModel()
        x = torch.randn(10, 5)
        y = torch.randint(0, 2, (10,))
        
        importance = FeatureImportance(method='permutation')
        scores = importance.calculate(model, x, y)
        
        assert len(scores) == 5
        assert sum(scores.values()) > 0
    
    def test_gradient_importance(self):
        """Test gradient importance."""
        class SimpleModel(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.linear = torch.nn.Linear(5, 2)
            
            def forward(self, x, edge_index=None):
                return self.linear(x)
        
        model = SimpleModel()
        x = torch.randn(10, 5)
        
        importance = FeatureImportance(method='gradient')
        scores = importance.calculate(model, x, None)
        
        assert len(scores) == 5


class TestNodeExplanation:
    """Tests for NodeExplanation."""
    
    def test_explain(self):
        """Test node explanation."""
        class SimpleModel(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.linear = torch.nn.Linear(5, 2)
            
            def forward(self, x, edge_index=None):
                return self.linear(x)
        
        model = SimpleModel()
        x = torch.randn(10, 5)
        
        explainer = NodeExplanation()
        result = explainer.explain(
            model=model,
            x=x,
            node_id="NODE-1",
            node_idx=0,
        )
        
        assert result.node_id == "NODE-1"
        assert result.prediction in ["NORMAL", "ATTACK"]
        assert len(result.reasons) > 0


class TestPredictionExplanation:
    """Tests for PredictionExplanation."""
    
    def test_explain(self):
        """Test prediction explanation."""
        class SimpleModel(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.linear = torch.nn.Linear(5, 2)
            
            def forward(self, x, edge_index=None):
                return self.linear(x)
        
        model = SimpleModel()
        x = torch.randn(10, 5)
        
        explainer = PredictionExplanation()
        result = explainer.explain(
            model=model,
            x=x,
            node_id="NODE-1",
            node_idx=0,
        )
        
        assert result.node_id == "NODE-1"
        assert result.summary is not None
        assert len(result.recommendations) > 0


class TestExplanationVisualizer:
    """Tests for ExplanationVisualizer."""
    
    def test_plot_feature_importance(self):
        """Test feature importance plot."""
        visualizer = ExplanationVisualizer()
        
        feature_importance = {
            "feature_1": 0.3,
            "feature_2": 0.25,
            "feature_3": 0.2,
            "feature_4": 0.15,
            "feature_5": 0.1,
        }
        
        # Should not raise exception
        visualizer.plot_feature_importance(
            feature_importance,
            title="Test",
            return_base64=True,
        )
    
    def test_plot_dashboard(self):
        """Test explanation dashboard."""
        visualizer = ExplanationVisualizer()
        
        visualizer.plot_explanation_dashboard(
            node_id="NODE-1",
            prediction="ATTACK",
            confidence=0.94,
            anomaly_score=0.94,
            feature_importance={"feature_1": 0.3, "feature_2": 0.25},
            reasons=["Test reason 1", "Test reason 2"],
            recommendations=["Recommendation 1", "Recommendation 2"],
            return_base64=True,
        )