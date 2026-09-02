"""Alert routes for Member 5 - Attack Engine."""

from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.core.logging import get_logger
from src.alert.alert_generator import AlertGenerator
from src.alert.alert_classifier import AlertStatus
from src.core.exceptions import AlertError

router = APIRouter()
logger = get_logger("api.alerts")

alert_generator = AlertGenerator()


@router.post("/generate")
async def generate_alert(
    incident: Dict[str, Any],
    events: List[Dict[str, Any]],
    risk_assessment: Dict[str, Any],
    mitre_mapping: Dict[str, Any],
    attack_path: Optional[List[Dict[str, Any]]] = None,
):
    """
    Generate an alert from an incident.
    
    Args:
        incident: Incident data
        events: List of events
        risk_assessment: Risk assessment results
        mitre_mapping: MITRE mapping results
        attack_path: Attack path
        
    Returns:
        dict: Generated alert
    """
    try:
        alert = alert_generator.generate(
            incident=incident,
            events=events,
            risk_assessment=risk_assessment,
            mitre_mapping=mitre_mapping,
            attack_path=attack_path,
        )
        
        return {
            "status": "success",
            "alert": alert,
            "formatted": {
                "json": alert_generator.formatter.format_json(alert),
                "human": alert_generator.formatter.format_human_readable(alert),
                "dashboard": alert_generator.formatter.format_dashboard(alert),
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except AlertError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Alert generation failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Alert generation failed: {str(e)}")


@router.post("/generate/sample")
async def generate_sample_alert():
    """
    Generate a sample alert.
    
    Returns:
        dict: Sample alert
    """
    # Sample data
    sample_incident = {
        "incident_id": "INC-SAMPLE-001",
        "attack_type": "lateral_movement",
        "confidence": 0.93,
        "anomaly_score": 0.85,
    }
    
    sample_events = [
        {"event_id": "EVT-001", "event_type": "LOGIN_FAILURE"},
        {"event_id": "EVT-002", "event_type": "LOGIN_FAILURE"},
        {"event_id": "EVT-003", "event_type": "LOGIN_SUCCESS"},
        {"event_id": "EVT-004", "event_type": "NETWORK_CONNECTION"},
    ]
    
    sample_risk = {
        "risk_score": 87.5,
        "affected_nodes": ["192.168.1.50", "192.168.1.20", "192.168.1.30"],
    }
    
    sample_mitre = {
        "technique_ids": ["T1110", "T1021"],
        "tactic_ids": ["Credential Access", "Lateral Movement"],
    }
    
    sample_attack_path = [
        {"from": "192.168.1.50", "to": "192.168.1.20"},
        {"from": "192.168.1.20", "to": "192.168.1.30"},
    ]
    
    alert = alert_generator.generate(
        incident=sample_incident,
        events=sample_events,
        risk_assessment=sample_risk,
        mitre_mapping=sample_mitre,
        attack_path=sample_attack_path,
    )
    
    return {
        "status": "success",
        "sample_data": {
            "incident": sample_incident,
            "events": sample_events,
            "risk_assessment": sample_risk,
            "mitre_mapping": sample_mitre,
            "attack_path": sample_attack_path,
        },
        "alert": alert,
        "formatted": {
            "json": alert_generator.formatter.format_json(alert),
            "human": alert_generator.formatter.format_human_readable(alert),
            "dashboard": alert_generator.formatter.format_dashboard(alert),
            "slack": alert_generator.formatter.format_slack(alert),
        },
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/")
async def get_alerts(
    status: Optional[str] = Query(None, description="Filter by status"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
):
    """
    Get all alerts.
    
    Args:
        status: Filter by status
        severity: Filter by severity
        
    Returns:
        dict: List of alerts
    """
    try:
        if status:
            alerts = alert_generator.get_alerts_by_status(status)
        elif severity:
            alerts = alert_generator.get_alerts_by_severity(severity)
        else:
            alerts = alert_generator.get_all_alerts()
        
        return {
            "status": "success",
            "alerts": alerts,
            "total": len(alerts),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"Failed to get alerts: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{alert_id}")
async def get_alert(alert_id: str):
    """
    Get an alert by ID.
    
    Args:
        alert_id: Alert ID
        
    Returns:
        dict: Alert data
    """
    try:
        alert = alert_generator.get_alert(alert_id)
        
        if not alert:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Alert {alert_id} not found")
        
        return {
            "status": "success",
            "alert": alert,
            "formatted": {
                "json": alert_generator.formatter.format_json(alert),
                "human": alert_generator.formatter.format_human_readable(alert),
                "dashboard": alert_generator.formatter.format_dashboard(alert),
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get alert: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/{alert_id}/status")
async def update_alert_status(
    alert_id: str,
    status: str = Query(..., description="New status"),
    note: Optional[str] = Query(None, description="Optional note"),
    user: Optional[str] = Query(None, description="User making the change"),
):
    """
    Update alert status.
    
    Args:
        alert_id: Alert ID
        status: New status
        note: Optional note
        user: User making the change
        
    Returns:
        dict: Updated alert
    """
    try:
        # Validate status
        valid_statuses = [s.value for s in AlertStatus]
        if status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {valid_statuses}"
            )
        
        alert = alert_generator.update_status(alert_id, status, note, user)
        
        return {
            "status": "success",
            "alert": alert,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except AlertError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update alert status: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{alert_id}/notes")
async def add_alert_note(
    alert_id: str,
    note: str = Query(..., description="Note content"),
    user: Optional[str] = Query(None, description="User adding the note"),
):
    """
    Add an investigation note to an alert.
    
    Args:
        alert_id: Alert ID
        note: Note content
        user: User adding the note
        
    Returns:
        dict: Updated alert
    """
    try:
        alert = alert_generator.add_note(alert_id, note, user)
        
        return {
            "status": "success",
            "alert": alert,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except AlertError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to add note: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/stats")
async def get_alert_stats():
    """
    Get alert statistics.
    
    Returns:
        dict: Alert statistics
    """
    try:
        stats = alert_generator.get_statistics()
        
        return {
            "status": "success",
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"Failed to get alert stats: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))