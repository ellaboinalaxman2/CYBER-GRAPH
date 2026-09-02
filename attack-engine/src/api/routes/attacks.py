"""Attack routes for Member 5 - Attack Engine."""

from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta  # Add timedelta here

from src.core.logging import get_logger
from src.reconstruction.attack_reconstructor import AttackReconstructor
from src.attack_path.path_engine import PathEngine
from src.core.exceptions import ReconstructionError

router = APIRouter()
logger = get_logger("api.attacks")

reconstructor = AttackReconstructor()
path_engine = PathEngine()


@router.post("/reconstruct")
async def reconstruct_attack(
    events: List[Dict[str, Any]],
    predictions: Optional[List[Dict[str, Any]]] = None,
    graph_data: Optional[Dict[str, Any]] = None,
):
    """
    Reconstruct an attack from events.
    
    Args:
        events: List of events
        predictions: AI predictions
        graph_data: Graph data
        
    Returns:
        dict: Reconstruction results
    """
    try:
        result = reconstructor.reconstruct(events, predictions, graph_data)
        return {
            "status": "success",
            "data": result,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except ReconstructionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Reconstruction failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Reconstruction failed")


@router.post("/reconstruct/sample")
async def reconstruct_sample():
    """
    Reconstruct attack from sample data.
    
    Returns:
        dict: Reconstruction results
    """
    # Sample events
    now = datetime.utcnow()
    events = [
        {
            "event_id": "EVT-001",
            "timestamp": (now - timedelta(minutes=5)).isoformat() + "Z",
            "event_type": "LOGIN_FAILURE",
            "source_ip": "192.168.1.50",
            "destination_ip": "192.168.1.20",
            "raw_source": "firewall",
            "severity": "LOW",
        },
        {
            "event_id": "EVT-002",
            "timestamp": (now - timedelta(minutes=4)).isoformat() + "Z",
            "event_type": "LOGIN_FAILURE",
            "source_ip": "192.168.1.50",
            "destination_ip": "192.168.1.20",
            "raw_source": "firewall",
            "severity": "LOW",
        },
        {
            "event_id": "EVT-003",
            "timestamp": (now - timedelta(minutes=3)).isoformat() + "Z",
            "event_type": "LOGIN_SUCCESS",
            "source_ip": "192.168.1.50",
            "destination_ip": "192.168.1.20",
            "raw_source": "firewall",
            "severity": "MEDIUM",
        },
        {
            "event_id": "EVT-004",
            "timestamp": (now - timedelta(minutes=2)).isoformat() + "Z",
            "event_type": "NETWORK_CONNECTION",
            "source_ip": "192.168.1.20",
            "destination_ip": "192.168.1.30",
            "raw_source": "network",
            "protocol": "SSH",
            "severity": "MEDIUM",
        },
        {
            "event_id": "EVT-005",
            "timestamp": (now - timedelta(minutes=1)).isoformat() + "Z",
            "event_type": "FILE_ACCESS",
            "source_ip": "192.168.1.30",
            "destination_ip": "192.168.1.40",
            "raw_source": "system",
            "severity": "HIGH",
        },
    ]
    
    # Sample graph
    graph_data = {
        "nodes": [
            {"id": "192.168.1.50", "type": "device"},
            {"id": "192.168.1.20", "type": "server"},
            {"id": "192.168.1.30", "type": "server"},
            {"id": "192.168.1.40", "type": "database"},
        ],
        "edges": [
            {"source_id": "192.168.1.50", "target_id": "192.168.1.20"},
            {"source_id": "192.168.1.20", "target_id": "192.168.1.30"},
            {"source_id": "192.168.1.30", "target_id": "192.168.1.40"},
        ],
    }
    
    # Sample predictions
    predictions = [
        {"node_id": "192.168.1.50", "anomaly_score": 0.85, "prediction": "ATTACK"},
        {"node_id": "192.168.1.20", "anomaly_score": 0.90, "prediction": "ATTACK"},
        {"node_id": "192.168.1.30", "anomaly_score": 0.75, "prediction": "ATTACK"},
        {"node_id": "192.168.1.40", "anomaly_score": 0.95, "prediction": "ATTACK"},
    ]
    
    result = reconstructor.reconstruct(events, predictions, graph_data)
    
    return {
        "status": "success",
        "sample_events": events,
        "sample_graph": graph_data,
        "sample_predictions": predictions,
        "data": result,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/paths/analyze")
async def analyze_paths(
    events: List[Dict[str, Any]],
    graph_data: Dict[str, Any],
    predictions: Optional[List[Dict[str, Any]]] = None,
):
    """
    Analyze attack paths.
    
    Args:
        events: List of events
        graph_data: Graph data
        predictions: AI predictions
        
    Returns:
        dict: Path analysis results
    """
    try:
        result = path_engine.analyze_paths(events, graph_data, predictions)
        return {
            "status": "success",
            "data": result,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"Path analysis failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Path analysis failed")


@router.get("/paths")
async def get_attack_paths(
    incident_id: Optional[str] = Query(None, description="Filter by incident ID"),
):
    """
    Get attack paths.
    
    Args:
        incident_id: Filter by incident ID
        
    Returns:
        dict: List of attack paths
    """
    return {
        "status": "success",
        "paths": [],
        "total": 0,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }