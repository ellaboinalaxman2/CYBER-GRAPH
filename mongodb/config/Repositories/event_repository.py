from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from ..models.event import EventModel, EventType
from .base_repository import BaseRepository

class EventRepository(BaseRepository):
    """Repository for event operations"""
    
    def __init__(self):
        super().__init__("events")
    
    def create_event(self, event_data: Dict[str, Any]) -> InsertOneResult:
        """Create a new event"""
        event_doc = EventModel.create(event_data)
        return self.create(event_doc)
    
    def create_events_bulk(self, events_data: List[Dict[str, Any]]) -> Any:
        """Create multiple events"""
        event_docs = [EventModel.create(data) for data in events_data]
        return self.create_many(event_docs)
    
    def get_event_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get event by ID"""
        return self.find_by_id(event_id, "event_id")
    
    def get_events(self, limit: int = 100, skip: int = 0,
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get events with time filter"""
        query = {}
        if start_time or end_time:
            query["timestamp"] = {}
            if start_time:
                query["timestamp"]["$gte"] = start_time
            if end_time:
                query["timestamp"]["$lte"] = end_time
        return self.find(query, limit=limit, skip=skip, sort=[("timestamp", -1)])
    
    def get_events_by_source(self, source: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get events by source"""
        return self.find({"source": source}, limit=limit, sort=[("timestamp", -1)])
    
    def get_events_by_destination(self, destination: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get events by destination"""
        return self.find({"destination": destination}, limit=limit, sort=[("timestamp", -1)])
    
    def get_events_by_event_type(self, event_type: EventType, limit: int = 100) -> List[Dict[str, Any]]:
        """Get events by event type"""
        return self.find({"event_type": event_type}, limit=limit, sort=[("timestamp", -1)])
    
    def get_events_by_protocol(self, protocol: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get events by protocol"""
        return self.find({"protocol": protocol}, limit=limit, sort=[("timestamp", -1)])
    
    def get_anomalous_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get anomalous events"""
        return self.find({"is_anomaly": True}, limit=limit, sort=[("anomaly_score", -1)])
    
    def get_events_by_time_range(self, start_time: datetime, end_time: datetime,
                                  limit: int = 1000) -> List[Dict[str, Any]]:
        """Get events within time range"""
        return self.find({
            "timestamp": {"$gte": start_time, "$lte": end_time}
        }, limit=limit, sort=[("timestamp", 1)])
    
    def get_recent_events(self, minutes: int = 60, limit: int = 100) -> List[Dict[str, Any]]:
        """Get events from last N minutes"""
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        return self.find({"timestamp": {"$gte": cutoff}}, limit=limit, sort=[("timestamp", -1)])
    
    def update_event_anomaly(self, event_id: str, is_anomaly: bool, 
                             anomaly_score: Optional[float] = None) -> UpdateResult:
        """Update event anomaly status"""
        update_data = {"is_anomaly": is_anomaly}
        if anomaly_score is not None:
            update_data["anomaly_score"] = anomaly_score
        return self.update_by_id(event_id, update_data, "event_id")
    
    def delete_events_older_than(self, days: int) -> DeleteResult:
        """Delete events older than N days"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        return self.delete_many({"timestamp": {"$lt": cutoff}})
    
    def get_event_statistics(self) -> Dict[str, Any]:
        """Get event statistics"""
        total = self.count()
        anomalous = self.count({"is_anomaly": True})
        by_type = self.aggregate([
            {"$group": {"_id": "$event_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ])
        by_protocol = self.aggregate([
            {"$group": {"_id": "$protocol", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ])
        last_hour = self.count({
            "timestamp": {"$gte": datetime.utcnow() - timedelta(hours=1)}
        })
        
        return {
            "total_events": total,
            "anomalous_events": anomalous,
            "anomaly_rate": (anomalous / total * 100) if total > 0 else 0,
            "events_by_type": by_type,
            "events_by_protocol": by_protocol,
            "events_last_hour": last_hour
        }
    
    def get_source_destination_pairs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get common source-destination pairs"""
        return self.aggregate([
            {"$group": {
                "_id": {"source": "$source", "destination": "$destination"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ])
    
    def search_events(self, search_term: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Search events by message or raw_log"""
        return self.find({
            "$or": [
                {"message": {"$regex": search_term, "$options": "i"}},
                {"raw_log": {"$regex": search_term, "$options": "i"}},
                {"source": {"$regex": search_term, "$options": "i"}},
                {"destination": {"$regex": search_term, "$options": "i"}}
            ]
        }, limit=limit, sort=[("timestamp", -1)])