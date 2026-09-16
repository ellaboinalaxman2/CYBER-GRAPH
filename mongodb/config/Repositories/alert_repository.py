from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from ..models.alert import AlertModel, AlertSeverity, AlertStatus
from .base_repository import BaseRepository

class AlertRepository(BaseRepository):
    """Repository for alert operations"""
    
    def __init__(self):
        super().__init__("alerts")
    
    def create_alert(self, alert_data: Dict[str, Any]) -> InsertOneResult:
        """Create a new alert"""
        alert_doc = AlertModel.create(alert_data)
        return self.create(alert_doc)
    
    def get_alert_by_id(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """Get alert by ID"""
        return self.find_by_id(alert_id, "alert_id")
    
    def get_alerts(self, limit: int = 100, skip: int = 0,
                   status: Optional[AlertStatus] = None,
                   severity: Optional[AlertSeverity] = None) -> List[Dict[str, Any]]:
        """Get alerts with filters"""
        query = {}
        if status:
            query["status"] = status
        if severity:
            query["severity"] = severity
        return self.find(query, limit=limit, skip=skip, sort=[("created_at", -1)])
    
    def get_open_alerts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get open alerts"""
        return self.find({
            "status": {"$in": [AlertStatus.OPEN, AlertStatus.UNDER_INVESTIGATION]}
        }, limit=limit, sort=[("risk_score", -1), ("created_at", -1)])
    
    def get_alerts_by_severity(self, severity: AlertSeverity, limit: int = 100) -> List[Dict[str, Any]]:
        """Get alerts by severity"""
        return self.find({"severity": severity}, limit=limit, sort=[("created_at", -1)])
    
    def get_critical_alerts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get critical alerts"""
        return self.get_alerts_by_severity(AlertSeverity.CRITICAL, limit)
    
    def get_alerts_by_risk_score(self, min_score: float = 0, max_score: float = 100,
                                  limit: int = 100) -> List[Dict[str, Any]]:
        """Get alerts by risk score range"""
        return self.find({
            "risk_score": {"$gte": min_score, "$lte": max_score}
        }, limit=limit, sort=[("risk_score", -1)])
    
    def get_alerts_by_incident(self, incident_id: str) -> List[Dict[str, Any]]:
        """Get alerts for an incident"""
        return self.find({"incident_id": incident_id}, sort=[("created_at", -1)])
    
    def get_alerts_by_node(self, node_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get alerts affecting a node"""
        return self.find({
            "affected_nodes": node_id
        }, limit=limit, sort=[("created_at", -1)])
    
    def get_alerts_by_source(self, source: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get alerts by source"""
        return self.find({"source": source}, limit=limit, sort=[("created_at", -1)])
    
    def update_alert_status(self, alert_id: str, status: AlertStatus,
                            resolved_at: Optional[datetime] = None) -> UpdateResult:
        """Update alert status"""
        update_data = {"status": status}
        if status in [AlertStatus.RESOLVED, AlertStatus.CLOSED, AlertStatus.CONFIRMED,
                      AlertStatus.FALSE_POSITIVE]:
            update_data["resolved_at"] = resolved_at or datetime.utcnow()
        return self.update_by_id(alert_id, update_data, "alert_id")
    
    def assign_alert(self, alert_id: str, assigned_to: str) -> UpdateResult:
        """Assign alert to analyst"""
        return self.update_by_id(alert_id, {"assigned_to": assigned_to}, "alert_id")
    
    def add_investigation_note(self, alert_id: str, note: Dict[str, Any]) -> UpdateResult:
        """Add investigation note to alert"""
        alert = self.get_alert_by_id(alert_id)
        if alert:
            notes = alert.get("investigation_notes", [])
            notes.append({
                "timestamp": datetime.utcnow(),
                **note
            })
            return self.update_by_id(alert_id, {"investigation_notes": notes}, "alert_id")
        return None
    
    def add_blockchain_record(self, alert_id: str, blockchain_hash: str, 
                              blockchain_tx_id: str) -> UpdateResult:
        """Add blockchain record to alert"""
        return self.update_by_id(alert_id, {
            "blockchain_hash": blockchain_hash,
            "blockchain_tx_id": blockchain_tx_id
        }, "alert_id")
    
    def escalate_alert(self, alert_id: str) -> UpdateResult:
        """Escalate alert"""
        return self.update_by_id(alert_id, {"escalated": True}, "alert_id")
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics"""
        total = self.count()
        by_status = self.aggregate([
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ])
        by_severity = self.aggregate([
            {"$group": {"_id": "$severity", "count": {"$sum": 1}}}
        ])
        open_alerts = self.count({"status": {"$in": [AlertStatus.OPEN, 
                                                      AlertStatus.UNDER_INVESTIGATION]}})
        critical_open = self.count({
            "severity": AlertSeverity.CRITICAL,
            "status": {"$in": [AlertStatus.OPEN, AlertStatus.UNDER_INVESTIGATION]}
        })
        avg_risk = self.aggregate([
            {"$group": {"_id": None, "avg_risk": {"$avg": "$risk_score"}}}
        ])
        
        return {
            "total_alerts": total,
            "open_alerts": open_alerts,
            "critical_open": critical_open,
            "alerts_by_status": by_status,
            "alerts_by_severity": by_severity,
            "average_risk_score": avg_risk[0]["avg_risk"] if avg_risk else 0
        }
    
    def get_recent_alerts(self, minutes: int = 60) -> List[Dict[str, Any]]:
        """Get alerts from last N minutes"""
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        return self.find({
            "timestamp": {"$gte": cutoff}
        }, sort=[("timestamp", -1)])
    
    def search_alerts(self, search_term: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Search alerts by various fields"""
        return self.find({
            "$or": [
                {"attack_type": {"$regex": search_term, "$options": "i"}},
                {"description": {"$regex": search_term, "$options": "i"}},
                {"attack_technique": {"$regex": search_term, "$options": "i"}},
                {"source": {"$regex": search_term, "$options": "i"}},
                {"target": {"$regex": search_term, "$options": "i"}}
            ]
        }, limit=limit, sort=[("created_at", -1)])