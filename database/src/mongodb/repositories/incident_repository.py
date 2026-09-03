"""Incident repository for MongoDB operations."""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError
from typing import Dict, Any

from src.core.logging import get_logger
from src.core.exceptions import MongoDBError, DocumentNotFoundError
from src.mongodb.connection import mongodb
from src.mongodb.models.incident import IncidentModel


class IncidentRepository:
    """
    Repository for incident operations in MongoDB.
    
    Features:
    - Create, read, update, delete incidents
    - Query incidents by various filters
    - Status management
    - Timeline tracking
    """
    
    def __init__(self):
        """Initialize the incident repository."""
        self.logger = get_logger("mongodb.incident_repository")
        self.collection = mongodb.get_collection("incidents")
        self._ensure_indexes()
    
    def _ensure_indexes(self) -> None:
        """Create indexes for common queries."""
        try:
            self.collection.create_index("incident_id", unique=True)
            self.collection.create_index("severity")
            self.collection.create_index("status")
            self.collection.create_index("assigned_to")
            self.collection.create_index([
    ("started_at", DESCENDING)
])
            self.collection.create_index([
    ("risk_score", DESCENDING)
])
            self.collection.create_index([
                ("severity", ASCENDING),
                ("status", ASCENDING),
            ])
            self.logger.info("Incident indexes created")
        except Exception as e:
            self.logger.warning(f"Failed to create incident indexes: {e}")
    
    def create(self, incident: IncidentModel) -> Dict[str, Any]:
        """Create a new incident."""
        try:
            incident_dict = incident.dict()
            self.collection.insert_one(incident_dict)
            self.logger.info(f"Created incident: {incident.incident_id}")
            return incident_dict
        except DuplicateKeyError:
            raise MongoDBError(f"Incident {incident.incident_id} already exists")
        except Exception as e:
            self.logger.error(f"Failed to create incident: {e}")
            raise MongoDBError(f"Failed to create incident: {e}")
    
    def get_by_id(self, incident_id: str) -> Dict[str, Any]:
        """Get an incident by ID."""
        try:
            incident = self.collection.find_one({"incident_id": incident_id})
            if not incident:
                raise DocumentNotFoundError(f"Incident {incident_id} not found")
            return incident
        except DocumentNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to get incident {incident_id}: {e}")
            raise MongoDBError(f"Failed to get incident: {e}")
    
    def get_all(
        self,
        limit: int = 100,
        skip: int = 0,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Get all incidents with filtering and pagination."""
        try:
            query = filters or {}
            sort_dir = DESCENDING if sort_order == "desc" else ASCENDING
            
            cursor = self.collection.find(query).sort(sort_by, sort_dir).skip(skip).limit(limit)
            return list(cursor)
        except Exception as e:
            self.logger.error(f"Failed to get incidents: {e}")
            raise MongoDBError(f"Failed to get incidents: {e}")
    
    def get_by_status(self, status: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get incidents by status."""
        try:
            cursor = self.collection.find({"status": status}).sort("created_at", DESCENDING).limit(limit)
            return list(cursor)
        except Exception as e:
            self.logger.error(f"Failed to get incidents by status: {e}")
            raise MongoDBError(f"Failed to get incidents by status: {e}")
    
    def update_status(self, incident_id: str, status: str) -> Dict[str, Any]:
        """Update incident status with timeline tracking."""
        try:
            update_data = {"status": status, "updated_at": datetime.utcnow()}
            
            # Track timeline based on status
            status_map = {
                "CONTAINED": "contained_at",
                "ERADICATED": "eradicated_at",
                "RECOVERED": "recovered_at",
                "CLOSED": "resolved_at",
            }
            
            if status in status_map:
                update_data[status_map[status]] = datetime.utcnow()
            
            result = self.collection.find_one_and_update(
                {"incident_id": incident_id},
                {"$set": update_data},
                return_document=True,
            )
            
            if not result:
                raise DocumentNotFoundError(f"Incident {incident_id} not found")
            
            self.logger.info(f"Updated incident {incident_id} status to {status}")
            return result
        except DocumentNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to update incident status: {e}")
            raise MongoDBError(f"Failed to update incident status: {e}")
    
    def add_alert(self, incident_id: str, alert_id: str) -> Dict[str, Any]:
        """Add an alert to an incident."""
        try:
            result = self.collection.find_one_and_update(
                {"incident_id": incident_id},
                {
                    "$addToSet": {"alert_ids": alert_id},
                    "$set": {"updated_at": datetime.utcnow()}
                },
                return_document=True,
            )
            
            if not result:
                raise DocumentNotFoundError(f"Incident {incident_id} not found")
            
            self.logger.info(f"Added alert {alert_id} to incident {incident_id}")
            return result
        except DocumentNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to add alert to incident: {e}")
            raise MongoDBError(f"Failed to add alert to incident: {e}")
    
    def add_investigation_note(self, incident_id: str, note: str, author: str) -> Dict[str, Any]:
        """Add an investigation note to an incident."""
        try:
            note_entry = {
                "note": note,
                "author": author,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
            
            result = self.collection.find_one_and_update(
                {"incident_id": incident_id},
                {
                    "$push": {"investigation_notes": note_entry},
                    "$set": {"updated_at": datetime.utcnow()}
                },
                return_document=True,
            )
            
            if not result:
                raise DocumentNotFoundError(f"Incident {incident_id} not found")
            
            self.logger.info(f"Added investigation note to incident {incident_id}")
            return result
        except DocumentNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to add investigation note: {e}")
            raise MongoDBError(f"Failed to add investigation note: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get incident statistics."""
        try:
            total = self.collection.count_documents({})
            
            # Status distribution
            pipeline = [
                {"$group": {"_id": "$status", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
            ]
            status_dist = list(self.collection.aggregate(pipeline))
            
            # Severity distribution
            pipeline = [
                {"$group": {"_id": "$severity", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
            ]
            severity_dist = list(self.collection.aggregate(pipeline))
            
            # Open incidents
            open_incidents = self.collection.count_documents({"status": {"$nin": ["CLOSED", "RECOVERED"]}})
            
            return {
                "total_incidents": total,
                "open_incidents": open_incidents,
                "status_distribution": status_dist,
                "severity_distribution": severity_dist,
            }
        except Exception as e:
            self.logger.error(f"Failed to get incident statistics: {e}")
            return {"total_incidents": 0}