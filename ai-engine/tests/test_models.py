"""Tests for data models."""

import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from src.models import (
    EventInput,
    NodeInput,
    EdgeInput,
    GraphInput,
    AIPredictionRequest,
    AIPredictionResponse,
    NodeFeatures,
    EdgeFeatures,
    EventFeatures,
    TemporalFeatures,
    FeatureSet,
    PredictionResult,
    MLGraph,
)


class TestEventInput:
    """Tests for EventInput model."""
    
    def test_valid_event(self):
        """Test creating a valid event."""
        event = EventInput(
            event_id="EVT-12345678",
            timestamp=datetime.now(timezone.utc),
            event_type="LOGIN_FAILURE",
            source_ip="192.168.1.50",
            destination_ip="192.168.1.20",
            raw_source="firewall",
        )
        assert event.event_id == "EVT-12345678"
        assert event.source_ip == "192.168.1.50"
        assert event.destination_ip == "192.168.1.20"
    
    def test_event_with_optional_fields(self):
        """Test event with optional fields."""
        event = EventInput(
            event_id="EVT-12345678",
            timestamp=datetime.now(timezone.utc),
            event_type="LOGIN_FAILURE",
            raw_source="firewall",
            source_ip="192.168.1.50",
            destination_ip="192.168.1.20",
            source_port=45122,
            destination_port=22,
            protocol="SSH",
            action="DENY",
            severity="LOW",
            user="admin",
            hostname="SERVER-01",
            message="Failed password for admin",
            tags=["authentication", "ssh"],
        )
        assert event.source_port == 45122
        assert event.destination_port == 22
        assert event.protocol == "SSH"
        assert event.action == "DENY"
        assert "authentication" in event.tags


class TestNodeInput:
    """Tests for NodeInput model."""
    
    def test_valid_node(self):
        """Test creating a valid node."""
        node = NodeInput(
            node_id="SERVER-01",
            node_type="device",
            hostname="server-01.example.com",
            ip_address="192.168.1.20",
            device_type="server",
        )
        assert node.node_id == "SERVER-01"
        assert node.hostname == "server-01.example.com"
        assert node.ip_address == "192.168.1.20"
    
    def test_node_with_criticality(self):
        """Test node with criticality score."""
        node = NodeInput(
            node_id="SERVER-01",
            node_type="device",
            criticality=9,
            department="IT Operations",
            owner="IT Team",
        )
        assert node.criticality == 9
        assert node.department == "IT Operations"
        assert node.owner == "IT Team"


class TestEdgeInput:
    """Tests for EdgeInput model."""
    
    def test_valid_edge(self):
        """Test creating a valid edge."""
        edge = EdgeInput(
            source_id="PC-01",
            target_id="SERVER-01",
            relationship_type="CONNECTS_TO",
            properties={"protocol": "SSH", "port": 22},
            weight=1.0,
        )
        assert edge.source_id == "PC-01"
        assert edge.target_id == "SERVER-01"
        assert edge.relationship_type == "CONNECTS_TO"
        assert edge.properties["protocol"] == "SSH"


class TestAIPredictionRequest:
    """Tests for AIPredictionRequest model."""
    
    def test_valid_request(self):
        """Test creating a valid prediction request."""
        request = AIPredictionRequest(
            node_id="SERVER-01",
            neighbors=["PC-01", "SERVER-02", "DB-01"],
            include_explanation=True,
        )
        assert request.node_id == "SERVER-01"
        assert len(request.neighbors) == 3
        assert request.include_explanation is True


class TestFeatureModels:
    """Tests for feature models."""
    
    def test_node_features(self):
        """Test NodeFeatures model."""
        features = NodeFeatures(
            node_id="SERVER-01",
            node_type="device",
            connection_count=15,
            failed_login_count=8,
            successful_login_count=3,
            login_failure_rate=0.73,
            protocol_counts={"SSH": 12, "HTTP": 2},
            criticality=9,
        )
        assert features.connection_count == 15
        assert features.failed_login_count == 8
        assert features.protocol_counts["SSH"] == 12
        assert features.criticality == 9
    
    def test_event_features(self):
        """Test EventFeatures model."""
        features = EventFeatures(
            node_id="SERVER-01",
            total_events=25,
            login_failure_count=8,
            login_success_count=3,
            firewall_deny_count=4,
            alert_count=5,
        )
        assert features.total_events == 25
        assert features.login_failure_count == 8
        assert features.alert_count == 5
    
    def test_temporal_features(self):
        """Test TemporalFeatures model."""
        features = TemporalFeatures(
            node_id="SERVER-01",
            hour_of_day=3,
            day_of_week=0,
            is_weekend=True,
            is_business_hours=False,
            activity_score=0.85,
            event_frequency=2.5,
        )
        assert features.hour_of_day == 3
        assert features.day_of_week == 0
        assert features.is_weekend is True
        assert features.activity_score == 0.85


class TestMLGraph:
    """Tests for MLGraph model."""
    
    def test_valid_graph(self):
        """Test creating a valid ML graph."""
        nodes = [
            GraphNode(
                node_id="SERVER-01",
                node_type="device",
                features=[15.0, 8.0, 5.0],
                label=1,
            ),
            GraphNode(
                node_id="PC-01",
                node_type="device",
                features=[8.0, 2.0, 1.0],
                label=0,
            ),
        ]
        
        edges = [
            GraphEdge(
                source_id="PC-01",
                target_id="SERVER-01",
                edge_type="CONNECTS_TO",
                features=[1.0, 15.0, 0.75],
            ),
        ]
        
        graph = MLGraph(
            nodes=nodes,
            edges=edges,
            graph_id="GRAPH-001",
            num_nodes=2,
            num_edges=1,
            num_features=3,
            num_classes=2,
        )
        
        assert len(graph.nodes) == 2
        assert len(graph.edges) == 1
        assert graph.num_nodes == 2
        assert graph.num_classes == 2