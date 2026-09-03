"""Alert repository for MongoDB operations."""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError
from typing import Dict, Any

from src.core.logging import get_logger
from src.core.exceptions import MongoDBError, DocumentNotFoundError
from src.mongodb.connection import mongodb
from src.mongodb.models.alert import AlertModel


class AlertRepository:
    """
    Repository for alert operations in MongoDB.
    
    Features:
    - Create, read, update, delete alerts
    - Query alerts by various filters
    - Status management
    - Assignment management
    """
    
    def __init__(self):
        """Initialize the alert repository."""
        self.logger = get_logger("mongodb.alert_repository")
        self.collection = mongodb.get_collection("alerts")
        self._ensure_indexes()
    
    def _ensure_indexes(self) -> None:
        """Create indexes for common queries."""
        try:
            self.collection.create_index("alert_id", unique=True)
            self.collection.create_index("incident_id")
            self.collection.create_index("severity")
            self.collection.create_index("status")
            self.collection.create_index("assigned_to")
            self.collection.create_index([
    ("created_at", DESCENDING)
])
            self.collection.create_index([
    ("risk_score", DESCENDING)
])
            self.collection.create_index([
                ("severity", ASCENDING),
                ("status", ASCENDING),
            ])
            self.collection.create_index([
                ("risk_score", DESCENDING),
                ("created_at", DESCENDING),
            ])
            self.logger.info("Alert indexes created")
        except Exception as e:
            self.logger.warning(f"Failed to create alert indexes: {e}")
    
    def create(self, alert: AlertModel) -> Dict[str, Any]:
        """Create a new alert."""
        try:
            alert_dict = alert.dict()
            self.collection.insert_one(alert_dict)
            self.logger.info(f"Created alert: {alert.alert_id}")
            return alert_dict
        except DuplicateKeyError:
            raise MongoDBError(f"Alert {alert.alert_id} already exists")
        except Exception as e:
            self.logger.error(f"Failed to create alert: {e}")
            raise MongoDBError(f"Failed to create alert: {e}")
    
    def get_by_id(self, alert_id: str) -> Dict[str, Any]:
        """Get an alert by ID."""
        try:
            alert = self.collection.find_one({"alert_id": alert_id})
            if not alert:
                raise DocumentNotFoundError(f"Alert {alert_id} not found")
            return alert
        except DocumentNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to get alert {alert_id}: {e}")
            raise MongoDBError(f"Failed to get alert: {e}")
    
    def get_all(
        self,
        limit: int = 100,
        skip: int = 0,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Get all alerts with filtering and pagination."""
        try:
            query = filters or {}
            sort_dir = DESCENDING if sort_order == "desc" else ASCENDING
            
            cursor = self.collection.find(query).sort(sort_by, sort_dir).skip(skip).limit(limit)
            return list(cursor)
        except Exception as e:
            self.logger.error(f"Failed to get alerts: {e}")
            raise MongoDBError(f"Failed to get alerts: {e}")
    
    def get_by_status(self, status: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get alerts by status."""
        try:
            cursor = self.collection.find({"status": status}).sort("created_at", DESCENDING).limit(limit)
            return list(cursor)
        except Exception as e:
            self.logger.error(f"Failed to get alerts by status: {e}")
            raise MongoDBError(f"Failed to get alerts by status: {e}")
    
    def get_by_severity(self, severity: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get alerts by severity."""
        try:
            cursor = self.collection.find({"severity": severity}).sort("created_at", DESCENDING).limit(limit)
            return list(cursor)
        except Exception as e:
            self.logger.error(f"Failed to get alerts by severity: {e}")
            raise MongoDBError(f"Failed to get alerts by severity: {e}")
    
    def update_status(self, alert_id: str, status: str, updated_by: Optional[str] = None) -> Dict[str, Any]:
        """Update alert status."""
        try:
            update_data = {"status": status, "updated_at": datetime.utcnow()}
            if status == "RESOLVED":
                update_data["resolved_at"] = datetime.utcnow()
                if updated_by:
                    update_data["resolved_by"] = updated_by
            
            result = self.collection.find_one_and_update(
                {"alert_id": alert_id},
                {"$set": update_data},
                return_document=True,
            )
            
            if not result:
                raise DocumentNotFoundError(f"Alert {alert_id} not found")
            
            self.logger.info(f"Updated alert {alert_id} status to {status}")
            return result
        except DocumentNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to update alert status: {e}")
            raise MongoDBError(f"Failed to update alert status: {e}")
    
    def assign(self, alert_id: str, assigned_to: str) -> Dict[str, Any]:
        """Assign alert to an analyst."""
        try:
            result = self.collection.find_one_and_update(
                {"alert_id": alert_id},
                {"$set": {"assigned_to": assigned_to, "updated_at": datetime.utcnow()}},
                return_document=True,
            )
            
            if not result:
                raise DocumentNotFoundError(f"Alert {alert_id} not found")
            
            self.logger.info(f"Assigned alert {alert_id} to {assigned_to}")
            return result
        except DocumentNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to assign alert: {e}")
            raise MongoDBError(f"Failed to assign alert: {e}")
    
    def add_note(self, alert_id: str, note: str, author: str) -> Dict[str, Any]:
        """Add a note to an alert."""
        try:
            note_entry = {
                "note": note,
                "author": author,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
            
            result = self.collection.find_one_and_update(
                {"alert_id": alert_id},
                {
                    "$push": {"notes": note_entry},
                    "$set": {"updated_at": datetime.utcnow()}
                },
                return_document=True,
            )
            
            if not result:
                raise DocumentNotFoundError(f"Alert {alert_id} not found")
            
            self.logger.info(f"Added note to alert {alert_id}")
            return result
        except DocumentNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to add note: {e}")
            raise MongoDBError(f"Failed to add note: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get alert statistics."""
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
            
            # Open alerts by severity
            open_alerts = self.collection.count_documents({"status": {"$ne": "CLOSED"}})
            critical_open = self.collection.count_documents({"status": {"$ne": "CLOSED"}, "severity": "CRITICAL"})
            
            return {
                "total_alerts": total,
                "open_alerts": open_alerts,
                "critical_open": critical_open,
                "status_distribution": status_dist,
                "severity_distribution": severity_dist,
            }
        except Exception as e:
            self.logger.error(f"Failed to get alert statistics: {e}")
            return {"total_alerts": 0}