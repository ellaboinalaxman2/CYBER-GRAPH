"""Incident routes for Member 4 - Database Engine."""

from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.core.logging import get_logger
from src.mongodb.repositories.incident_repository import IncidentRepository
from src.mongodb.models.incident import IncidentModel
from src.core.exceptions import DocumentNotFoundError, MongoDBError

router = APIRouter()
logger = get_logger("api.incidents")
incident_repo = IncidentRepository()


@router.post("/")
async def create_incident(incident: IncidentModel):
    """Create a new incident."""
    try:
        result = incident_repo.create(incident)
        return {
            "status": "created",
            "incident": result,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except MongoDBError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
async def get_incidents(
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0),
    status: Optional[str] = None,
    severity: Optional[str] = None,
):
    """Get all incidents with filtering."""
    try:
        filters = {}
        if status:
            filters["status"] = status
        if severity:
            filters["severity"] = severity
        
        incidents = incident_repo.get_all(limit, skip, "created_at", "desc", filters)
        total = incident_repo.collection.count_documents(filters)
        
        return {
            "status": "success",
            "incidents": incidents,
            "pagination": {"limit": limit, "skip": skip, "total": total},
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except MongoDBError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{incident_id}")
async def get_incident(incident_id: str):
    """Get an incident by ID."""
    try:
        incident = incident_repo.get_by_id(incident_id)
        return {"status": "success", "incident": incident}
    except DocumentNotFoundError:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    except MongoDBError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{incident_id}/status")
async def update_incident_status(incident_id: str, status: str):
    """Update incident status."""
    try:
        result = incident_repo.update_status(incident_id, status)
        return {
            "status": "updated",
            "incident": result,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except DocumentNotFoundError:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    except MongoDBError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{incident_id}/alerts")
async def add_alert_to_incident(incident_id: str, alert_id: str):
    """Add an alert to an incident."""
    try:
        result = incident_repo.add_alert(incident_id, alert_id)
        return {
            "status": "alert_added",
            "incident": result,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except DocumentNotFoundError:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    except MongoDBError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{incident_id}/notes")
async def add_investigation_note(incident_id: str, note: str, author: str = "system"):
    """Add an investigation note to an incident."""
    try:
        result = incident_repo.add_investigation_note(incident_id, note, author)
        return {
            "status": "note_added",
            "incident": result,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except DocumentNotFoundError:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    except MongoDBError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_incident_stats():
    """Get incident statistics."""
    try:
        stats = incident_repo.get_statistics()
        return {"status": "success", "stats": stats}
    except MongoDBError as e:
        raise HTTPException(status_code=500, detail=str(e))