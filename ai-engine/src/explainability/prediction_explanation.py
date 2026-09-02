"""Prediction explanation for Member 3 - AI Engine."""

import torch
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field

from src.core.logging import get_logger
from src.core.exceptions import ExplainabilityError
from src.explainability.node_explanation import NodeExplanation, NodeExplanationResult


@dataclass
class PredictionExplanationResult:
    """Result of prediction explanation."""
    
    node_id: str
    prediction: str
    confidence: float
    anomaly_score: float
    summary: str
    detailed_reasons: List[str] = field(default_factory=list)
    feature_importance: Dict[str, float] = field(default_factory=dict)
    neighbor_influence: Dict[str, float] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            from datetime import datetime
            self.timestamp = datetime.utcnow().isoformat() + "Z"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "node_id": self.node_id,
            "prediction": self.prediction,
            "confidence": self.confidence,
            "anomaly_score": self.anomaly_score,
            "summary": self.summary,
            "detailed_reasons": self.detailed_reasons,
            "feature_importance": self.feature_importance,
            "neighbor_influence": self.neighbor_influence,
            "recommendations": self.recommendations,
            "timestamp": self.timestamp,
        }


class PredictionExplanation:
    """
    Generates comprehensive prediction explanations.
    
    Features:
    - Human-readable summaries
    - Detailed reasons
    - Actionable recommendations
    - Multiple explanation formats
    """
    
    def __init__(self):
        """Initialize the prediction explanation."""
        self.logger = get_logger("explainability.prediction_explanation")
        self.node_explainer = NodeExplanation()
        self._stats = {
            "total_explanations": 0,
        }
    
    def explain(
        self,
        model: torch.nn.Module,
        x: torch.Tensor,
        node_id: str,
        node_idx: int,
        edge_index: Optional[torch.Tensor] = None,
        feature_names: Optional[List[str]] = None,
        neighbor_ids: Optional[List[str]] = None,
        prediction: Optional[str] = None,
        confidence: Optional[float] = None,
        anomaly_score: Optional[float] = None,
    ) -> PredictionExplanationResult:
        """
        Generate comprehensive prediction explanation.
        
        Args:
            model: Trained model
            x: Node features
            node_id: Node identifier
            node_idx: Node index
            edge_index: Edge indices
            feature_names: Feature names
            neighbor_ids: Neighbor node IDs
            prediction: Predicted class
            confidence: Prediction confidence
            anomaly_score: Anomaly score
            
        Returns:
            PredictionExplanationResult: Explanation result
        """
        self.logger.info(f"Generating prediction explanation for: {node_id}")
        
        # Get node explanation
        node_explanation = self.node_explainer.explain(
            model,
            x,
            node_id,
            node_idx,
            edge_index,
            feature_names,
            neighbor_ids,
            prediction,
            confidence,
            anomaly_score,
        )
        
        # Generate summary
        summary = self._generate_summary(node_explanation)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(node_explanation)
        
        self._stats["total_explanations"] += 1
        
        return PredictionExplanationResult(
            node_id=node_explanation.node_id,
            prediction=node_explanation.prediction,
            confidence=node_explanation.confidence,
            anomaly_score=node_explanation.anomaly_score,
            summary=summary,
            detailed_reasons=node_explanation.reasons,
            feature_importance=node_explanation.feature_importance,
            neighbor_influence=node_explanation.neighbor_influence,
            recommendations=recommendations,
        )
    
    def _generate_summary(self, node_explanation: NodeExplanationResult) -> str:
        """
        Generate human-readable summary.
        
        Args:
            node_explanation: Node explanation result
            
        Returns:
            str: Human-readable summary
        """
        if node_explanation.prediction == "ATTACK":
            summary = f"Node {node_explanation.node_id} is flagged as an attack with {node_explanation.confidence:.1%} confidence and {node_explanation.anomaly_score:.1%} anomaly score."
            
            # Add key reasons
            if node_explanation.reasons:
                top_reason = node_explanation.reasons[0]
                summary += f" Key indicators: {top_reason}"
        else:
            summary = f"Node {node_explanation.node_id} appears normal with {node_explanation.confidence:.1%} confidence and {node_explanation.anomaly_score:.1%} anomaly score."
        
        return summary
    
    def _generate_recommendations(self, node_explanation: NodeExplanationResult) -> List[str]:
        """
        Generate actionable recommendations.
        
        Args:
            node_explanation: Node explanation result
            
        Returns:
            List[str]: Recommendations
        """
        recommendations = []
        
        if node_explanation.prediction == "ATTACK":
            recommendations.append("Investigate this node immediately")
            recommendations.append("Check for lateral movement to other nodes")
            
            if node_explanation.anomaly_score > 0.85:
                recommendations.append("High severity - isolate this node if necessary")
            
            # Feature-based recommendations
            for feature, importance in node_explanation.feature_importance.items():
                if importance > 0.15:
                    if "login" in feature.lower():
                        recommendations.append(f"Review authentication logs for {feature}")
                    elif "connection" in feature.lower():
                        recommendations.append(f"Analyze connection patterns: {feature}")
                    elif "alert" in feature.lower():
                        recommendations.append(f"Investigate alerts related to {feature}")
            
            # Neighbor-based recommendations
            for neighbor, influence in node_explanation.neighbor_influence.items():
                if influence > 0.1:
                    recommendations.append(f"Investigate neighboring node: {neighbor}")
        else:
            recommendations.append("No immediate action required")
            recommendations.append("Continue monitoring for unusual activity")
        
        return recommendations
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get explanation statistics."""
        return self._stats.copy()