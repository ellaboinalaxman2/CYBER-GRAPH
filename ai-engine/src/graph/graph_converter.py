"""Graph converter for Member 3 - AI Engine."""

import torch
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from torch_geometric.data import Data, HeteroData
from torch_geometric.utils import to_undirected

from src.core.logging import get_logger
from src.core.exceptions import GraphConstructionError
from src.models.graph_schemas import MLGraph


class GraphConverter:
    """
    Converts graphs to PyTorch Geometric format.
    
    Features:
    - Homogeneous graph conversion
    - Heterogeneous graph conversion
    - Batch conversion
    - Device placement
    """
    
    def __init__(self, device: Optional[str] = None):
        """
        Initialize the graph converter.
        
        Args:
            device: Device to place tensors on ('cpu', 'cuda', etc.)
        """
        self.logger = get_logger("graph.graph_converter")
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self._stats = {
            "graphs_converted": 0,
            "total_nodes": 0,
            "total_edges": 0,
            "device": self.device,
        }
    
    def convert(self, ml_graph: MLGraph) -> Data:
        """
        Convert MLGraph to PyTorch Geometric Data object.
        
        Args:
            ml_graph: MLGraph object
            
        Returns:
            Data: PyTorch Geometric Data object
        """
        self.logger.info(f"Converting graph with {ml_graph.num_nodes} nodes and {ml_graph.num_edges} edges")
        
        # Extract node features
        x = torch.tensor(
            [node.features for node in ml_graph.nodes],
            dtype=torch.float
        )
        
        # Extract edges
        edge_list = []
        for edge in ml_graph.edges:
            # Find node indices
            source_idx = self._find_node_index(ml_graph.nodes, edge.source_id)
            target_idx = self._find_node_index(ml_graph.nodes, edge.target_id)
            
            if source_idx is not None and target_idx is not None:
                edge_list.append([source_idx, target_idx])
        
        if not edge_list:
            self.logger.warning("No valid edges found")
            edge_index = torch.tensor([], dtype=torch.long).reshape(2, 0)
        else:
            edge_index = torch.tensor(edge_list, dtype=torch.long).t().contiguous()
        
        # Extract edge features
        edge_features = []
        for edge in ml_graph.edges:
            if edge.features:
                edge_features.append(edge.features)
            else:
                edge_features.append([edge.weight])
        
        edge_attr = torch.tensor(edge_features, dtype=torch.float) if edge_features else None
        
        # Extract labels
        y = torch.tensor(
            [node.label if node.label is not None else -1 for node in ml_graph.nodes],
            dtype=torch.long
        )
        
        # Create Data object
        data = Data(
            x=x,
            edge_index=edge_index,
            edge_attr=edge_attr,
            y=y,
            num_nodes=ml_graph.num_nodes,
        )
        
        # Add metadata
        data.graph_id = ml_graph.graph_id
        data.num_classes = ml_graph.num_classes
        data.is_directed = ml_graph.is_directed
        data.is_weighted = ml_graph.is_weighted
        
        # Move to device
        data = data.to(self.device)
        
        self._stats["graphs_converted"] += 1
        self._stats["total_nodes"] += ml_graph.num_nodes
        self._stats["total_edges"] += ml_graph.num_edges
        
        self.logger.info(f"Graph converted: {data}")
        return data
    
    def _find_node_index(self, nodes: List, node_id: str) -> Optional[int]:
        """Find node index by node_id."""
        for idx, node in enumerate(nodes):
            if node.node_id == node_id:
                return idx
        return None
    
    def convert_batch(self, ml_graphs: List[MLGraph]) -> List[Data]:
        """
        Convert multiple graphs to PyTorch Geometric Data objects.
        
        Args:
            ml_graphs: List of MLGraph objects
            
        Returns:
            List[Data]: List of PyTorch Geometric Data objects
        """
        return [self.convert(g) for g in ml_graphs]
    
    def to_undirected(self, data: Data) -> Data:
        """
        Convert directed graph to undirected.
        
        Args:
            data: PyTorch Geometric Data object
            
        Returns:
            Data: Undirected graph
        """
        data.edge_index = to_undirected(data.edge_index)
        return data
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get conversion statistics."""
        return self._stats.copy()