"""Prediction models for AI Engine."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class PredictionResult(BaseModel):
    """
    Result of a single prediction.
    """
    
    node_id: str = Field(..., description="Node ID")
    prediction: str = Field(..., description="Predicted class")
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
                "embedding": [0.21, 0.72, 0.43, 0.15, 0.88]
            }
        }


class AnomalyResult(BaseModel):
    """
    Result of anomaly detection.
    """
    
    node_id: str = Field(..., description="Node ID")
    anomaly_score: float = Field(..., ge=0.0, le=1.0, description="Anomaly score")
    severity: str = Field(..., description="Severity level")
    threshold: Optional[float] = Field(None, description="Classification threshold")
    is_anomaly: bool = Field(..., description="Is this an anomaly")
    
    class Config:
        json_schema_extra = {
            "example": {
                "node_id": "SERVER-01",
                "anomaly_score": 0.94,
                "severity": "HIGH",
                "threshold": 0.7,
                "is_anomaly": True
            }
        }


class ConfidenceResult(BaseModel):
    """
    Result of confidence scoring.
    """
    
    node_id: str = Field(..., description="Node ID")
    prediction: str = Field(..., description="Predicted class")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    uncertainty: float = Field(..., ge=0.0, le=1.0, description="Uncertainty score")
    entropy: float = Field(..., description="Prediction entropy")
    
    class Config:
        json_schema_extra = {
            "example": {
                "node_id": "SERVER-01",
                "prediction": "ATTACK",
                "confidence": 0.93,
                "uncertainty": 0.07,
                "entropy": 0.15
            }
        }


class ExplanationResult(BaseModel):
    """
    Result of prediction explanation.
    """
    
    node_id: str = Field(..., description="Node ID")
    prediction: str = Field(..., description="Predicted class")
    reasons: List[str] = Field(..., description="Reasons for prediction")
    feature_importance: Dict[str, float] = Field(..., description="Feature importance")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Explanation confidence")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Explanation timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "node_id": "SERVER-01",
                "prediction": "ATTACK",
                "reasons": [
                    "High failed login count: 8 (threshold: 3)",
                    "Unusual connection pattern to suspicious nodes",
                    "Activity outside business hours (3 AM)"
                ],
                "feature_importance": {
                    "failed_logins": 0.35,
                    "connection_pattern": 0.25,
                    "temporal_pattern": 0.20
                },
                "confidence": 0.93,
                "timestamp": "2026-08-29T10:30:15.000Z"
            }
        }