"""Graph preprocessor for Member 3 - AI Engine."""

import networkx as nx
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from collections import Counter

from src.core.logging import get_logger
from src.core.exceptions import PreprocessingError
from src.models.input_schemas import GraphInput, NodeInput, EdgeInput


class GraphPreprocessor:
    """
    Preprocesses graph data for ML.
    
    Features:
    - Graph cleaning
    - Node feature extraction
    - Edge feature extraction
    - Graph statistics
    - Graph sampling
    """
    
    def __init__(self):
        """Initialize the graph preprocessor."""
        self.logger = get_logger("preprocessing.graph_preprocessor")
        self._stats = {
            "nodes_processed": 0,
            "edges_processed": 0,
            "features_extracted": 0,
            "graph_connected": False,
        }
    
    def preprocess(self, graph: GraphInput) -> Dict[str, Any]:
        """
        Preprocess a graph for ML.
        
        Args:
            graph: Input graph
            
        Returns:
            Dict[str, Any]: Preprocessed graph data
        """
        self.logger.info(f"Preprocessing graph with {len(graph.nodes)} nodes and {len(graph.edges)} edges")
        
        # Extract features
        node_features = self._extract_node_features(graph)
        edge_features = self._extract_edge_features(graph)
        
        # Calculate graph statistics
        stats = self._calculate_statistics(graph)
        
        self._stats["nodes_processed"] = len(graph.nodes)
        self._stats["edges_processed"] = len(graph.edges)
        self._stats["features_extracted"] = len(node_features.columns) if not node_features.empty else 0
        
        return {
            "node_features": node_features,
            "edge_features": edge_features,
            "statistics": stats,
            "node_ids": [n.node_id for n in graph.nodes],
            "edge_list": [(e.source_id, e.target_id, e.relationship_type) for e in graph.edges],
        }
    
    def _extract_node_features(self, graph: GraphInput) -> pd.DataFrame:
        """Extract features from graph nodes."""
        features = []
        
        for node in graph.nodes:
            # Basic node features
            node_data = {
                'node_id': node.node_id,
                'node_type': node.node_type,
                'criticality': node.criticality or 0,
                'degree': 0,  # Will be calculated
                'is_server': 1 if node.device_type and 'server' in node.device_type.lower() else 0,
                'is_firewall': 1 if node.device_type and 'firewall' in node.device_type.lower() else 0,
                'is_database': 1 if node.device_type and 'database' in node.device_type.lower() else 0,
            }
            
            # Department encoding
            if node.department:
                dept_encoding = {
                    'Engineering': 1,
                    'IT': 2,
                    'Finance': 3,
                    'HR': 4,
                    'Security': 5,
                }
                node_data['department_encoded'] = dept_encoding.get(node.department, 0)
            
            features.append(node_data)
        
        # Convert to DataFrame
        df = pd.DataFrame(features)
        
        # Calculate degree (if edge list is available)
        if graph.edges:
            # Count degrees
            degree_counter = Counter()
            for edge in graph.edges:
                degree_counter[edge.source_id] += 1
                degree_counter[edge.target_id] += 1
            
            df['degree'] = df['node_id'].map(degree_counter).fillna(0)
        
        # Normalize features
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col != 'node_id':
                max_val = df[col].max()
                if max_val > 0:
                    df[col] = df[col] / max_val
        
        return df
    
    def _extract_edge_features(self, graph: GraphInput) -> pd.DataFrame:
        """Extract features from graph edges."""
        if not graph.edges:
            return pd.DataFrame()
        
        features = []
        
        for edge in graph.edges:
            edge_data = {
                'source': edge.source_id,
                'target': edge.target_id,
                'relationship_type': edge.relationship_type,
                'weight': edge.weight or 1.0,
            }
            
            # Protocol encoding
            protocol = edge.properties.get('protocol', '')
            if protocol:
                proto_encoding = {
                    'TCP': 1,
                    'UDP': 2,
                    'ICMP': 3,
                    'HTTP': 4,
                    'HTTPS': 5,
                    'SSH': 6,
                    'FTP': 7,
                    'DNS': 8,
                }
                edge_data['protocol_encoded'] = proto_encoding.get(protocol, 0)
            
            # Port encoding
            port = edge.properties.get('port', 0)
            if port:
                edge_data['is_privileged_port'] = 1 if port < 1024 else 0
                edge_data['is_common_port'] = 1 if port in [22, 80, 443, 3389, 3306, 5432] else 0
            
            # Frequency
            frequency = edge.properties.get('frequency', 0)
            edge_data['frequency'] = frequency
            
            features.append(edge_data)
        
        df = pd.DataFrame(features)
        
        # Normalize numeric features
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col not in ['source', 'target']:
                max_val = df[col].max()
                if max_val > 0:
                    df[col] = df[col] / max_val
        
        return df
    
    def _calculate_statistics(self, graph: GraphInput) -> Dict[str, Any]:
        """Calculate graph statistics."""
        stats = {
            'num_nodes': len(graph.nodes),
            'num_edges': len(graph.edges),
            'avg_degree': 0,
            'graph_density': 0,
            'node_types': {},
            'relationship_types': {},
            'is_connected': False,
            'components': 0,
        }
        
        # Node type counts
        for node in graph.nodes:
            stats['node_types'][node.node_type] = stats['node_types'].get(node.node_type, 0) + 1
        
        # Edge type counts
        for edge in graph.edges:
            stats['relationship_types'][edge.relationship_type] = \
                stats['relationship_types'].get(edge.relationship_type, 0) + 1
        
        # Calculate density
        if len(graph.nodes) > 1:
            max_edges = len(graph.nodes) * (len(graph.nodes) - 1) / 2
            stats['graph_density'] = len(graph.edges) / max_edges if max_edges > 0 else 0
        
        # Calculate average degree
        if graph.edges:
            degree_counter = Counter()
            for edge in graph.edges:
                degree_counter[edge.source_id] += 1
                degree_counter[edge.target_id] += 1
            
            if degree_counter:
                stats['avg_degree'] = sum(degree_counter.values()) / len(degree_counter)
        
        # Check connectivity (using NetworkX)
        try:
            G = nx.Graph()
            G.add_nodes_from([n.node_id for n in graph.nodes])
            G.add_edges_from([(e.source_id, e.target_id) for e in graph.edges])
            
            stats['is_connected'] = nx.is_connected(G) if len(G.nodes) > 0 else False
            stats['components'] = nx.number_connected_components(G) if len(G.nodes) > 0 else 0
            
            self._stats["graph_connected"] = stats['is_connected']
        except:
            pass
        
        return stats
    
    def sample_graph(
        self,
        graph: GraphInput,
        sample_size: int = 100,
        strategy: str = 'random'
    ) -> GraphInput:
        """
        Sample a graph to reduce size.
        
        Args:
            graph: Input graph
            sample_size: Number of nodes to sample
            strategy: Sampling strategy (random, degree-based)
            
        Returns:
            GraphInput: Sampled graph
        """
        if len(graph.nodes) <= sample_size:
            return graph
        
        self.logger.info(f"Sampling graph from {len(graph.nodes)} to {sample_size} nodes")
        
        # Select nodes based on strategy
        if strategy == 'random':
            selected_nodes = np.random.choice(
                [n.node_id for n in graph.nodes],
                size=sample_size,
                replace=False
            )
        elif strategy == 'degree':
            # Calculate degrees
            degree_counter = Counter()
            for edge in graph.edges:
                degree_counter[edge.source_id] += 1
                degree_counter[edge.target_id] += 1
            
            # Sort by degree
            sorted_nodes = sorted(degree_counter.items(), key=lambda x: x[1], reverse=True)
            selected_nodes = [n[0] for n in sorted_nodes[:sample_size]]
        else:
            raise PreprocessingError(f"Unknown sampling strategy: {strategy}")
        
        selected_nodes = set(selected_nodes)
        
        # Filter nodes
        sampled_nodes = [n for n in graph.nodes if n.node_id in selected_nodes]
        
        # Filter edges (both endpoints in selected nodes)
        sampled_edges = [
            e for e in graph.edges
            if e.source_id in selected_nodes and e.target_id in selected_nodes
        ]
        
        sampled_graph = GraphInput(
            nodes=sampled_nodes,
            edges=sampled_edges,
            graph_id=f"{graph.graph_id}_sampled" if graph.graph_id else None,
            timestamp=datetime.utcnow(),
            metadata={
                "original_nodes": len(graph.nodes),
                "original_edges": len(graph.edges),
                "sampled_nodes": len(sampled_nodes),
                "sampled_edges": len(sampled_edges),
                "strategy": strategy,
            }
        )
        
        self.logger.info(f"Sampled graph: {len(sampled_nodes)} nodes, {len(sampled_edges)} edges")
        return sampled_graph
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get preprocessing statistics."""
        return self._stats.copy()