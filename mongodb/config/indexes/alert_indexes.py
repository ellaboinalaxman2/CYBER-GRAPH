from pymongo import IndexModel, ASCENDING, DESCENDING
from ..config.connection import mongodb_connection

def create_alert_indexes():
    """Create indexes for alerts collection"""
    
    collection = mongodb_connection.get_collection("alerts")
    
    indexes = [
        # Primary indexes
        IndexModel([("alert_id", ASCENDING)], unique=True, name="alert_id_unique"),
        IndexModel([("incident_id", ASCENDING)], name="incident_id"),
        IndexModel([("timestamp", DESCENDING)], name="timestamp_desc"),
        
        # Status and severity indexes
        IndexModel([("status", ASCENDING), ("timestamp", DESCENDING)], 
                   name="status_timestamp"),
        IndexModel([("severity", ASCENDING), ("timestamp", DESCENDING)], 
                   name="severity_timestamp"),
        IndexModel([("severity", ASCENDING), ("status", ASCENDING), ("timestamp", DESCENDING)], 
                   name="severity_status_timestamp"),
        
        # Risk score indexes
        IndexModel([("risk_score", DESCENDING)], name="risk_score_desc"),
        IndexModel([("risk_score", DESCENDING), ("timestamp", DESCENDING)], 
                   name="risk_score_timestamp"),
        
        # Source and target indexes
        IndexModel([("source", ASCENDING), ("timestamp", DESCENDING)], 
                   name="source_timestamp"),
        IndexModel([("target", ASCENDING), ("timestamp", DESCENDING)], 
                   name="target_timestamp"),
        
        # Attack type and technique indexes
        IndexModel([("attack_type", ASCENDING), ("timestamp", DESCENDING)], 
                   name="attack_type_timestamp"),
        IndexModel([("attack_technique", ASCENDING), ("timestamp", DESCENDING)], 
                   name="attack_technique_timestamp"),
        IndexModel([("attack_technique_id", ASCENDING)], name="attack_technique_id"),
        
        # Affected nodes index
        IndexModel([("affected_nodes", ASCENDING)], name="affected_nodes"),
        
        # Blockchain indexes
        IndexModel([("blockchain_hash", ASCENDING)], name="blockchain_hash"),
        IndexModel([("blockchain_tx_id", ASCENDING)], name="blockchain_tx_id"),
        
        # Escalation index
        IndexModel([("escalated", ASCENDING), ("status", ASCENDING)], 
                   name="escalated_status"),
        
        # Text search index
        IndexModel([("description", "text"), ("attack_type", "text")], 
                   name="text_search"),
        
        # Assigned to index
        IndexModel([("assigned_to", ASCENDING), ("status", ASCENDING)], 
                   name="assigned_to_status"),
        
        # Resolution time for metrics
        IndexModel([("resolved_at", ASCENDING)], name="resolved_at"),
    ]
    
    collection.create_indexes(indexes)
    print("Created indexes for alerts collection")

def drop_alert_indexes():
    """Drop all indexes for alerts collection"""
    collection = mongodb_connection.get_collection("alerts")
    collection.drop_indexes()
    print("Dropped indexes for alerts collection")