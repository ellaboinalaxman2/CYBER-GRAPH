from pymongo import IndexModel, ASCENDING, DESCENDING
from pymongo.collection import Collection
from ..config.connection import mongodb_connection

def create_event_indexes():
    """Create indexes for events collection"""
    
    collection = mongodb_connection.get_collection("events")
    
    indexes = [
        # Primary indexes for common queries
        IndexModel([("event_id", ASCENDING)], unique=True, name="event_id_unique"),
        IndexModel([("timestamp", DESCENDING)], name="timestamp_desc"),
        IndexModel([("source", ASCENDING), ("timestamp", DESCENDING)], 
                   name="source_timestamp"),
        IndexModel([("destination", ASCENDING), ("timestamp", DESCENDING)], 
                   name="destination_timestamp"),
        IndexModel([("source", ASCENDING), ("destination", ASCENDING), ("timestamp", DESCENDING)], 
                   name="source_dest_timestamp"),
        
        # Protocol and event type indexes
        IndexModel([("protocol", ASCENDING), ("timestamp", DESCENDING)], 
                   name="protocol_timestamp"),
        IndexModel([("event_type", ASCENDING), ("timestamp", DESCENDING)], 
                   name="event_type_timestamp"),
        
        # Anomaly detection indexes
        IndexModel([("is_anomaly", ASCENDING), ("anomaly_score", DESCENDING)], 
                   name="anomaly_score"),
        IndexModel([("is_anomaly", ASCENDING), ("timestamp", DESCENDING)], 
                   name="anomaly_timestamp"),
        
        # User and process indexes
        IndexModel([("user", ASCENDING), ("timestamp", DESCENDING)], 
                   name="user_timestamp"),
        IndexModel([("process", ASCENDING), ("timestamp", DESCENDING)], 
                   name="process_timestamp"),
        
        # Source hostname and destination hostname
        IndexModel([("source_hostname", ASCENDING), ("timestamp", DESCENDING)], 
                   name="source_hostname_timestamp"),
        IndexModel([("destination_hostname", ASCENDING), ("timestamp", DESCENDING)], 
                   name="dest_hostname_timestamp"),
        
        # Tags index for filtering
        IndexModel([("tags", ASCENDING)], name="tags"),
        
        # Text search index
        IndexModel([("message", "text"), ("raw_log", "text")], 
                   name="text_search"),
        
        # Date range for cleanup
        IndexModel([("ingestion_timestamp", ASCENDING)], 
                   name="ingestion_timestamp_asc"),
    ]
    
    collection.create_indexes(indexes)
    print("Created indexes for events collection")

def drop_event_indexes():
    """Drop all indexes for events collection"""
    collection = mongodb_connection.get_collection("events")
    collection.drop_indexes()
    print("Dropped indexes for events collection")