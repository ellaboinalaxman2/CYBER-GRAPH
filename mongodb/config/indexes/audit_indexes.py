from pymongo import IndexModel, ASCENDING, DESCENDING
from ..config.connection import mongodb_connection

def create_audit_indexes():
    """Create indexes for audit_logs collection"""
    
    collection = mongodb_connection.get_collection("audit_logs")
    
    indexes = [
        # Primary indexes
        IndexModel([("audit_id", ASCENDING)], unique=True, name="audit_id_unique"),
        IndexModel([("timestamp", DESCENDING)], name="timestamp_desc"),
        
        # User indexes
        IndexModel([("user_id", ASCENDING), ("timestamp", DESCENDING)], 
                   name="user_id_timestamp"),
        IndexModel([("username", ASCENDING), ("timestamp", DESCENDING)], 
                   name="username_timestamp"),
        
        # Action and resource indexes
        IndexModel([("action", ASCENDING), ("timestamp", DESCENDING)], 
                   name="action_timestamp"),
        IndexModel([("resource_type", ASCENDING), ("timestamp", DESCENDING)], 
                   name="resource_type_timestamp"),
        IndexModel([("resource_id", ASCENDING), ("timestamp", DESCENDING)], 
                   name="resource_id_timestamp"),
        IndexModel([("resource_type", ASCENDING), ("resource_id", ASCENDING), 
                    ("timestamp", DESCENDING)], 
                   name="resource_type_id_timestamp"),
        
        # Session and success indexes
        IndexModel([("session_id", ASCENDING)], name="session_id"),
        IndexModel([("success", ASCENDING), ("timestamp", DESCENDING)], 
                   name="success_timestamp"),
        
        # Source module index
        IndexModel([("source_module", ASCENDING), ("timestamp", DESCENDING)], 
                   name="source_module_timestamp"),
        
        # IP address index for security monitoring
        IndexModel([("ip_address", ASCENDING), ("timestamp", DESCENDING)], 
                   name="ip_address_timestamp"),
        
        # Text search index
        IndexModel([("details", "text")], name="text_search"),
    ]
    
    collection.create_indexes(indexes)
    print("Created indexes for audit_logs collection")

def drop_audit_indexes():
    """Drop all indexes for audit_logs collection"""
    collection = mongodb_connection.get_collection("audit_logs")
    collection.drop_indexes()
    print("Dropped indexes for audit_logs collection")