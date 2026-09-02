"""Tests for feature engineering module."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.features import (
    NodeFeatureExtractor,
    EdgeFeatureExtractor,
    EventFeatureExtractor,
    TemporalFeatureExtractor,
    FeatureBuilder,
    FeatureNormalizer,
)
from src.models.input_schemas import NodeInput, EdgeInput, EventInput


class TestNodeFeatureExtractor:
    """Tests for NodeFeatureExtractor."""
    
    def test_extract_features(self):
        """Test extracting node features."""
        extractor = NodeFeatureExtractor()
        
        nodes = [
            NodeInput(node_id="NODE-1", node_type="device", criticality=9),
            NodeInput(node_id="NODE-2", node_type="server", criticality=5),
        ]
        
        edges = [
            EdgeInput(source_id="NODE-1", target_id="NODE-2", relationship_type="CONNECTS_TO"),
        ]
        
        events = [
            EventInput(
                event_id="EVT-001",
                timestamp=datetime.utcnow(),
                event_type="LOGIN_FAILURE",
                source_ip="NODE-1",
                raw_source="test",
            ),
            EventInput(
                event_id="EVT-002",
                timestamp=datetime.utcnow(),
                event_type="ALERT",
                source_ip="NODE-1",
                raw_source="test",
            ),
        ]
        
        df = extractor.extract_features(nodes, edges, events)
        
        assert not df.empty
        assert len(df) == len(nodes)
        assert 'degree' in df.columns
        assert 'criticality' in df.columns
        assert 'total_events' in df.columns
        assert 'risk_score' in df.columns


class TestEdgeFeatureExtractor:
    """Tests for EdgeFeatureExtractor."""
    
    def test_extract_features(self):
        """Test extracting edge features."""
        extractor = EdgeFeatureExtractor()
        
        edges = [
            EdgeInput(
                source_id="NODE-1",
                target_id="NODE-2",
                relationship_type="CONNECTS_TO",
                properties={"protocol": "SSH", "port": 22, "frequency": 10},
            ),
        ]
        
        df = extractor.extract_features(edges)
        
        assert not df.empty
        assert len(df) == len(edges)
        assert 'weight' in df.columns
        assert 'protocol_encoded' in df.columns
        assert 'is_common_port' in df.columns


class TestEventFeatureExtractor:
    """Tests for EventFeatureExtractor."""
    
    def test_extract_features(self):
        """Test extracting event features."""
        extractor = EventFeatureExtractor()
        
        events = []
        for i in range(10):
            events.append(
                EventInput(
                    event_id=f"EVT-{i:03d}",
                    timestamp=datetime.utcnow() - timedelta(minutes=i),
                    event_type=np.random.choice(["LOGIN", "LOGOUT", "ALERT"]),
                    severity=np.random.choice(["INFO", "LOW", "HIGH"]),
                    protocol=np.random.choice(["TCP", "UDP", "HTTP"]),
                    action=np.random.choice(["ALLOW", "DENY"]),
                    raw_source="test",
                )
            )
        
        df = extractor.extract_features(events)
        
        assert not df.empty
        assert 'total_events' in df.columns
        assert 'risk_score' in df.columns


class TestTemporalFeatureExtractor:
    """Tests for TemporalFeatureExtractor."""
    
    def test_extract_features(self):
        """Test extracting temporal features."""
        extractor = TemporalFeatureExtractor()
        
        events = []
        for i in range(20):
            events.append(
                EventInput(
                    event_id=f"EVT-{i:03d}",
                    timestamp=datetime.utcnow() - timedelta(minutes=i * 5),
                    event_type="LOGIN",
                    raw_source="test",
                )
            )
        
        df = extractor.extract_features(events)
        
        assert not df.empty
        assert 'total_events' in df.columns
        assert 'events_per_minute' in df.columns
        assert 'business_hours_ratio' in df.columns


class TestFeatureBuilder:
    """Tests for FeatureBuilder."""
    
    def test_build_features(self):
        """Test building complete features."""
        builder = FeatureBuilder()
        
        nodes = [
            NodeInput(node_id="NODE-1", node_type="device", criticality=9),
            NodeInput(node_id="NODE-2", node_type="server", criticality=5),
            NodeInput(node_id="NODE-3", node_type="workstation", criticality=3),
        ]
        
        edges = [
            EdgeInput(source_id="NODE-1", target_id="NODE-2", relationship_type="CONNECTS_TO"),
            EdgeInput(source_id="NODE-2", target_id="NODE-3", relationship_type="CONNECTS_TO"),
        ]
        
        events = []
        for i in range(10):
            events.append(
                EventInput(
                    event_id=f"EVT-{i:03d}",
                    timestamp=datetime.utcnow() - timedelta(minutes=i),
                    event_type=np.random.choice(["LOGIN_SUCCESS", "LOGIN_FAILURE", "ALERT"]),
                    severity=np.random.choice(["INFO", "LOW", "HIGH"]),
                    raw_source="test",
                    source_ip=f"NODE-{np.random.choice([1, 2, 3])}",
                )
            )
        
        result = builder.build_features(nodes, edges, events, normalize=True)
        
        assert result["status"] == "completed"
        assert "combined" in result["features"]
        assert "normalized" in result["features"]
        assert "metadata" in result


class TestFeatureNormalizer:
    """Tests for FeatureNormalizer."""
    
    def test_normalize(self):
        """Test feature normalization."""
        normalizer = FeatureNormalizer(method='standard')
        
        df = pd.DataFrame({
            'feature1': [1, 2, 3, 4, 5],
            'feature2': [10, 20, 30, 40, 50],
            'feature3': [100, 200, 300, 400, 500],
        })
        
        normalized = normalizer.normalize(df)
        
        assert normalized.shape == df.shape
        assert normalized.mean().abs().max() < 0.1  # Should have mean ~0
    
    def test_transform(self):
        """Test transforming new data."""
        normalizer = FeatureNormalizer(method='standard')
        
        df_train = pd.DataFrame({'feature': [1, 2, 3, 4, 5]})
        normalizer.normalize(df_train)
        
        df_test = pd.DataFrame({'feature': [6, 7, 8]})
        transformed = normalizer.transform(df_test)
        
        assert transformed.shape == df_test.shape