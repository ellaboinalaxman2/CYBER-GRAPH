from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from ..models.audit_log import AuditLogModel, AuditAction
from .base_repository import BaseRepository

class AuditRepository(BaseRepository):
    """Repository for audit log operations"""
    
    def __init__(self):
        super().__init__("audit_logs")
    
    def create_audit_log(self, audit_data: Dict[str, Any]) -> InsertOneResult:
        """Create a new audit log entry"""
        audit_doc = AuditLogModel.create(audit_data)
        return self.create(audit_doc)
    
    def get_audit_by_id(self, audit_id: str) -> Optional[Dict[str, Any]]:
        """Get audit log by ID"""
        return self.find_by_id(audit_id, "audit_id")
    
    def get_audit_logs(self, limit: int = 100, skip: int = 0,
                       user_id: Optional[str] = None,
                       action: Optional[AuditAction] = None,
                       start_time: Optional[datetime] = None,
                       end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get audit logs with filters"""
        query = {}
        if user_id:
            query["user_id"] = user_id
        if action:
            query["action"] = action
        if start_time or end_time:
            query["timestamp"] = {}
            if start_time:
                query["timestamp"]["$gte"] = start_time
            if end_time:
                query["timestamp"]["$lte"] = end_time
        return self.find(query, limit=limit, skip=skip, sort=[("timestamp", -1)])
    
    def get_audit_logs_by_user(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit logs by user"""
        return self.find({"user_id": user_id}, limit=limit, sort=[("timestamp", -1)])
    
    def get_audit_logs_by_action(self, action: AuditAction, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit logs by action"""
        return self.find({"action": action}, limit=limit, sort=[("timestamp", -1)])
    
    def get_audit_logs_by_resource(self, resource_type: str, resource_id: str,
                                    limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit logs by resource"""
        return self.find({
            "resource_type": resource_type,
            "resource_id": resource_id
        }, limit=limit, sort=[("timestamp", -1)])
    
    def get_audit_logs_by_time_range(self, start_time: datetime, end_time: datetime,
                                      limit: int = 1000) -> List[Dict[str, Any]]:
        """Get audit logs within time range"""
        return self.find({
            "timestamp": {"$gte": start_time, "$lte": end_time}
        }, limit=limit, sort=[("timestamp", 1)])
    
    def get_recent_audit_logs(self, minutes: int = 60, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit logs from last N minutes"""
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        return self.find({"timestamp": {"$gte": cutoff}}, limit=limit, sort=[("timestamp", -1)])
    
    def get_audit_statistics(self) -> Dict[str, Any]:
        """Get audit log statistics"""
        total = self.count()
        by_action = self.aggregate([
            {"$group": {"_id": "$action", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ])
        by_user = self.aggregate([
            {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ])
        success_count = self.count({"success": True})
        failure_count = self.count({"success": False})
        last_hour = self.count({
            "timestamp": {"$gte": datetime.utcnow() - timedelta(hours=1)}
        })
        
        return {
            "total_audit_logs": total,
            "successful_actions": success_count,
            "failed_actions": failure_count,
            "success_rate": (success_count / total * 100) if total > 0 else 0,
            "actions_by_type": by_action,
            "top_users": by_user,
            "audit_logs_last_hour": last_hour
        }
    
    def search_audit_logs(self, search_term: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Search audit logs by various fields"""
        return self.find({
            "$or": [
                {"username": {"$regex": search_term, "$options": "i"}},
                {"details": {"$regex": search_term, "$options": "i"}},
                {"resource_type": {"$regex": search_term, "$options": "i"}},
                {"resource_id": {"$regex": search_term, "$options": "i"}}
            ]
        }, limit=limit, sort=[("timestamp", -1)])