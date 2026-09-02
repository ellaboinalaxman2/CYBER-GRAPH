# app/services/event_service.py
from fastapi import HTTPException, status
from app.schemas.event import EventCreate, EventResponse
from app.config.database import MongoDB
from typing import List
import uuid
from datetime import datetime

class EventService:
    @staticmethod
    async def get_events(skip: int = 0, limit: int = 100) -> List[EventResponse]:
        if not MongoDB.get_db():
            return []
        
        cursor = MongoDB.get_db().events.find().skip(skip).limit(limit)
        events = await cursor.to_list(length=limit)
        return [EventResponse(**{**event, "id": str(event["_id"])}) for event in events]

    @staticmethod
    async def create_event(event: EventCreate) -> EventResponse:
        if not MongoDB.get_db():
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database not connected")
        
        event_dict = event.dict()
        event_dict["id"] = str(uuid.uuid4())
        event_dict["created_at"] = datetime.utcnow().isoformat()
        if not event_dict.get("timestamp"):
            event_dict["timestamp"] = datetime.utcnow().isoformat()
        
        result = await MongoDB.get_db().events.insert_one(event_dict)
        event_dict["id"] = str(result.inserted_id)
        
        return EventResponse(**event_dict)

    @staticmethod
    async def get_event(event_id: str) -> EventResponse:
        if not MongoDB.get_db():
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database not connected")
        
        try:
            from bson import ObjectId
            event = await MongoDB.get_db().events.find_one({"_id": ObjectId(event_id)})
            if not event:
                raise ValueError("Event not found")
            return EventResponse(**{**event, "id": str(event["_id"])})
        except Exception:
            raise ValueError("Invalid event ID")
