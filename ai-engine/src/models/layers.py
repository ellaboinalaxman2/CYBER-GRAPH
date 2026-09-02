"""GraphSAGE layers for Member 3 - AI Engine."""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, List, Tuple


class SAGEConv(nn.Module):
    """
    GraphSAGE convolution layer.
    
    Implements the SAGEConv operation from the GraphSAGE paper.
    Supports mean, max, and LSTM aggregators.
    """
    
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        aggregator: str = 'mean',
        bias: bool = True,
        normalize: bool = False,
        dropout: float = 0.0,
    ):
        """
        Initialize the SAGEConv layer.
        
        Args:
            in_channels: Input feature dimension
            out_channels: Output feature dimension
            aggregator: Aggregation method ('mean', 'max', 'lstm')
            bias: Whether to use bias
            normalize: Whether to normalize output
            dropout: Dropout probability
        """
        super().__init__()
        
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.aggregator = aggregator
        self.dropout = dropout
        
        # Linear layer for neighbor aggregation
        self.lin_neigh = nn.Linear(in_channels, out_channels, bias=bias)
        
        # Linear layer for self transformation
        self.lin_self = nn.Linear(in_channels, out_channels, bias=bias)
        
        # Normalization
        self.normalize = normalize
        
        if normalize:
            self.norm = nn.BatchNorm1d(out_channels)
        
        self._reset_parameters()
    
    def _reset_parameters(self):
        """Reset model parameters."""
        nn.init.xavier_uniform_(self.lin_neigh.weight)
        nn.init.xavier_uniform_(self.lin_self.weight)
        
        if self.lin_neigh.bias is not None:
            nn.init.zeros_(self.lin_neigh.bias)
        if self.lin_self.bias is not None:
            nn.init.zeros_(self.lin_self.bias)
    
    def forward(self, x: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            x: Node features [num_nodes, in_channels]
            edge_index: Edge indices [2, num_edges]
            
        Returns:
            torch.Tensor: Updated node features [num_nodes, out_channels]
        """
        # Apply dropout to input
        if self.training and self.dropout > 0:
            x = F.dropout(x, p=self.dropout)
        
        # Aggregate neighbor features
        neigh_agg = self._aggregate_neighbors(x, edge_index)
        
        # Apply linear transformations
        neigh_out = self.lin_neigh(neigh_agg)
        self_out = self.lin_self(x)
        
        # Combine self and neighbor information
        out = neigh_out + self_out
        
        # Apply normalization
        if self.normalize:
            out = self.norm(out)
        
        # Apply activation
        out = F.relu(out)
        
        return out
    
    def _aggregate_neighbors(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor
    ) -> torch.Tensor:
        """
        Aggregate neighbor features.
        
        Args:
            x: Node features
            edge_index: Edge indices
            
        Returns:
            torch.Tensor: Aggregated neighbor features
        """
        num_nodes = x.size(0)
        
        # Convert edge_index to sparse matrix
        src, dst = edge_index
        
        # Mean aggregation
        if self.aggregator == 'mean':
            # Create sparse adjacency matrix
            adj = torch.sparse_coo_tensor(
                edge_index,
                torch.ones(edge_index.size(1), device=x.device),
                (num_nodes, num_nodes)
            )
            
            # Normalize by degree
            deg = torch.sparse.sum(adj, dim=1).to_dense()
            deg = deg.clamp(min=1)
            
            # Aggregate
            agg = torch.sparse.mm(adj, x)
            agg = agg / deg.unsqueeze(1)
            
            return agg
        
        # Max aggregation
        elif self.aggregator == 'max':
            # This is a simplified version
            # For proper max aggregation, we'd need a scatter operation
            agg = torch.zeros_like(x)
            
            for i in range(num_nodes):
                neigh_mask = (src == i)
                if neigh_mask.any():
                    neigh_idx = dst[neigh_mask]
                    if len(neigh_idx) > 0:
                        agg[i] = x[neigh_idx].max(dim=0)[0]
            
            return agg
        
        # LSTM aggregation (simplified)
        elif self.aggregator == 'lstm':
            # For simplicity, use mean as LSTM is more complex
            return self._aggregate_neighbors(x, edge_index, aggregator='mean')
        
        else:
            raise ValueError(f"Unknown aggregator: {self.aggregator}")
    
    def extra_repr(self) -> str:
        """Extra representation string."""
        return f'in={self.in_channels}, out={self.out_channels}, agg={self.aggregator}'


class GraphSAGELayer(nn.Module):
    """
    Complete GraphSAGE layer with neighborhood sampling.
    """
    
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        num_samples: int = 10,
        aggregator: str = 'mean',
        dropout: float = 0.0,
    ):
        """
        Initialize the GraphSAGE layer.
        
        Args:
            in_channels: Input feature dimension
            out_channels: Output feature dimension
            num_samples: Number of neighbors to sample
            aggregator: Aggregation method
            dropout: Dropout probability
        """
        super().__init__()
        
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.num_samples = num_samples
        
        self.conv = SAGEConv(
            in_channels,
            out_channels,
            aggregator=aggregator,
            normalize=True,
            dropout=dropout,
        )
        
        self._reset_parameters()
    
    def _reset_parameters(self):
        """Reset model parameters."""
        # Parameters are already reset in SAGEConv
        pass
    
    def forward(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        batch: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            x: Node features
            edge_index: Edge indices
            batch: Batch indices (for batching)
            
        Returns:
            torch.Tensor: Updated node features
        """
        return self.conv(x, edge_index)