from ..config.connection import mongodb_connection

class Migration001:
    """Initial migration - Create collections and basic indexes"""
    
    version = "001"
    description = "Initial database setup"
    
    @staticmethod
    def up():
        """Apply migration"""
        db = mongodb_connection.database
        
        # Create collections (they will be created implicitly on first insert)
        collections = ["users", "events", "alerts", "incidents", "audit_logs"]
        
        # Create initial indexes
        from ..indexes import create_event_indexes, create_alert_indexes, create_audit_indexes
        
        create_event_indexes()
        create_alert_indexes()
        create_audit_indexes()
        
        # Create system metadata collection
        if "system_metadata" not in db.list_collection_names():
            db.create_collection("system_metadata")
        
        # Store migration record
        db.system_metadata.insert_one({
            "migration": "001",
            "applied_at": mongodb_connection.database.command("serverStatus")["localTime"],
            "description": "Initial database setup"
        })
        
        print(f"Migration {Migration001.version} applied successfully")
    
    @staticmethod
    def down():
        """Rollback migration"""
        # Drop all collections
        db = mongodb_connection.database
        collections = ["users", "events", "alerts", "incidents", "audit_logs", "system_metadata"]
        for collection in collections:
            if collection in db.list_collection_names():
                db[collection].drop()
        
        print(f"Migration {Migration001.version} rolled back")