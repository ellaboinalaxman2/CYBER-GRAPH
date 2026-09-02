"""Tests for reconstruction module."""

import pytest
from datetime import datetime, timedelta

from src.reconstruction.graph_traversal import GraphTraversal
from src.reconstruction.sequence_analyzer import SequenceAnalyzer
from src.reconstruction.path_builder import PathBuilder
from src.reconstruction.attack_reconstructor import AttackReconstructor


class TestGraphTraversal:
    """Tests for GraphTraversal."""
    
    def test_build_graph(self):
        """Test building a graph."""
        traversal = GraphTraversal()
        
        nodes = [
            {"id": "A", "type": "device"},
            {"id": "B", "type": "device"},
            {"id": "C", "type": "device"},
        ]
        edges = [
            {"source_id": "A", "target_id": "B"},
            {"source_id": "B", "target_id": "C"},
        ]
        
        traversal.build_graph(nodes, edges)
        
        assert traversal.graph.number_of_nodes() == 3
        assert traversal.graph.number_of_edges() == 2
    
    def test_find_path(self):
        """Test finding paths."""
        traversal = GraphTraversal()
        
        nodes = [{"id": f"N{i}", "type": "device"} for i in range(5)]
        edges = [
            {"source_id": "N0", "target_id": "N1"},
            {"source_id": "N1", "target_id": "N2"},
            {"source_id": "N2", "target_id": "N3"},
            {"source_id": "N3", "target_id": "N4"},
        ]
        
        traversal.build_graph(nodes, edges)
        paths = traversal.find_path("N0", "N4")
        
        assert len(paths) > 0
        assert paths[0][0] == "N0"
        assert paths[0][-1] == "N4"
    
    def test_get_neighbors(self):
        """Test getting neighbors."""
        traversal = GraphTraversal()
        
        nodes = [{"id": "A"}, {"id": "B"}, {"id": "C"}]
        edges = [
            {"source_id": "A", "target_id": "B"},
            {"source_id": "B", "target_id": "C"},
        ]
        
        traversal.build_graph(nodes, edges)
        neighbors = traversal.get_neighbors("B")
        
        assert "A" in neighbors["in"]
        assert "C" in neighbors["out"]


class TestSequenceAnalyzer:
    """Tests for SequenceAnalyzer."""
    
    def test_analyze_brute_force(self):
        """Test brute force pattern detection."""
        analyzer = SequenceAnalyzer()
        
        now = datetime.utcnow()
        events = []
        for i in range(5):
            events.append({
                "event_id": f"EVT-{i}",
                "timestamp": (now + timedelta(seconds=i * 10)).isoformat() + "Z",
                "event_type": "LOGIN_FAILURE",
                "source_ip": "192.168.1.50",
                "raw_source": "test",
            })
        events.append({
            "event_id": "EVT-5",
            "timestamp": (now + timedelta(seconds=50)).isoformat() + "Z",
            "event_type": "LOGIN_SUCCESS",
            "source_ip": "192.168.1.50",
            "raw_source": "test",
        })
        
        result = analyzer.analyze(events)
        
        assert result["total_events"] == 6
        assert result["source_groups"] > 0
        assert "overall_score" in result["sequence_scores"]


class TestAttackReconstructor:
    """Tests for AttackReconstructor."""
    
    def test_reconstruct(self):
        """Test attack reconstruction."""
        reconstructor = AttackReconstructor()
        
        events = [
            {"event_id": "EVT-1", "source_ip": "A", "destination_ip": "B"},
            {"event_id": "EVT-2", "source_ip": "B", "destination_ip": "C"},
        ]
        
        result = reconstructor.reconstruct(events)
        
        assert result["status"] == "success"
        assert result["events_processed"] == 2
        assert "attack_path" in result