"""Event routes for Member 4 - Database Engine."""

from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional, Dict, Any
from datetime import datetime

from src.core.logging import get_logger
from src.mongodb.repositories.event_repository import EventRepository
from src.mongodb.models.event import EventModel
from src.core.exceptions import DocumentNotFoundError, MongoDBError

router = APIRouter()
logger = get_logger("api.events")
event_repo = EventRepository()


@router.post("/")
async def create_event(event: EventModel):
    """
    Create a new event.
    
    Args:
        event: Event model
        
    Returns:
        dict: Created event
    """
    try:
        result = event_repo.create(event)
        return {
            "status": "created",
            "event": result,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except MongoDBError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error creating event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/")
async def get_events(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of events"),
    skip: int = Query(0, ge=0, description="Number of events to skip"),
    sort_by: str = Query("timestamp", description="Field to sort by"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
):
    """
    Get events with filtering and pagination.
    
    Args:
        limit: Maximum number of events
        skip: Number of events to skip
        sort_by: Field to sort by
        sort_order: Sort order
        event_type: Filter by event type
        severity: Filter by severity
        
    Returns:
        dict: List of events
    """
    try:
        filters = {}
        if event_type:
            filters["event_type"] = event_type
        if severity:
            filters["severity"] = severity
        
        events = event_repo.get_all(limit, skip, sort_by, sort_order, filters)
        total = event_repo.collection.count_documents(filters)
        
        return {
            "status": "success",
            "events": events,
            "pagination": {
                "limit": limit,
                "skip": skip,
                "total": total,
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except MongoDBError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{event_id}")
async def get_event(event_id: str):
    """
    Get an event by ID.
    
    Args:
        event_id: Event ID
        
    Returns:
        dict: Event data
    """
    try:
        result = event_repo.get_by_id(event_id)
        return {
            "status": "success",
            "event": result,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except DocumentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except MongoDBError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/stats")
async def get_event_stats():
    """
    Get event statistics.
    
    Returns:
        dict: Event statistics
    """
    try:
        stats = event_repo.get_statistics()
        return {
            "status": "success",
            "stats": stats,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except MongoDBError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{event_id}")
async def update_event(event_id: str, update_data: Dict[str, Any]):
    """
    Update an event.
    
    Args:
        event_id: Event ID
        update_data: Data to update
        
    Returns:
        dict: Updated event
    """
    try:
        result = event_repo.update(event_id, update_data)
        return {
            "status": "updated",
            "event": result,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except DocumentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except MongoDBError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{event_id}")
async def delete_event(event_id: str):
    """
    Delete an event.
    
    Args:
        event_id: Event ID
        
    Returns:
        dict: Deletion status
    """
    try:
        event_repo.delete(event_id)
        return {
            "status": "deleted",
            "event_id": event_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except DocumentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except MongoDBError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )