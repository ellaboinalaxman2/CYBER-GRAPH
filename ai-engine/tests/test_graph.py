"""Tests for graph construction module."""

import pytest
import torch
import numpy as np
from datetime import datetime

from src.models.input_schemas import NodeInput, EdgeInput
from src.models.graph_schemas import GraphSamplingConfig
from src.graph import (
    GraphBuilder,
    GraphConverter,
    NodeEncoder,
    EdgeEncoder,
    GraphSampler,
)


class TestNodeEncoder:
    """Tests for NodeEncoder."""
    
    def test_encode_nodes(self):
        """Test encoding nodes."""
        encoder = NodeEncoder()
        
        nodes = [
            NodeInput(node_id="NODE-1", node_type="device", criticality=9),
            NodeInput(node_id="NODE-2", node_type="server", criticality=5),
            NodeInput(node_id="NODE-3", node_type="workstation", criticality=3),
        ]
        
        df = encoder.encode_nodes(nodes)
        
        assert not df.empty
        assert len(df) == len(nodes)
        assert 'criticality' in df.columns
        assert 'node_type_device' in df.columns


class TestEdgeEncoder:
    """Tests for EdgeEncoder."""
    
    def test_encode_edges(self):
        """Test encoding edges."""
        encoder = EdgeEncoder()
        
        edges = [
            EdgeInput(
                source_id="NODE-1",
                target_id="NODE-2",
                relationship_type="CONNECTS_TO",
                properties={"protocol": "SSH", "port": 22},
            ),
            EdgeInput(
                source_id="NODE-2",
                target_id="NODE-3",
                relationship_type="ACCESSES",
                properties={"protocol": "HTTP", "port": 80},
            ),
        ]
        
        df = encoder.encode_edges(edges)
        
        assert not df.empty
        assert len(df) == len(edges)
        assert 'weight' in df.columns
        assert 'protocol_SSH' in df.columns


class TestGraphBuilder:
    """Tests for GraphBuilder."""
    
    def test_build_graph(self):
        """Test building an ML graph."""
        builder = GraphBuilder()
        
        nodes = [
            NodeInput(node_id="NODE-1", node_type="device", criticality=9),
            NodeInput(node_id="NODE-2", node_type="server", criticality=5),
            NodeInput(node_id="NODE-3", node_type="workstation", criticality=3),
        ]
        
        edges = [
            EdgeInput(source_id="NODE-1", target_id="NODE-2", relationship_type="CONNECTS_TO"),
            EdgeInput(source_id="NODE-2", target_id="NODE-3", relationship_type="CONNECTS_TO"),
        ]
        
        labels = [0, 1, 0]
        
        ml_graph = builder.build_graph(nodes, edges, labels)
        
        assert ml_graph.num_nodes == len(nodes)
        assert ml_graph.num_edges == len(edges)
        assert ml_graph.num_features > 0
        assert ml_graph.num_classes == 2
    
    def test_build_from_graph_input(self):
        """Test building from GraphInput."""
        builder = GraphBuilder()
        
        nodes = [
            NodeInput(node_id="NODE-1", node_type="device"),
            NodeInput(node_id="NODE-2", node_type="server"),
        ]
        edges = [
            EdgeInput(source_id="NODE-1", target_id="NODE-2", relationship_type="CONNECTS_TO"),
        ]
        
        graph_input = GraphInput(nodes=nodes, edges=edges)
        ml_graph = builder.build_from_graph_input(graph_input)
        
        assert ml_graph.num_nodes == 2
        assert ml_graph.num_edges == 1


class TestGraphConverter:
    """Tests for GraphConverter."""
    
    def test_convert(self):
        """Test converting to PyTorch Geometric."""
        builder = GraphBuilder()
        converter = GraphConverter()
        
        nodes = [
            NodeInput(node_id="NODE-1", node_type="device", criticality=9),
            NodeInput(node_id="NODE-2", node_type="server", criticality=5),
        ]
        edges = [
            EdgeInput(source_id="NODE-1", target_id="NODE-2", relationship_type="CONNECTS_TO"),
        ]
        
        ml_graph = builder.build_graph(nodes, edges)
        data = converter.convert(ml_graph)
        
        assert isinstance(data, torch_geometric.data.Data)  # noqa: F821
        assert data.num_nodes == len(nodes)
        assert data.edge_index.size(1) == len(edges)
        assert data.x is not None


class TestGraphSampler:
    """Tests for GraphSampler."""
    
    def test_random_sample(self):
        """Test random sampling."""
        builder = GraphBuilder()
        converter = GraphConverter()
        sampler = GraphSampler()
        
        # Create larger graph
        nodes = [NodeInput(node_id=f"NODE-{i}", node_type="device") for i in range(20)]
        edges = [
            EdgeInput(source_id=f"NODE-{i}", target_id=f"NODE-{i+1}", relationship_type="CONNECTS_TO")
            for i in range(15)
        ]
        
        ml_graph = builder.build_graph(nodes, edges)
        data = converter.convert(ml_graph)
        
        config = GraphSamplingConfig(
            sampling_strategy="random",
            sample_size=10,
            neighbor_samples=[5, 5],
        )
        
        sampled_data = sampler.sample(data, config)
        
        assert sampled_data.num_nodes <= 10
        assert sampled_data.edge_index.size(1) <= data.edge_index.size(1)