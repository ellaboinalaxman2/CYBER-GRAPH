"""Graph sampler for Member 3 - AI Engine."""

import torch
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from torch_geometric.data import Data
from torch_geometric.utils import subgraph, degree, k_hop_subgraph

from src.core.logging import get_logger
from src.core.exceptions import GraphConstructionError
from src.models.graph_schemas import GraphSamplingConfig


class GraphSampler:
    """
    Samples large graphs for training.
    
    Features:
    - Random sampling
    - Degree-based sampling
    - K-hop neighborhood sampling
    - Stratified sampling
    """
    
    def __init__(self):
        """Initialize the graph sampler."""
        self.logger = get_logger("graph.graph_sampler")
        self._stats = {
            "graphs_sampled": 0,
            "original_nodes": 0,
            "sampled_nodes": 0,
            "original_edges": 0,
            "sampled_edges": 0,
            "sampling_strategy": None,
        }
    
    def sample(
        self,
        data: Data,
        config: GraphSamplingConfig,
    ) -> Data:
        """
        Sample a graph using the specified strategy.
        
        Args:
            data: PyTorch Geometric Data object
            config: Sampling configuration
            
        Returns:
            Data: Sampled graph
        """
        self.logger.info(f"Sampling graph with {data.num_nodes} nodes using {config.sampling_strategy}")
        
        self._stats["original_nodes"] = data.num_nodes
        self._stats["original_edges"] = data.edge_index.size(1)
        self._stats["sampling_strategy"] = config.sampling_strategy
        
        if config.sampling_strategy == "random":
            sampled_data = self._random_sample(data, config)
        elif config.sampling_strategy == "degree":
            sampled_data = self._degree_sample(data, config)
        elif config.sampling_strategy == "k_hop":
            sampled_data = self._k_hop_sample(data, config)
        elif config.sampling_strategy == "stratified":
            sampled_data = self._stratified_sample(data, config)
        else:
            raise GraphConstructionError(f"Unknown sampling strategy: {config.sampling_strategy}")
        
        self._stats["graphs_sampled"] += 1
        self._stats["sampled_nodes"] = sampled_data.num_nodes
        self._stats["sampled_edges"] = sampled_data.edge_index.size(1)
        
        self.logger.info(f"Sampled graph: {sampled_data.num_nodes} nodes, {sampled_data.edge_index.size(1)} edges")
        return sampled_data
    
    def _random_sample(self, data: Data, config: GraphSamplingConfig) -> Data:
        """
        Randomly sample nodes.
        
        Args:
            data: PyTorch Geometric Data object
            config: Sampling configuration
            
        Returns:
            Data: Sampled graph
        """
        num_nodes = data.num_nodes
        sample_size = min(config.sample_size, num_nodes)
        
        # Randomly select nodes
        if config.random_seed:
            torch.manual_seed(config.random_seed)
        
        indices = torch.randperm(num_nodes)[:sample_size]
        indices = indices.sort()[0]
        
        return self._extract_subgraph(data, indices)
    
    def _degree_sample(self, data: Data, config: GraphSamplingConfig) -> Data:
        """
        Sample nodes based on degree.
        
        Args:
            data: PyTorch Geometric Data object
            config: Sampling configuration
            
        Returns:
            Data: Sampled graph
        """
        num_nodes = data.num_nodes
        sample_size = min(config.sample_size, num_nodes)
        
        # Calculate degrees
        deg = degree(data.edge_index[0], num_nodes=num_nodes)
        
        # Sort by degree descending
        sorted_indices = torch.argsort(deg, descending=True)
        indices = sorted_indices[:sample_size].sort()[0]
        
        return self._extract_subgraph(data, indices)
    
    def _k_hop_sample(self, data: Data, config: GraphSamplingConfig) -> Data:
        """
        Sample k-hop neighborhood around random nodes.
        
        Args:
            data: PyTorch Geometric Data object
            config: Sampling configuration
            
        Returns:
            Data: Sampled graph
        """
        num_nodes = data.num_nodes
        sample_size = min(config.sample_size, num_nodes)
        
        # Select random seed nodes
        if config.random_seed:
            torch.manual_seed(config.random_seed)
        
        seed_nodes = torch.randperm(num_nodes)[:min(sample_size // 2, num_nodes)]
        
        # Get k-hop subgraph
        k = len(config.neighbor_samples)
        subset, edge_index, _, _ = k_hop_subgraph(
            seed_nodes,
            k,
            data.edge_index,
            num_nodes=num_nodes,
            flow='source_to_target'
        )
        
        # If too many nodes, sample further
        if len(subset) > sample_size:
            # Randomly select from subset
            subset = subset[torch.randperm(len(subset))[:sample_size]].sort()[0]
        
        return self._extract_subgraph(data, subset)
    
    def _stratified_sample(self, data: Data, config: GraphSamplingConfig) -> Data:
        """
        Sample nodes stratified by labels.
        
        Args:
            data: PyTorch Geometric Data object
            config: Sampling configuration
            
        Returns:
            Data: Sampled graph
        """
        if not hasattr(data, 'y') or data.y is None:
            self.logger.warning("No labels found for stratified sampling, using random")
            return self._random_sample(data, config)
        
        num_nodes = data.num_nodes
        sample_size = min(config.sample_size, num_nodes)
        
        # Get unique labels
        unique_labels = torch.unique(data.y)
        samples_per_class = sample_size // len(unique_labels)
        
        indices = []
        for label in unique_labels:
            label_indices = torch.where(data.y == label)[0]
            if len(label_indices) > 0:
                n_samples = min(samples_per_class, len(label_indices))
                label_samples = label_indices[torch.randperm(len(label_indices))[:n_samples]]
                indices.append(label_samples)
        
        indices = torch.cat(indices)
        
        # If we need more samples
        if len(indices) < sample_size:
            remaining = sample_size - len(indices)
            all_indices = torch.tensor([i for i in range(num_nodes) if i not in indices])
            if len(all_indices) > 0:
                additional = all_indices[torch.randperm(len(all_indices))[:remaining]]
                indices = torch.cat([indices, additional])
        
        indices = indices.sort()[0]
        
        return self._extract_subgraph(data, indices)
    
    def _extract_subgraph(self, data: Data, indices: torch.Tensor) -> Data:
        """
        Extract subgraph for given node indices.
        
        Args:
            data: PyTorch Geometric Data object
            indices: Node indices to include
            
        Returns:
            Data: Subgraph
        """
        # Get node features and labels
        x = data.x[indices] if data.x is not None else None
        y = data.y[indices] if hasattr(data, 'y') else None
        
        # Get edges within subgraph
        edge_index, edge_attr = subgraph(
            indices,
            data.edge_index,
            data.edge_attr,
            relabel_nodes=True,
        )
        
        # Create new data object
        sampled_data = Data(
            x=x,
            edge_index=edge_index,
            edge_attr=edge_attr,
            y=y,
            num_nodes=len(indices),
        )
        
        # Copy metadata
        if hasattr(data, 'graph_id'):
            sampled_data.graph_id = f"{data.graph_id}_sampled"
        
        return sampled_data
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get sampling statistics."""
        return self._stats.copy()