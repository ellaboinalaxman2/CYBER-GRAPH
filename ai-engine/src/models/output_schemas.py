"""Output schemas - What Member 3 sends to other members."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class PredictionResult(BaseModel):
    """
    Individual prediction result for a node.
    """
    
    node_id: str = Field(..., description="Node ID")
    prediction: str = Field(..., description="Predicted class (NORMAL/ATTACK)")
    probability: float = Field(..., ge=0.0, le=1.0, description="Prediction probability")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    anomaly_score: float = Field(..., ge=0.0, le=1.0, description="Anomaly score")
    embedding: Optional[List[float]] = Field(None, description="Node embedding vector")
    explanation: Optional[Dict[str, Any]] = Field(None, description="Explanation details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "node_id": "SERVER-01",
                "prediction": "ATTACK",
                "probability": 0.94,
                "confidence": 0.93,
                "anomaly_score": 0.94,
                "embedding": [0.21, 0.72, 0.43, 0.15, 0.88],
                "explanation": {
                    "reasons": [
                        "High failed login count: 8 (threshold: 3)",
                        "Unusual connection pattern to suspicious nodes"
                    ],
                    "feature_importance": {
                        "failed_logins": 0.35,
                        "connection_pattern": 0.25
                    }
                }
            }
        }


class AIPredictionResponse(BaseModel):
    """
    Response for AI prediction request.
    """
    
    status: str = Field(default="success", description="Response status")
    result: PredictionResult = Field(..., description="Prediction result")
    model_info: Dict[str, Any] = Field(..., description="Model information")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "result": {
                    "node_id": "SERVER-01",
                    "prediction": "ATTACK",
                    "probability": 0.94,
                    "confidence": 0.93,
                    "anomaly_score": 0.94
                },
                "model_info": {
                    "name": "GraphSAGE",
                    "version": "1.0.0",
                    "architecture": "3-layer SAGEConv"
                },
                "processing_time_ms": 45.2,
                "timestamp": "2026-08-29T10:30:15.000Z"
            }
        }


class BatchPredictionResponse(BaseModel):
    """
    Response for batch prediction request.
    """
    
    status: str = Field(default="success", description="Response status")
    total: int = Field(..., description="Total predictions")
    results: List[PredictionResult] = Field(..., description="List of prediction results")
    summary: Dict[str, int] = Field(..., description="Summary statistics")
    model_info: Dict[str, Any] = Field(..., description="Model information")
    processing_time_ms: float = Field(..., description="Total processing time in milliseconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "total": 4,
                "results": [
                    {"node_id": "SERVER-01", "prediction": "ATTACK", "probability": 0.94},
                    {"node_id": "PC-01", "prediction": "NORMAL", "probability": 0.12},
                    {"node_id": "DB-01", "prediction": "ATTACK", "probability": 0.87},
                    {"node_id": "SERVER-02", "prediction": "NORMAL", "probability": 0.08}
                ],
                "summary": {
                    "total": 4,
                    "normal": 2,
                    "attack": 2
                },
                "model_info": {"name": "GraphSAGE", "version": "1.0.0"},
                "processing_time_ms": 152.5,
                "timestamp": "2026-08-29T10:30:15.000Z"
            }
        }


class AnomalyScoreResponse(BaseModel):
    """
    Response for anomaly score request.
    """
    
    node_id: str = Field(..., description="Node ID")
    anomaly_score: float = Field(..., ge=0.0, le=1.0, description="Anomaly score")
    severity: str = Field(..., description="Severity level (LOW/MEDIUM/HIGH/CRITICAL)")
    threshold: Optional[float] = Field(None, description="Threshold used for classification")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "node_id": "SERVER-01",
                "anomaly_score": 0.94,
                "severity": "HIGH",
                "threshold": 0.7,
                "timestamp": "2026-08-29T10:30:15.000Z"
            }
        }


class ModelInfoResponse(BaseModel):
    """
    Response for model information request.
    """
    
    name: str = Field(..., description="Model name")
    version: str = Field(..., description="Model version")
    architecture: Dict[str, Any] = Field(..., description="Model architecture details")
    trained_at: datetime = Field(..., description="Training timestamp")
    metrics: Dict[str, float] = Field(..., description="Performance metrics")
    status: str = Field(..., description="Model status (ready/training/error)")
    size_mb: float = Field(..., description="Model size in MB")
    features: List[str] = Field(..., description="Feature names")
    classes: List[str] = Field(..., description="Prediction classes")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "GraphSAGE",
                "version": "1.0.0",
                "architecture": {
                    "layers": 3,
                    "hidden_channels": 128,
                    "dropout": 0.2
                },
                "trained_at": "2026-08-28T12:00:00.000Z",
                "metrics": {
                    "accuracy": 0.94,
                    "precision": 0.92,
                    "recall": 0.89,
                    "f1": 0.905,
                    "roc_auc": 0.96
                },
                "status": "ready",
                "size_mb": 45.2,
                "features": ["failed_logins", "connection_count", "protocol_diversity"],
                "classes": ["NORMAL", "ATTACK"],
                "timestamp": "2026-08-29T10:30:15.000Z"
            }
        }


class ExplanationResponse(BaseModel):
    """
    Response for prediction explanation request.
    """
    
    node_id: str = Field(..., description="Node ID")
    prediction: str = Field(..., description="Predicted class")
    reasons: List[str] = Field(..., description="List of reasons for the prediction")
    feature_importance: Dict[str, float] = Field(..., description="Feature importance scores")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in explanation")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "node_id": "SERVER-01",
                "prediction": "ATTACK",
                "reasons": [
                    "High failed login count: 8 (threshold: 3)",
                    "Unusual connection pattern to suspicious nodes",
                    "Activity outside business hours (3 AM)",
                    "SSH connection frequency: 15 (above normal)"
                ],
                "feature_importance": {
                    "failed_logins": 0.35,
                    "connection_pattern": 0.25,
                    "temporal_pattern": 0.20,
                    "protocol": 0.12,
                    "other": 0.08
                },
                "confidence": 0.93,
                "timestamp": "2026-08-29T10:30:15.000Z"
            }
        }