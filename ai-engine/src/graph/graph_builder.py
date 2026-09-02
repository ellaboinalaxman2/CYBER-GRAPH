"""Graph builder for Member 3 - AI Engine."""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from collections import defaultdict
import networkx as nx

from src.core.logging import get_logger
from src.core.exceptions import GraphConstructionError
from src.models.input_schemas import NodeInput, EdgeInput, GraphInput
from src.models.graph_schemas import MLGraph, GraphNode, GraphEdge
from src.graph.node_encoder import NodeEncoder
from src.graph.edge_encoder import EdgeEncoder


class GraphBuilder:
    """
    Builds ML-ready graphs from cybersecurity data.
    
    Features:
    - Node and edge encoding
    - Feature extraction
    - Graph validation
    - Graph statistics
    """
    
    def __init__(self):
        """Initialize the graph builder."""
        self.logger = get_logger("graph.graph_builder")
        self.node_encoder = NodeEncoder()
        self.edge_encoder = EdgeEncoder()
        self._stats = {
            "graphs_built": 0,
            "total_nodes": 0,
            "total_edges": 0,
            "total_features": 0,
        }
    
    def build_graph(
        self,
        nodes: List[NodeInput],
        edges: List[EdgeInput],
        labels: Optional[List[int]] = None,
    ) -> MLGraph:
        """
        Build an ML graph from nodes and edges.
        
        Args:
            nodes: List of NodeInput objects
            edges: List of EdgeInput objects
            labels: List of node labels (optional)
            
        Returns:
            MLGraph: ML-ready graph
        """
        self.logger.info(f"Building ML graph with {len(nodes)} nodes and {len(edges)} edges")
        
        # Validate inputs
        self._validate_inputs(nodes, edges)
        
        # Encode nodes
        node_features_df = self.node_encoder.encode_nodes(nodes)
        
        # Encode edges
        edge_features_df = self.edge_encoder.encode_edges(edges)
        
        # Build graph
        ml_graph = self._build_ml_graph(
            nodes,
            edges,
            node_features_df,
            edge_features_df,
            labels,
        )
        
        self._stats["graphs_built"] += 1
        self._stats["total_nodes"] = len(nodes)
        self._stats["total_edges"] = len(edges)
        self._stats["total_features"] = len(node_features_df.columns)
        
        self.logger.info(f"ML graph built: {len(nodes)} nodes, {len(edges)} edges")
        return ml_graph
    
    def _validate_inputs(self, nodes: List[NodeInput], edges: List[EdgeInput]) -> None:
        """Validate inputs."""
        if not nodes:
            raise GraphConstructionError("No nodes provided")
        
        # Check for duplicate node IDs
        node_ids = [n.node_id for n in nodes]
        if len(node_ids) != len(set(node_ids)):
            raise GraphConstructionError("Duplicate node IDs found")
        
        # Check that all edge endpoints exist
        edge_source_ids = [e.source_id for e in edges]
        edge_target_ids = [e.target_id for e in edges]
        all_endpoint_ids = set(edge_source_ids + edge_target_ids)
        
        missing_nodes = all_endpoint_ids - set(node_ids)
        if missing_nodes:
            self.logger.warning(f"Missing nodes for edges: {missing_nodes}")
    
    def _build_ml_graph(
        self,
        nodes: List[NodeInput],
        edges: List[EdgeInput],
        node_features_df: pd.DataFrame,
        edge_features_df: pd.DataFrame,
        labels: Optional[List[int]] = None,
    ) -> MLGraph:
        """
        Build MLGraph object.
        
        Args:
            nodes: List of NodeInput objects
            edges: List of EdgeInput objects
            node_features_df: Encoded node features
            edge_features_df: Encoded edge features
            labels: Node labels (optional)
            
        Returns:
            MLGraph: ML-ready graph
        """
        # Create node ID to index mapping
        node_id_to_idx = {node.node_id: idx for idx, node in enumerate(nodes)}
        
        # Build GraphNodes
        graph_nodes = []
        for idx, node in enumerate(nodes):
            # Get features
            if node.node_id in node_features_df.index:
                features = node_features_df.loc[node.node_id].values.tolist()
            else:
                features = []
            
            # Get label
            label = labels[idx] if labels and idx < len(labels) else None
            
            graph_node = GraphNode(
                node_id=node.node_id,
                node_type=node.node_type,
                features=features,
                label=label,
                metadata={
                    "hostname": node.hostname,
                    "ip_address": node.ip_address,
                    "device_type": node.device_type,
                    "criticality": node.criticality,
                },
            )
            graph_nodes.append(graph_node)
        
        # Build GraphEdges
        graph_edges = []
        for edge in edges:
            # Get features
            edge_key = (edge.source_id, edge.target_id)
            if edge_key in edge_features_df.index:
                features = edge_features_df.loc[edge_key].values.tolist()
            else:
                features = []
            
            graph_edge = GraphEdge(
                source_id=edge.source_id,
                target_id=edge.target_id,
                edge_type=edge.relationship_type,
                features=features,
                weight=edge.weight or 1.0,
                metadata=edge.properties,
            )
            graph_edges.append(graph_edge)
        
        # Create MLGraph
        ml_graph = MLGraph(
            nodes=graph_nodes,
            edges=graph_edges,
            graph_id=f"MLGRAPH-{pd.Timestamp.utcnow().timestamp()}",
            num_nodes=len(graph_nodes),
            num_edges=len(graph_edges),
            num_features=len(graph_nodes[0].features) if graph_nodes else 0,
            num_classes=len(set([n.label for n in graph_nodes if n.label is not None])) if labels else 0,
            is_directed=True,
            is_weighted=True,
            metadata={
                "node_encoder": self.node_encoder.get_statistics(),
                "edge_encoder": self.edge_encoder.get_statistics(),
                "timestamp": pd.Timestamp.utcnow().isoformat(),
            },
        )
        
        return ml_graph
    
    def build_from_graph_input(self, graph_input: GraphInput) -> MLGraph:
        """
        Build ML graph from GraphInput.
        
        Args:
            graph_input: GraphInput object
            
        Returns:
            MLGraph: ML-ready graph
        """
        return self.build_graph(
            nodes=graph_input.nodes,
            edges=graph_input.edges,
        )
    
    def build_from_networkx(self, G: nx.Graph) -> MLGraph:
        """
        Build ML graph from NetworkX graph.
        
        Args:
            G: NetworkX graph
            
        Returns:
            MLGraph: ML-ready graph
        """
        nodes = []
        edges = []
        
        # Extract nodes
        for node_id, data in G.nodes(data=True):
            node = NodeInput(
                node_id=str(node_id),
                node_type=data.get('type', 'device'),
                device_type=data.get('device_type'),
                criticality=data.get('criticality', 1),
                properties=data.get('properties', {}),
            )
            nodes.append(node)
        
        # Extract edges
        for u, v, data in G.edges(data=True):
            edge = EdgeInput(
                source_id=str(u),
                target_id=str(v),
                relationship_type=data.get('type', 'CONNECTS_TO'),
                properties=data.get('properties', {}),
                weight=data.get('weight', 1.0),
            )
            edges.append(edge)
        
        return self.build_graph(nodes, edges)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get graph building statistics."""
        return {
            **self._stats,
            "node_encoder": self.node_encoder.get_statistics(),
            "edge_encoder": self.edge_encoder.get_statistics(),
        }