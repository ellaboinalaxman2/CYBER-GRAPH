"""Tests for data loaders."""

import pytest
from pathlib import Path

from src.data import (
    DatasetLoader,
    EventLoader,
    GraphLoader,
    CICIDSLoader,
    SampleLoader,
)
from src.core.exceptions import DataLoaderError


class TestEventLoader:
    """Tests for EventLoader."""
    
    def test_load_sample(self):
        """Test loading sample events."""
        loader = EventLoader()
        
        # Use sample data
        events = loader.load_from_api(source="sample")
        
        # Should have events
        assert len(events) > 0
        assert hasattr(events[0], 'event_id')
    
    def test_get_statistics(self):
        """Test getting event statistics."""
        loader = EventLoader()
        stats = loader.get_statistics()
        assert "total" in stats


class TestGraphLoader:
    """Tests for GraphLoader."""
    
    def test_load_sample_graph(self):
        """Test loading sample graph."""
        loader = GraphLoader()
        
        # Use sample data
        graph = loader.load_from_api(source="sample")
        
        assert graph is not None
        assert len(graph.nodes) > 0
        assert len(graph.edges) > 0
    
    def test_get_statistics(self):
        """Test getting graph statistics."""
        loader = GraphLoader()
        stats = loader.get_statistics()
        assert "nodes" in stats


class TestSampleLoader:
    """Tests for SampleLoader."""
    
    def test_generate_events(self):
        """Test generating sample events."""
        loader = SampleLoader()
        events = loader.generate_events(10)
        
        assert len(events) == 10
        assert all(isinstance(e, EventInput) for e in events)
    
    def test_generate_graph(self):
        """Test generating sample graph."""
        loader = SampleLoader()
        graph = loader.generate_graph(5, 7)
        
        assert len(graph.nodes) == 5
        assert len(graph.edges) == 7
    
    def test_load(self):
        """Test loading sample data."""
        loader = SampleLoader()
        data = loader.load(events_count=20, nodes_count=8, edges_count=10)
        
        assert "events" in data
        assert "graph" in data
        assert len(data["events"]) == 20
        assert len(data["graph"].nodes) == 8


class TestDatasetLoader:
    """Tests for DatasetLoader."""
    
    def test_load_sample(self):
        """Test loading sample dataset."""
        loader = DatasetLoader()
        data = loader.load_dataset("sample", events_count=30, nodes_count=6, edges_count=8)
        
        assert "events" in data
        assert "graph" in data
        assert len(data["events"]) == 30
    
    def test_get_statistics(self):
        """Test getting dataset statistics."""
        loader = DatasetLoader()
        data = loader.load_dataset("sample")
        stats = loader.get_statistics()
        
        assert "total_events" in stats
        assert "total_nodes" in stats