"""Alert routes for Member 4 - Database Engine."""

from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.core.logging import get_logger
from src.mongodb.repositories.alert_repository import AlertRepository
from src.mongodb.models.alert import AlertModel
from src.core.exceptions import DocumentNotFoundError, MongoDBError

router = APIRouter()
logger = get_logger("api.alerts")
alert_repo = AlertRepository()


@router.post("/")
async def create_alert(alert: AlertModel):
    """Create a new alert."""
    try:
        result = alert_repo.create(alert)
        return {
            "status": "created",
            "alert": result,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except MongoDBError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
async def get_alerts(
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0),
    status: Optional[str] = None,
    severity: Optional[str] = None,
):
    """Get all alerts with filtering."""
    try:
        filters = {}
        if status:
            filters["status"] = status
        if severity:
            filters["severity"] = severity
        
        alerts = alert_repo.get_all(limit, skip, "created_at", "desc", filters)
        total = alert_repo.collection.count_documents(filters)
        
        return {
            "status": "success",
            "alerts": alerts,
            "pagination": {"limit": limit, "skip": skip, "total": total},
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except MongoDBError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{alert_id}")
async def get_alert(alert_id: str):
    """Get an alert by ID."""
    try:
        alert = alert_repo.get_by_id(alert_id)
        return {"status": "success", "alert": alert}
    except DocumentNotFoundError:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
    except MongoDBError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{alert_id}/status")
async def update_alert_status(alert_id: str, status: str):
    """Update alert status."""
    try:
        result = alert_repo.update_status(alert_id, status)
        return {
            "status": "updated",
            "alert": result,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except DocumentNotFoundError:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
    except MongoDBError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{alert_id}/assign")
async def assign_alert(alert_id: str, assigned_to: str):
    """Assign alert to an analyst."""
    try:
        result = alert_repo.assign(alert_id, assigned_to)
        return {
            "status": "assigned",
            "alert": result,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except DocumentNotFoundError:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
    except MongoDBError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{alert_id}/notes")
async def add_alert_note(alert_id: str, note: str, author: str = "system"):
    """Add a note to an alert."""
    try:
        result = alert_repo.add_note(alert_id, note, author)
        return {
            "status": "note_added",
            "alert": result,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except DocumentNotFoundError:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
    except MongoDBError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_alert_stats():
    """Get alert statistics."""
    try:
        stats = alert_repo.get_statistics()
        return {"status": "success", "stats": stats}
    except MongoDBError as e:
        raise HTTPException(status_code=500, detail=str(e))