"""Graph schemas for AI Engine."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class GraphNode(BaseModel):
    """
    Node in the ML graph.
    """
    
    node_id: str = Field(..., description="Node ID")
    node_type: str = Field(..., description="Node type")
    features: List[float] = Field(..., description="Node feature vector")
    label: Optional[int] = Field(None, description="Node label (for training)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "node_id": "SERVER-01",
                "node_type": "device",
                "features": [15.0, 8.0, 5.0, 7.0, 9.0, 0.83],
                "label": 1,
                "metadata": {"hostname": "server-01", "ip": "192.168.1.20"}
            }
        }


class GraphEdge(BaseModel):
    """
    Edge in the ML graph.
    """
    
    source_id: str = Field(..., description="Source node ID")
    target_id: str = Field(..., description="Target node ID")
    edge_type: str = Field(..., description="Edge type")
    features: Optional[List[float]] = Field(None, description="Edge feature vector")
    weight: float = Field(1.0, description="Edge weight")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "source_id": "PC-01",
                "target_id": "SERVER-01",
                "edge_type": "CONNECTS_TO",
                "features": [1.0, 15.0, 0.75],
                "weight": 1.0,
                "metadata": {"protocol": "SSH", "port": 22}
            }
        }


class MLGraph(BaseModel):
    """
    Complete ML graph for training/inference.
    """
    
    nodes: List[GraphNode] = Field(..., description="List of nodes")
    edges: List[GraphEdge] = Field(..., description="List of edges")
    graph_id: Optional[str] = Field(None, description="Graph identifier")
    num_nodes: int = Field(0, description="Number of nodes")
    num_edges: int = Field(0, description="Number of edges")
    num_features: int = Field(0, description="Number of features")
    num_classes: int = Field(0, description="Number of classes")
    
    # Graph properties
    is_directed: bool = Field(False, description="Is the graph directed")
    is_weighted: bool = Field(False, description="Is the graph weighted")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "nodes": [
                    {"node_id": "SERVER-01", "node_type": "device", "features": [15.0, 8.0, 5.0]},
                    {"node_id": "PC-01", "node_type": "device", "features": [8.0, 2.0, 1.0]}
                ],
                "edges": [
                    {"source_id": "PC-01", "target_id": "SERVER-01", "edge_type": "CONNECTS_TO"}
                ],
                "graph_id": "GRAPH-001",
                "num_nodes": 2,
                "num_edges": 1,
                "num_features": 3,
                "num_classes": 2,
                "is_directed": True,
                "is_weighted": False,
                "metadata": {"source": "neo4j", "timestamp": "2026-08-29T10:30:15Z"}
            }
        }


class GraphSamplingConfig(BaseModel):
    """
    Configuration for graph sampling.
    """
    
    sampling_strategy: str = Field("random", description="Sampling strategy")
    sample_size: int = Field(1000, description="Number of nodes to sample")
    neighbor_samples: List[int] = Field([10, 10], description="Number of neighbors to sample per layer")
    random_seed: Optional[int] = Field(None, description="Random seed for reproducibility")
    stratified: bool = Field(True, description="Use stratified sampling")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sampling_strategy": "random",
                "sample_size": 1000,
                "neighbor_samples": [10, 10],
                "random_seed": 42,
                "stratified": True
            }
        }