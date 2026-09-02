"""Tests for GraphSAGE models."""

import pytest
import torch
import numpy as np
from datetime import datetime

from src.models import (
    GraphSAGE,
    GraphSAGEConfig,
    NodeClassifier,
    BinaryNodeClassifier,
    ModelFactory,
)


class TestGraphSAGE:
    """Tests for GraphSAGE model."""
    
    def test_forward(self):
        """Test forward pass."""
        config = GraphSAGEConfig(
            in_channels=16,
            hidden_channels=32,
            out_channels=16,
            num_layers=3,
            num_classes=2,
        )
        
        model = GraphSAGE(config)
        
        num_nodes = 10
        x = torch.randn(num_nodes, 16)
        edge_index = torch.randint(0, num_nodes, (2, 20))
        
        output = model(x, edge_index)
        
        assert output.shape == (num_nodes, 2)
    
    def test_get_embeddings(self):
        """Test getting embeddings."""
        config = GraphSAGEConfig(
            in_channels=16,
            hidden_channels=32,
            out_channels=16,
            num_layers=3,
        )
        
        model = GraphSAGE(config)
        
        num_nodes = 10
        x = torch.randn(num_nodes, 16)
        edge_index = torch.randint(0, num_nodes, (2, 20))
        
        embeddings = model.get_embeddings(x, edge_index)
        
        assert embeddings.shape == (num_nodes, 16)
    
    def test_predict_proba(self):
        """Test prediction probabilities."""
        config = GraphSAGEConfig(
            in_channels=16,
            hidden_channels=32,
            out_channels=16,
            num_layers=3,
            num_classes=2,
        )
        
        model = GraphSAGE(config)
        
        num_nodes = 10
        x = torch.randn(num_nodes, 16)
        edge_index = torch.randint(0, num_nodes, (2, 20))
        
        proba = model.predict_proba(x, edge_index)
        
        assert proba.shape == (num_nodes, 2)
        assert torch.allclose(proba.sum(dim=1), torch.ones(num_nodes), rtol=1e-6)
    
    def test_count_parameters(self):
        """Test parameter counting."""
        config = GraphSAGEConfig(
            in_channels=16,
            hidden_channels=32,
            out_channels=16,
            num_layers=3,
        )
        
        model = GraphSAGE(config)
        count = model.count_parameters()
        
        assert count > 0


class TestNodeClassifier:
    """Tests for NodeClassifier."""
    
    def test_forward(self):
        """Test forward pass."""
        classifier = NodeClassifier(
            in_channels=16,
            hidden_channels=32,
            out_channels=16,
            num_layers=3,
            num_classes=3,
        )
        
        num_nodes = 10
        x = torch.randn(num_nodes, 16)
        edge_index = torch.randint(0, num_nodes, (2, 20))
        
        output = classifier(x, edge_index)
        
        assert output.shape == (num_nodes, 3)
    
    def test_predict_proba(self):
        """Test prediction probabilities."""
        classifier = NodeClassifier(
            in_channels=16,
            hidden_channels=32,
            out_channels=16,
            num_layers=3,
            num_classes=2,
        )
        
        num_nodes = 10
        x = torch.randn(num_nodes, 16)
        edge_index = torch.randint(0, num_nodes, (2, 20))
        
        proba = classifier.predict_proba(x, edge_index)
        
        assert proba.shape == (num_nodes, 2)


class TestBinaryNodeClassifier:
    """Tests for BinaryNodeClassifier."""
    
    def test_predict_anomaly_score(self):
        """Test anomaly score prediction."""
        classifier = BinaryNodeClassifier(
            in_channels=16,
            hidden_channels=32,
            out_channels=16,
            num_layers=3,
        )
        
        num_nodes = 10
        x = torch.randn(num_nodes, 16)
        edge_index = torch.randint(0, num_nodes, (2, 20))
        
        scores = classifier.predict_anomaly_score(x, edge_index)
        
        assert scores.shape == (num_nodes,)
        assert torch.all((scores >= 0) & (scores <= 1))


class TestModelFactory:
    """Tests for ModelFactory."""
    
    def test_create_graphsage(self):
        """Test creating GraphSAGE model."""
        config = {
            "in_channels": 16,
            "hidden_channels": 32,
            "out_channels": 16,
            "num_layers": 3,
            "num_classes": 2,
        }
        
        model = ModelFactory.create("graphsage", config)
        
        assert isinstance(model, GraphSAGE)
    
    def test_create_classifier(self):
        """Test creating NodeClassifier."""
        config = {
            "in_channels": 16,
            "hidden_channels": 32,
            "out_channels": 16,
            "num_layers": 3,
            "num_classes": 2,
        }
        
        model = ModelFactory.create("node_classifier", config)
        
        assert isinstance(model, NodeClassifier)
    
    def test_default_graphsage(self):
        """Test creating default GraphSAGE."""
        model = ModelFactory.create_default_graphsage(
            in_channels=16,
            num_classes=2,
        )
        
        assert isinstance(model, GraphSAGE)
        assert model.config.in_channels == 16
        assert model.config.num_classes == 2