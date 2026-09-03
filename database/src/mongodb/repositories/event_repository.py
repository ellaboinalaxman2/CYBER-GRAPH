"""Event repository for MongoDB operations."""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError
from typing import Dict, Any

from src.core.logging import get_logger
from src.core.exceptions import MongoDBError, DocumentNotFoundError
from src.mongodb.connection import mongodb
from src.mongodb.models.event import EventModel


class EventRepository:
    """
    Repository for event operations in MongoDB.
    
    Features:
    - Create, read, update, delete events
    - Query events by various filters
    - Index management
    """
    
    def __init__(self):
        """Initialize the event repository."""
        self.logger = get_logger("mongodb.event_repository")
        self.collection = mongodb.get_collection("events")
        self._ensure_indexes()
    
    def _ensure_indexes(self) -> None:
        """Create indexes for common queries."""
        try:
            # Single field indexes
            self.collection.create_index("event_id", unique=True)
            self.collection.create_index([("timestamp", DESCENDING)])
            self.collection.create_index("event_type")
            self.collection.create_index("severity")
            self.collection.create_index("source_ip")
            self.collection.create_index("destination_ip")
            
            # Compound indexes
            self.collection.create_index([
                ("timestamp", DESCENDING),
                ("event_type", ASCENDING),
            ])
            self.collection.create_index([
                ("source_ip", ASCENDING),
                ("destination_ip", ASCENDING),
            ])
            
            self.logger.info("Event indexes created")
        except Exception as e:
            self.logger.warning(f"Failed to create indexes: {e}")
    
    def create(self, event: EventModel) -> Dict[str, Any]:
        """
        Create a new event.
        
        Args:
            event: Event model
            
        Returns:
            Dict[str, Any]: Created event
        """
        try:
            event_dict = event.dict()
            self.collection.insert_one(event_dict)
            self.logger.info(f"Created event: {event.event_id}")
            return event_dict
        except DuplicateKeyError:
            raise MongoDBError(f"Event {event.event_id} already exists")
        except Exception as e:
            self.logger.error(f"Failed to create event: {e}")
            raise MongoDBError(f"Failed to create event: {e}")
    
    def get_by_id(self, event_id: str) -> Dict[str, Any]:
        """
        Get an event by ID.
        
        Args:
            event_id: Event ID
            
        Returns:
            Dict[str, Any]: Event document
        """
        try:
            event = self.collection.find_one({"event_id": event_id})
            if not event:
                raise DocumentNotFoundError(f"Event {event_id} not found")
            return event
        except DocumentNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to get event {event_id}: {e}")
            raise MongoDBError(f"Failed to get event: {e}")
    
    def get_all(
        self,
        limit: int = 100,
        skip: int = 0,
        sort_by: str = "timestamp",
        sort_order: str = "desc",
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get all events with filtering and pagination.
        
        Args:
            limit: Maximum number of events
            skip: Number of events to skip
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)
            filters: Query filters
            
        Returns:
            List[Dict[str, Any]]: List of events
        """
        try:
            query = filters or {}
            sort_dir = DESCENDING if sort_order == "desc" else ASCENDING
            
            cursor = self.collection.find(query).sort(sort_by, sort_dir).skip(skip).limit(limit)
            return list(cursor)
        except Exception as e:
            self.logger.error(f"Failed to get events: {e}")
            raise MongoDBError(f"Failed to get events: {e}")
    
    def update(self, event_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an event.
        
        Args:
            event_id: Event ID
            update_data: Data to update
            
        Returns:
            Dict[str, Any]: Updated event
        """
        try:
            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            result = self.collection.find_one_and_update(
                {"event_id": event_id},
                {"$set": update_data},
                return_document=True,
            )
            
            if not result:
                raise DocumentNotFoundError(f"Event {event_id} not found")
            
            self.logger.info(f"Updated event: {event_id}")
            return result
            
        except DocumentNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to update event {event_id}: {e}")
            raise MongoDBError(f"Failed to update event: {e}")
    
    def delete(self, event_id: str) -> bool:
        """
        Delete an event.
        
        Args:
            event_id: Event ID
            
        Returns:
            bool: True if deleted
        """
        try:
            result = self.collection.delete_one({"event_id": event_id})
            if result.deleted_count == 0:
                raise DocumentNotFoundError(f"Event {event_id} not found")
            
            self.logger.info(f"Deleted event: {event_id}")
            return True
            
        except DocumentNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to delete event {event_id}: {e}")
            raise MongoDBError(f"Failed to delete event: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get event statistics.
        
        Returns:
            Dict[str, Any]: Statistics
        """
        try:
            total = self.collection.count_documents({})
            
            # Get earliest and latest
            earliest = self.collection.find_one(sort=[("timestamp", ASCENDING)])
            latest = self.collection.find_one(sort=[("timestamp", DESCENDING)])
            
            return {
                "total_events": total,
                "earliest_event": earliest["timestamp"] if earliest else None,
                "latest_event": latest["timestamp"] if latest else None,
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get statistics: {e}")
            return {"total_events": 0}