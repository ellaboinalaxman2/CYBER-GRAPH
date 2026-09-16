from ..config.connection import mongodb_connection

class Migration002:
    """Add risk_score and blockchain fields to alerts"""
    
    version = "002"
    description = "Add risk_score and blockchain fields to alerts"
    
    @staticmethod
    def up():
        """Apply migration"""
        db = mongodb_connection.database
        alerts = db.alerts
        
        # Add new fields to existing documents
        alerts.update_many(
            {},
            {
                "$set": {
                    "risk_score": 0.0,
                    "confidence": 0.0,
                    "blockchain_hash": None,
                    "blockchain_tx_id": None,
                    "escalated": False,
                    "investigation_notes": []
                }
            }
        )
        
        # Create new indexes
        from ..indexes import create_alert_indexes
        create_alert_indexes()
        
        # Store migration record
        db.system_metadata.insert_one({
            "migration": "002",
            "applied_at": mongodb_connection.database.command("serverStatus")["localTime"],
            "description": "Add risk_score and blockchain fields to alerts"
        })
        
        print(f"Migration {Migration002.version} applied successfully")
    
    @staticmethod
    def down():
        """Rollback migration"""
        db = mongodb_connection.database
        alerts = db.alerts
        
        # Remove added fields
        alerts.update_many(
            {},
            {
                "$unset": {
                    "risk_score": "",
                    "confidence": "",
                    "blockchain_hash": "",
                    "blockchain_tx_id": "",
                    "escalated": "",
                    "investigation_notes": ""
                }
            }
        )
        
        print(f"Migration {Migration002.version} rolled back")