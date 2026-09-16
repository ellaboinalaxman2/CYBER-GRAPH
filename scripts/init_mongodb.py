import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mongodb.config.connection import mongodb_connection
from mongodb.indexes import create_event_indexes, create_alert_indexes, create_audit_indexes

def init_mongodb():
    """Initialize MongoDB with indexes and collections"""
    
    print("=" * 60)
    print("Initializing MongoDB")
    print("=" * 60)
    
    try:
        # Check connection
        if not mongodb_connection.health_check():
            print("❌ MongoDB connection failed")
            return False
        
        print("✅ MongoDB connection successful")
        
        # Get database
        db = mongodb_connection.database
        
        # Create collections
        collections = ["users", "events", "alerts", "incidents", "audit_logs", "system_metadata"]
        for collection in collections:
            if collection not in db.list_collection_names():
                db.create_collection(collection)
                print(f"✅ Created collection: {collection}")
            else:
                print(f"Collection already exists: {collection}")
        
        # Create indexes
        print("\nCreating indexes...")
        create_event_indexes()
        create_alert_indexes()
        create_audit_indexes()
        
        print("\n✅ MongoDB initialization complete")
        return True
        
    except Exception as e:
        print(f"❌ MongoDB initialization failed: {e}")
        return False

if __name__ == "__main__":
    init_mongodb()