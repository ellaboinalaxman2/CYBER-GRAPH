from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from ..models.incident import IncidentModel, IncidentStatus
from .base_repository import BaseRepository

class IncidentRepository(BaseRepository):
    """Repository for incident operations"""
    
    def __init__(self):
        super().__init__("incidents")
    
    def create_incident(self, incident_data: Dict[str, Any]) -> InsertOneResult:
        """Create a new incident"""
        incident_doc = IncidentModel.create(incident_data)
        return self.create(incident_doc)
    
    def get_incident_by_id(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Get incident by ID"""
        return self.find_by_id(incident_id, "incident_id")
    
    def get_incidents(self, limit: int = 100, skip: int = 0,
                      status: Optional[IncidentStatus] = None,
                      priority: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get incidents with filters"""
        query = {}
        if status:
            query["status"] = status
        if priority:
            query["priority"] = priority
        return self.find(query, limit=limit, skip=skip, sort=[("created_at", -1)])
    
    def get_open_incidents(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get open incidents"""
        return self.find({
            "status": {"$nin": [IncidentStatus.CLOSED, IncidentStatus.RECOVERED]}
        }, limit=limit, sort=[("priority", 1), ("created_at", -1)])
    
    def get_incidents_by_severity(self, severity: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get incidents by severity"""
        return self.find({"severity": severity}, limit=limit, sort=[("created_at", -1)])
    
    def get_incidents_by_time_range(self, start_time: datetime, end_time: datetime,
                                     limit: int = 100) -> List[Dict[str, Any]]:
        """Get incidents within time range"""
        return self.find({
            "timestamp_start": {"$gte": start_time, "$lte": end_time}
        }, limit=limit, sort=[("timestamp_start", -1)])
    
    def update_incident_status(self, incident_id: str, status: IncidentStatus) -> UpdateResult:
        """Update incident status"""
        update_data = {"status": status}
        if status == IncidentStatus.CLOSED:
            update_data["closed_at"] = datetime.utcnow()
        return self.update_by_id(incident_id, update_data, "incident_id")
    
    def assign_incident(self, incident_id: str, assigned_to: str) -> UpdateResult:
        """Assign incident to team/analyst"""
        return self.update_by_id(incident_id, {"assigned_to": assigned_to}, "incident_id")
    
    def add_investigation_log_entry(self, incident_id: str, entry: Dict[str, Any]) -> UpdateResult:
        """Add investigation log entry"""
        incident = self.get_incident_by_id(incident_id)
        if incident:
            log = incident.get("investigation_log", [])
            log.append({
                "timestamp": datetime.utcnow(),
                **entry
            })
            return self.update_by_id(incident_id, {"investigation_log": log}, "incident_id")
        return None
    
    def add_evidence(self, incident_id: str, evidence: Dict[str, Any]) -> UpdateResult:
        """Add evidence to incident"""
        incident = self.get_incident_by_id(incident_id)
        if incident:
            evidence_list = incident.get("evidence", [])
            evidence_list.append({
                "timestamp": datetime.utcnow(),
                **evidence
            })
            return self.update_by_id(incident_id, {"evidence": evidence_list}, "incident_id")
        return None
    
    def add_indicator_of_compromise(self, incident_id: str, ioc: Dict[str, Any]) -> UpdateResult:
        """Add IOC to incident"""
        incident = self.get_incident_by_id(incident_id)
        if incident:
            iocs = incident.get("indicators_of_compromise", [])
            iocs.append({
                "timestamp": datetime.utcnow(),
                **ioc
            })
            return self.update_by_id(incident_id, {"indicators_of_compromise": iocs}, "incident_id")
        return None
    
    def update_remediation_status(self, incident_id: str, completed: bool) -> UpdateResult:
        """Update remediation completion status"""
        return self.update_by_id(incident_id, {"remediation_completed": completed}, "incident_id")
    
    def get_incident_statistics(self) -> Dict[str, Any]:
        """Get incident statistics"""
        total = self.count()
        open_count = self.count({
            "status": {"$nin": [IncidentStatus.CLOSED, IncidentStatus.RECOVERED]}
        })
        by_status = self.aggregate([
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ])
        by_severity = self.aggregate([
            {"$group": {"_id": "$severity", "count": {"$sum": 1}}}
        ])
        avg_time_to_detect = self.aggregate([
            {"$match": {"time_to_detect": {"$exists": True}}},
            {"$group": {"_id": None, "avg": {"$avg": "$time_to_detect"}}}
        ])
        avg_time_to_respond = self.aggregate([
            {"$match": {"time_to_respond": {"$exists": True}}},
            {"$group": {"_id": None, "avg": {"$avg": "$time_to_respond"}}}
        ])
        
        return {
            "total_incidents": total,
            "open_incidents": open_count,
            "incidents_by_status": by_status,
            "incidents_by_severity": by_severity,
            "avg_time_to_detect_seconds": avg_time_to_detect[0]["avg"] if avg_time_to_detect else 0,
            "avg_time_to_respond_seconds": avg_time_to_respond[0]["avg"] if avg_time_to_respond else 0
        }