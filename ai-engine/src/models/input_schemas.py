"""Input schemas - What Member 3 receives from other members."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime


class EventInput(BaseModel):
    """
    Security event from Member 2.
    
    This is the clean, normalized event that Member 3 consumes.
    """
    
    event_id: str = Field(..., description="Unique event identifier")
    timestamp: datetime = Field(..., description="Event timestamp in UTC")
    event_type: str = Field(..., description="Type of security event")
    source_ip: Optional[str] = Field(None, description="Source IP address")
    destination_ip: Optional[str] = Field(None, description="Destination IP address")
    source_port: Optional[int] = Field(None, description="Source port")
    destination_port: Optional[int] = Field(None, description="Destination port")
    protocol: Optional[str] = Field(None, description="Network protocol")
    action: Optional[str] = Field(None, description="Action taken (ALLOW/DENY/BLOCK)")
    severity: Optional[str] = Field(None, description="Event severity")
    user: Optional[str] = Field(None, description="Username involved")
    hostname: Optional[str] = Field(None, description="Hostname")
    raw_source: str = Field(..., description="Original source type")
    message: Optional[str] = Field(None, description="Event message")
    tags: List[str] = Field(default_factory=list, description="Event tags")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "EVT-12345678",
                "timestamp": "2026-08-29T10:30:15.000Z",
                "event_type": "LOGIN_FAILURE",
                "source_ip": "192.168.1.50",
                "destination_ip": "192.168.1.20",
                "source_port": 45122,
                "destination_port": 22,
                "protocol": "SSH",
                "action": "DENY",
                "severity": "LOW",
                "user": "admin",
                "hostname": "SERVER-01",
                "raw_source": "firewall",
                "message": "Failed password for admin from 192.168.1.50",
                "tags": ["authentication", "ssh"],
            }
        }


class NodeInput(BaseModel):
    """
    Graph node from Member 4 (Neo4j).
    
    Represents a device/asset in the network.
    """
    
    node_id: str = Field(..., description="Unique node identifier")
    node_type: str = Field(..., description="Type of node (device, user, etc.)")
    hostname: Optional[str] = Field(None, description="Hostname")
    ip_address: Optional[str] = Field(None, description="IP address")
    device_type: Optional[str] = Field(None, description="Device type (workstation/server/etc.)")
    os: Optional[str] = Field(None, description="Operating system")
    criticality: Optional[int] = Field(None, ge=1, le=10, description="Criticality score")
    department: Optional[str] = Field(None, description="Department")
    owner: Optional[str] = Field(None, description="Asset owner")
    tags: List[str] = Field(default_factory=list, description="Node tags")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional properties")
    
    class Config:
        json_schema_extra = {
            "example": {
                "node_id": "SERVER-01",
                "node_type": "device",
                "hostname": "server-01.example.com",
                "ip_address": "192.168.1.20",
                "device_type": "server",
                "os": "Ubuntu 22.04",
                "criticality": 9,
                "department": "IT Operations",
                "owner": "IT Team",
                "tags": ["production", "critical"],
                "properties": {"cpu": 16, "memory": 64}
            }
        }


class EdgeInput(BaseModel):
    """
    Graph edge from Member 4 (Neo4j).
    
    Represents a relationship between two nodes.
    """
    
    source_id: str = Field(..., description="Source node ID")
    target_id: str = Field(..., description="Target node ID")
    relationship_type: str = Field(..., description="Type of relationship")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Edge properties")
    weight: Optional[float] = Field(1.0, description="Edge weight")
    
    class Config:
        json_schema_extra = {
            "example": {
                "source_id": "PC-01",
                "target_id": "SERVER-01",
                "relationship_type": "CONNECTS_TO",
                "properties": {"protocol": "SSH", "port": 22, "frequency": 15},
                "weight": 1.0
            }
        }


class GraphInput(BaseModel):
    """
    Complete graph input from Member 4.
    
    Contains all nodes and edges for ML processing.
    """
    
    nodes: List[NodeInput] = Field(..., description="List of nodes")
    edges: List[EdgeInput] = Field(..., description="List of edges")
    graph_id: Optional[str] = Field(None, description="Graph identifier")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Graph timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "nodes": [
                    {"node_id": "PC-01", "node_type": "device", "hostname": "pc-01"},
                    {"node_id": "SERVER-01", "node_type": "device", "hostname": "server-01"}
                ],
                "edges": [
                    {"source_id": "PC-01", "target_id": "SERVER-01", "relationship_type": "CONNECTS_TO"}
                ],
                "graph_id": "GRAPH-001",
                "metadata": {"source": "neo4j", "timestamp": "2026-08-29T10:30:15Z"}
            }
        }


class AIPredictionRequest(BaseModel):
    """
    Request for AI prediction on a single node.
    
    This is what Member 5 (Attack Engine) sends to Member 3.
    """
    
    node_id: str = Field(..., description="Node ID to predict")
    node_features: Optional[List[float]] = Field(None, description="Pre-computed node features")
    neighbors: Optional[List[str]] = Field(None, description="Neighbor node IDs")
    event_context: Optional[List[EventInput]] = Field(None, description="Recent events for context")
    graph_context: Optional[GraphInput] = Field(None, description="Graph context")
    include_explanation: bool = Field(True, description="Include prediction explanation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "node_id": "SERVER-01",
                "neighbors": ["PC-01", "SERVER-02", "DB-01"],
                "include_explanation": True
            }
        }


class BatchPredictionRequest(BaseModel):
    """
    Request for batch AI predictions on multiple nodes.
    """
    
    node_ids: List[str] = Field(..., description="Node IDs to predict")
    include_explanation: bool = Field(True, description="Include prediction explanation")
    batch_size: Optional[int] = Field(32, description="Batch size for processing")
    
    class Config:
        json_schema_extra = {
            "example": {
                "node_ids": ["SERVER-01", "PC-01", "DB-01", "SERVER-02"],
                "include_explanation": True,
                "batch_size": 32
            }
        }