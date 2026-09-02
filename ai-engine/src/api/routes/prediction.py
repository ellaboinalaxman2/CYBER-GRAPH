"""Prediction API routes for Member 3 - AI Engine."""

from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime
import torch

from src.core.logging import get_logger
from src.core.config import settings
from src.inference import Predictor, BatchPredictor
from src.model_registry import ModelLoader
from src.models.input_schemas import AIPredictionRequest, BatchPredictionRequest
from src.models.output_schemas import AIPredictionResponse, BatchPredictionResponse

router = APIRouter()
logger = get_logger("api.prediction")

# Global instances
_predictor = None
_batch_predictor = None
_model_loader = None


def get_predictor():
    """Get or create predictor instance."""
    global _predictor, _batch_predictor, _model_loader
    
    if _predictor is None:
        try:
            # Try to load model from registry
            _model_loader = ModelLoader()
            model = _model_loader.load_active_model(device="cpu")
            
            _predictor = Predictor(model=model, device="cpu")
            _batch_predictor = BatchPredictor(_predictor)
            
            logger.info("Predictor initialized with active model")
        except Exception as e:
            logger.warning(f"Failed to load model: {e}, using dummy model")
            # Create predictor without model (will use dummy)
            _predictor = Predictor(model_path=None, device="cpu")
            _batch_predictor = BatchPredictor(_predictor)
    
    return _predictor, _batch_predictor


@router.post("/single", response_model=AIPredictionResponse)
async def predict_single(
    request: AIPredictionRequest,
):
    """
    Make a prediction for a single node.
    
    Args:
        request: Prediction request
        
    Returns:
        AIPredictionResponse: Prediction result
    """
    logger.info(f"Prediction request for node: {request.node_id}")
    
    try:
        predictor, _ = get_predictor()
        
        # Prepare node data
        node_data = {
            "node_id": request.node_id,
            "features": request.node_features,
            "neighbors": [{"node_id": n} for n in request.neighbors] if request.neighbors else [],
        }
        
        # Make prediction
        result = predictor.predict(
            node_data,
            None,
            return_embedding=True,
            return_explanation=request.include_explanation,
        )
        
        # Prepare response
        response = AIPredictionResponse(
            status="success",
            result=result.to_dict(),
            model_info={
                "name": "GraphSAGE",
                "version": settings.model_version,
                "architecture": predictor.model_config,
            },
            processing_time_ms=0.0,
            timestamp=datetime.utcnow(),
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}",
        )


@router.post("/batch", response_model=BatchPredictionResponse)
async def predict_batch(
    request: BatchPredictionRequest,
):
    """
    Make predictions for multiple nodes.
    
    Args:
        request: Batch prediction request
        
    Returns:
        BatchPredictionResponse: Batch prediction results
    """
    logger.info(f"Batch prediction request for {len(request.node_ids)} nodes")
    
    try:
        _, batch_predictor = get_predictor()
        
        # Prepare node data list
        node_data_list = [
            {
                "node_id": node_id,
                "include_explanation": request.include_explanation,
            }
            for node_id in request.node_ids
        ]
        
        # Make predictions
        results = batch_predictor.predict_batch_with_summary(
            node_data_list,
            parallel=True,
        )
        
        # Prepare response
        response = BatchPredictionResponse(
            status="success",
            total=len(results["results"]),
            results=results["results"],
            summary=results["summary"],
            model_info={
                "name": "GraphSAGE",
                "version": settings.model_version,
            },
            processing_time_ms=0.0,
            timestamp=datetime.utcnow(),
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Batch prediction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch prediction failed: {str(e)}",
        )


@router.get("/status")
async def get_model_status():
    """
    Get model status.
    
    Returns:
        dict: Model status
    """
    try:
        predictor, _ = get_predictor()
        
        return {
            "status": "ready",
            "model_name": "GraphSAGE",
            "model_version": settings.model_version,
            "device": str(predictor.device),
            "total_predictions": predictor.get_stats()["total_predictions"],
            "last_prediction": predictor.get_stats()["last_prediction"],
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }


@router.get("/info")
async def get_model_info():
    """
    Get model information.
    
    Returns:
        dict: Model information
    """
    try:
        predictor, _ = get_predictor()
        
        # Count parameters
        param_count = 0
        if hasattr(predictor.model, 'count_parameters'):
            param_count = predictor.model.count_parameters()
        else:
            param_count = sum(p.numel() for p in predictor.model.parameters())
        
        return {
            "model": {
                "name": "GraphSAGE",
                "version": settings.model_version,
                "config": predictor.model_config,
                "device": str(predictor.device),
                "parameters": param_count,
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get model info: {str(e)}",
        )