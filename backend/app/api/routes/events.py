# app/api/routes/events.py
from fastapi import APIRouter, Query, HTTPException, status, Request
from app.api.controllers.event_controller import EventController
from app.schemas.event import EventCreate, EventResponse
from typing import List

router = APIRouter(prefix="/api/events", tags=["Events"])

@router.get("/", response_model=List[EventResponse])
async def get_events(request: Request, skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000)):
    return await EventController.get_events(skip, limit, request.state.user["userId"])

@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(event: EventCreate, request: Request):
    return await EventController.create_event(event, request.state.user["userId"])

@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: str, request: Request):
    try:
        return await EventController.get_event(event_id, request.state.user["userId"])
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
