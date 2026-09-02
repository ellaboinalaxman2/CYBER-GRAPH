"""Feature schemas for AI Engine."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class NodeFeatures(BaseModel):
    """
    Node-level features for a device/asset.
    """
    
    node_id: str = Field(..., description="Node ID")
    node_type: str = Field(..., description="Type of node")
    
    # Connection features
    connection_count: int = Field(0, description="Total connections")
    incoming_connections: int = Field(0, description="Incoming connections")
    outgoing_connections: int = Field(0, description="Outgoing connections")
    unique_connections: int = Field(0, description="Unique connection partners")
    
    # Authentication features
    failed_login_count: int = Field(0, description="Failed login attempts")
    successful_login_count: int = Field(0, description="Successful login attempts")
    login_failure_rate: float = Field(0.0, description="Login failure rate")
    
    # Protocol features
    protocol_diversity: int = Field(0, description="Number of different protocols")
    protocol_counts: Dict[str, int] = Field(default_factory=dict, description="Protocol counts")
    
    # Port features
    port_diversity: int = Field(0, description="Number of different ports")
    port_counts: Dict[int, int] = Field(default_factory=dict, description="Port counts")
    
    # Temporal features
    avg_session_duration: float = Field(0.0, description="Average session duration in seconds")
    session_count: int = Field(0, description="Total sessions")
    
    # Security features
    alert_count: int = Field(0, description="Number of alerts")
    severity_scores: Dict[str, int] = Field(default_factory=dict, description="Severity counts")
    
    # Asset features
    criticality: int = Field(1, ge=1, le=10, description="Criticality score")
    asset_type: Optional[str] = Field(None, description="Asset type")
    
    # Additional features
    features_vector: Optional[List[float]] = Field(None, description="Computed feature vector")
    
    class Config:
        json_schema_extra = {
            "example": {
                "node_id": "SERVER-01",
                "node_type": "device",
                "connection_count": 15,
                "incoming_connections": 5,
                "outgoing_connections": 10,
                "unique_connections": 8,
                "failed_login_count": 8,
                "successful_login_count": 3,
                "login_failure_rate": 0.73,
                "protocol_diversity": 4,
                "protocol_counts": {"SSH": 12, "HTTP": 2, "HTTPS": 1},
                "port_diversity": 3,
                "port_counts": {22: 12, 80: 2, 443: 1},
                "avg_session_duration": 120.5,
                "session_count": 23,
                "alert_count": 5,
                "severity_scores": {"LOW": 3, "MEDIUM": 2},
                "criticality": 9,
                "asset_type": "server"
            }
        }


class EdgeFeatures(BaseModel):
    """
    Edge-level features for a relationship between nodes.
    """
    
    source_id: str = Field(..., description="Source node ID")
    target_id: str = Field(..., description="Target node ID")
    relationship_type: str = Field(..., description="Relationship type")
    
    # Communication features
    frequency: int = Field(0, description="Communication frequency")
    avg_bytes: int = Field(0, description="Average bytes transferred")
    total_bytes: int = Field(0, description="Total bytes transferred")
    
    # Protocol features
    protocol: Optional[str] = Field(None, description="Primary protocol")
    protocols: List[str] = Field(default_factory=list, description="Protocols used")
    
    # Temporal features
    first_seen: Optional[datetime] = Field(None, description="First seen timestamp")
    last_seen: Optional[datetime] = Field(None, description="Last seen timestamp")
    duration_seconds: float = Field(0.0, description="Duration in seconds")
    
    # Security features
    alert_count: int = Field(0, description="Number of alerts on this edge")
    suspicious_score: float = Field(0.0, ge=0.0, le=1.0, description="Suspicious score")
    
    # Additional features
    features_vector: Optional[List[float]] = Field(None, description="Computed feature vector")
    weight: float = Field(1.0, description="Edge weight")
    
    class Config:
        json_schema_extra = {
            "example": {
                "source_id": "PC-01",
                "target_id": "SERVER-01",
                "relationship_type": "CONNECTS_TO",
                "frequency": 15,
                "avg_bytes": 1024,
                "total_bytes": 15360,
                "protocol": "SSH",
                "protocols": ["SSH"],
                "first_seen": "2026-08-29T08:00:00Z",
                "last_seen": "2026-08-29T10:30:00Z",
                "duration_seconds": 9000,
                "alert_count": 3,
                "suspicious_score": 0.75,
                "weight": 1.0
            }
        }


class EventFeatures(BaseModel):
    """
    Event-based features derived from security events.
    """
    
    node_id: str = Field(..., description="Node ID")
    
    # Event counts
    total_events: int = Field(0, description="Total events")
    event_type_counts: Dict[str, int] = Field(default_factory=dict, description="Event type counts")
    
    # Authentication events
    login_success_count: int = Field(0, description="Successful logins")
    login_failure_count: int = Field(0, description="Failed logins")
    login_lockout_count: int = Field(0, description="Lockouts")
    
    # Network events
    network_connection_count: int = Field(0, description="Network connections")
    network_disconnection_count: int = Field(0, description="Network disconnections")
    
    # Firewall events
    firewall_allow_count: int = Field(0, description="Allowed connections")
    firewall_deny_count: int = Field(0, description="Denied connections")
    firewall_drop_count: int = Field(0, description="Dropped connections")
    
    # Alert events
    alert_count: int = Field(0, description="Alerts")
    
    # User events
    user_created_count: int = Field(0, description="User creations")
    user_deleted_count: int = Field(0, description="User deletions")
    user_modified_count: int = Field(0, description="User modifications")
    
    # File events
    file_access_count: int = Field(0, description="File accesses")
    file_modified_count: int = Field(0, description="File modifications")
    file_deleted_count: int = Field(0, description="File deletions")
    
    # Time window
    window_start: Optional[datetime] = Field(None, description="Window start")
    window_end: Optional[datetime] = Field(None, description="Window end")
    window_duration: int = Field(0, description="Window duration in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "node_id": "SERVER-01",
                "total_events": 25,
                "event_type_counts": {"LOGIN_FAILURE": 8, "LOGIN_SUCCESS": 3, "ALERT": 5},
                "login_success_count": 3,
                "login_failure_count": 8,
                "login_lockout_count": 1,
                "network_connection_count": 10,
                "firewall_allow_count": 6,
                "firewall_deny_count": 4,
                "alert_count": 5,
                "window_start": "2026-08-29T08:00:00Z",
                "window_end": "2026-08-29T10:30:00Z",
                "window_duration": 9000
            }
        }


class TemporalFeatures(BaseModel):
    """
    Temporal features capturing time-based patterns.
    """
    
    node_id: str = Field(..., description="Node ID")
    
    # Time of day
    hour_of_day: int = Field(0, ge=0, le=23, description="Hour of day")
    day_of_week: int = Field(0, ge=0, le=6, description="Day of week")
    is_weekend: bool = Field(False, description="Is weekend")
    is_business_hours: bool = Field(False, description="Is business hours (9-5)")
    
    # Activity patterns
    activity_score: float = Field(0.0, ge=0.0, le=1.0, description="Activity score")
    event_frequency: float = Field(0.0, description="Events per minute")
    
    # Time since
    time_since_first_event: float = Field(0.0, description="Seconds since first event")
    time_since_last_event: float = Field(0.0, description="Seconds since last event")
    
    # Burst detection
    burst_count: int = Field(0, description="Number of activity bursts")
    avg_burst_duration: float = Field(0.0, description="Average burst duration")
    max_burst_frequency: float = Field(0.0, description="Maximum burst frequency")
    
    # Periodicity
    is_periodic: bool = Field(False, description="Is activity periodic")
    period_seconds: float = Field(0.0, description="Period in seconds")
    
    # Features vector
    features_vector: Optional[List[float]] = Field(None, description="Computed feature vector")
    
    class Config:
        json_schema_extra = {
            "example": {
                "node_id": "SERVER-01",
                "hour_of_day": 3,
                "day_of_week": 0,
                "is_weekend": True,
                "is_business_hours": False,
                "activity_score": 0.85,
                "event_frequency": 2.5,
                "time_since_first_event": 9000.0,
                "time_since_last_event": 45.0,
                "burst_count": 3,
                "avg_burst_duration": 120.0,
                "max_burst_frequency": 5.0,
                "is_periodic": False,
                "period_seconds": 0.0
            }
        }


class FeatureSet(BaseModel):
    """
    Complete feature set for a node.
    """
    
    node_id: str = Field(..., description="Node ID")
    node_features: NodeFeatures = Field(..., description="Node features")
    edge_features: List[EdgeFeatures] = Field(default_factory=list, description="Edge features")
    event_features: EventFeatures = Field(..., description="Event features")
    temporal_features: TemporalFeatures = Field(..., description="Temporal features")
    
    # Combined features
    feature_vector: Optional[List[float]] = Field(None, description="Combined feature vector")
    feature_names: Optional[List[str]] = Field(None, description="Feature names")
    
    class Config:
        json_schema_extra = {
            "example": {
                "node_id": "SERVER-01",
                "node_features": {"connection_count": 15, "failed_login_count": 8},
                "edge_features": [{"source_id": "PC-01", "target_id": "SERVER-01", "frequency": 15}],
                "event_features": {"total_events": 25, "login_failure_count": 8},
                "temporal_features": {"hour_of_day": 3, "is_weekend": True}
            }
        }


class FeatureImportance(BaseModel):
    """
    Feature importance scores for explainability.
    """
    
    node_id: str = Field(..., description="Node ID")
    prediction: str = Field(..., description="Predicted class")
    feature_scores: Dict[str, float] = Field(..., description="Feature importance scores")
    top_features: List[Dict[str, Any]] = Field(..., description="Top contributing features")
    
    class Config:
        json_schema_extra = {
            "example": {
                "node_id": "SERVER-01",
                "prediction": "ATTACK",
                "feature_scores": {
                    "failed_logins": 0.35,
                    "connection_pattern": 0.25,
                    "temporal_pattern": 0.20,
                    "protocol": 0.12,
                    "other": 0.08
                },
                "top_features": [
                    {"name": "failed_logins", "score": 0.35, "value": 8, "threshold": 3},
                    {"name": "connection_pattern", "score": 0.25, "value": 0.85, "threshold": 0.5}
                ]
            }
        }