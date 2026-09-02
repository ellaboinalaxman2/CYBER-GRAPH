"""Explanation API routes for Member 3 - AI Engine."""

from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import Optional, Dict, Any
from datetime import datetime

from src.core.logging import get_logger
from src.core.config import settings
from src.inference import Predictor
from src.explainability import PredictionExplanation, ExplanationVisualizer

router = APIRouter()
logger = get_logger("api.explain")

# Global instances
_predictor = None
_explainer = None
_visualizer = None


def get_components():
    """Get or create explainability components."""
    global _predictor, _explainer, _visualizer
    
    if _predictor is None:
        try:
            from src.model_registry import ModelLoader
            loader = ModelLoader()
            model = loader.load_active_model(device="cpu")
            _predictor = Predictor(model=model, device="cpu")
        except Exception as e:
            logger.warning(f"Failed to load model: {e}, using dummy")
            _predictor = Predictor(model_path=None, device="cpu")
        
        _explainer = PredictionExplanation()
        _visualizer = ExplanationVisualizer()
    
    return _predictor, _explainer, _visualizer


@router.post("/node")
async def explain_prediction(
    node_id: str = Query(..., description="Node ID to explain"),
    include_visualization: bool = Query(False, description="Include visualization"),
):
    """
    Get explanation for a prediction.
    
    Args:
        node_id: Node ID to explain
        include_visualization: Whether to include visualization
        
    Returns:
        dict: Explanation result
    """
    logger.info(f"Explanation request for node: {node_id}")
    
    try:
        predictor, explainer, visualizer = get_components()
        
        # Prepare node data
        node_data = {
            "node_id": node_id,
            "features": [],  # Will be filled from data
        }
        
        # Make prediction first
        result = predictor.predict(node_data, return_embedding=True)
        
        # Generate explanation
        explanation = explainer.explain(
            model=predictor.model,
            x=None,
            node_id=node_id,
            node_idx=0,
            edge_index=None,
            feature_names=None,
            neighbor_ids=None,
            prediction=result.prediction,
            confidence=result.confidence,
            anomaly_score=result.anomaly_score,
        )
        
        response = {
            "status": "success",
            "explanation": explanation.to_dict(),
            "prediction": result.to_dict(),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        
        # Add visualization if requested
        if include_visualization:
            image_base64 = visualizer.plot_explanation_dashboard(
                node_id=node_id,
                prediction=result.prediction,
                confidence=result.confidence,
                anomaly_score=result.anomaly_score,
                feature_importance=explanation.feature_importance,
                reasons=explanation.detailed_reasons,
                recommendations=explanation.recommendations,
                return_base64=True,
            )
            response["visualization"] = image_base64
        
        return response
        
    except Exception as e:
        logger.error(f"Explanation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Explanation failed: {str(e)}",
        )


@router.get("/feature-names")
async def get_feature_names():
    """
    Get feature names.
    
    Returns:
        dict: Feature names
    """
    return {
        "feature_names": [
            "degree",
            "failed_login_count",
            "successful_login_count",
            "incoming_connections",
            "outgoing_connections",
            "protocol_diversity",
            "avg_session_duration",
            "alert_count",
            "criticality",
            "login_failure_ratio",
            "alert_ratio",
            "severity_score",
            "protocol_entropy",
            "risk_score",
            "has_alerts",
            "has_login_failures",
            "has_high_severity",
        ],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }