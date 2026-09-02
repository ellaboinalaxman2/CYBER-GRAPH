"""Tests for preprocessing module."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime

from src.preprocessing import (
    DataCleaner,
    EventPreprocessor,
    GraphPreprocessor,
    LabelProcessor,
    PreprocessingPipeline,
)
from src.models.input_schemas import GraphInput, NodeInput, EdgeInput


class TestDataCleaner:
    """Tests for DataCleaner."""
    
    def test_clean_dataframe(self):
        """Test cleaning a DataFrame."""
        cleaner = DataCleaner()
        
        # Create dirty DataFrame
        df = pd.DataFrame({
            'id': [1, 2, 3, 3, 4, 5],
            'value': [10, None, 30, 30, 50, -5],
            'count': [100, 200, 300, 300, -10, 600],
        })
        
        cleaned = cleaner.clean_dataframe(df)
        
        assert len(cleaned) < len(df)  # Duplicates removed
        assert cleaned['value'].isnull().sum() == 0  # Missing values filled
        assert (cleaned['count'] >= 0).all()  # Negative values fixed
        assert cleaner.get_statistics()["duplicates_removed"] > 0
    
    def test_clean_events(self):
        """Test cleaning events."""
        cleaner = DataCleaner()
        
        events = [
            {"id": 1, "event_type": "LOGIN", "severity": "HIGH"},
            {"id": 2, "event_type": None, "severity": "LOW"},
            {"id": 3, "event_type": "LOGOUT", "severity": None},
        ]
        
        cleaned = cleaner.clean_events(events)
        assert len(cleaned) == 3
        assert all("event_type" in e for e in cleaned)
        assert all("severity" in e for e in cleaned)


class TestEventPreprocessor:
    """Tests for EventPreprocessor."""
    
    def test_preprocess_events(self):
        """Test preprocessing events."""
        preprocessor = EventPreprocessor()
        
        events = [
            {
                "event_id": f"EVT-{i:08d}",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "event_type": np.random.choice(["LOGIN", "LOGOUT", "ALERT"]),
                "severity": np.random.choice(["INFO", "LOW", "HIGH"]),
                "protocol": np.random.choice(["TCP", "UDP", "HTTP"]),
                "source_port": np.random.randint(1024, 65535),
                "destination_port": np.random.choice([22, 80, 443, 3389]),
                "action": np.random.choice(["ALLOW", "DENY", "BLOCK"]),
            }
            for i in range(10)
        ]
        
        features = preprocessor.preprocess(events)
        assert not features.empty
        assert len(features) == len(events)
        assert "severity_score" in features.columns
        assert "protocol_TCP" in features.columns or "protocol_HTTP" in features.columns
    
    def test_aggregate_events(self):
        """Test aggregating events."""
        preprocessor = EventPreprocessor()
        
        events = [
            {
                "event_id": f"EVT-{i:08d}",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "event_type": "LOGIN",
                "severity": "INFO",
                "source_ip": f"192.168.1.{i+1}",
                "destination_ip": "192.168.1.100",
            }
            for i in range(20)
        ]
        
        aggregated = preprocessor.aggregate_events(events, window_minutes=5)
        assert len(aggregated) > 0
        assert "total_events" in aggregated[0]


class TestGraphPreprocessor:
    """Tests for GraphPreprocessor."""
    
    def test_preprocess_graph(self):
        """Test preprocessing a graph."""
        preprocessor = GraphPreprocessor()
        
        # Create test graph
        nodes = [
            NodeInput(node_id="NODE-1", node_type="device"),
            NodeInput(node_id="NODE-2", node_type="device"),
            NodeInput(node_id="NODE-3", node_type="server"),
        ]
        
        edges = [
            EdgeInput(source_id="NODE-1", target_id="NODE-2", relationship_type="CONNECTS_TO"),
            EdgeInput(source_id="NODE-2", target_id="NODE-3", relationship_type="CONNECTS_TO"),
        ]
        
        graph = GraphInput(nodes=nodes, edges=edges)
        
        result = preprocessor.preprocess(graph)
        
        assert "node_features" in result
        assert "edge_features" in result
        assert "statistics" in result
        assert result["statistics"]["num_nodes"] == 3
        assert result["statistics"]["num_edges"] == 2
    
    def test_sample_graph(self):
        """Test sampling a graph."""
        preprocessor = GraphPreprocessor()
        
        # Create large test graph
        nodes = [NodeInput(node_id=f"NODE-{i}", node_type="device") for i in range(10)]
        edges = [
            EdgeInput(
                source_id=f"NODE-{i}",
                target_id=f"NODE-{i+1}",
                relationship_type="CONNECTS_TO"
            )
            for i in range(8)
        ]
        
        graph = GraphInput(nodes=nodes, edges=edges)
        
        sampled = preprocessor.sample_graph(graph, sample_size=5)
        assert len(sampled.nodes) == 5


class TestLabelProcessor:
    """Tests for LabelProcessor."""
    
    def test_create_mapping(self):
        """Test creating label mapping."""
        processor = LabelProcessor()
        labels = ["normal", "attack", "normal", "attack", "malware"]
        
        mapping = processor.create_mapping(labels)
        assert len(mapping) == 3
        assert "normal" in mapping
        assert "attack" in mapping
        assert "malware" in mapping
    
    def test_encode_labels(self):
        """Test encoding labels."""
        processor = LabelProcessor()
        labels = ["normal", "attack", "normal"]
        
        encoded = processor.encode_labels(labels)
        assert len(encoded) == 3
        assert encoded[0] == encoded[2]  # Both "normal"
        assert encoded[0] != encoded[1]  # "normal" != "attack"
    
    def test_balance_labels(self):
        """Test balancing labels."""
        processor = LabelProcessor()
        labels = [0, 0, 0, 1]  # 3 normal, 1 attack
        
        balanced = processor.balance_labels(labels, strategy='oversample')
        assert len(balanced) >= len(labels)


class TestPreprocessingPipeline:
    """Tests for PreprocessingPipeline."""
    
    def test_full_pipeline(self):
        """Test the full preprocessing pipeline."""
        pipeline = PreprocessingPipeline()
        
        # Create test data
        events = [
            {
                "event_id": f"EVT-{i:08d}",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "event_type": np.random.choice(["LOGIN", "LOGOUT", "ALERT"]),
                "severity": np.random.choice(["INFO", "LOW", "HIGH"]),
            }
            for i in range(10)
        ]
        
        labels = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
        
        result = pipeline.process(
            events=events,
            labels=labels,
            clean_data=True,
        )
        
        assert "events" in result
        assert "event_features" in result
        assert "labels" in result
        assert "encoded_labels" in result
        assert "combined_features" in result
        
        stats = pipeline.get_statistics()
        assert "pipeline" in stats
        assert stats["pipeline"]["pipeline_complete"] is True