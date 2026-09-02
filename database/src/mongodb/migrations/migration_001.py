"""Migration 001: Add alert and incident collections."""

from datetime import datetime
from src.core.logging import get_logger
from src.mongodb.connection import mongodb


class Migration001:
    """
    Migration 001: Create alert and incident collections.
    
    Adds:
    - alerts collection with indexes
    - incidents collection with indexes
    - Event collection updates
    """
    
    def __init__(self):
        """Initialize the migration."""
        self.logger = get_logger("mongodb.migration_001")
        self.db = mongodb.get_database()
    
    def up(self) -> Dict[str, Any]:
        """
        Apply the migration.
        
        Returns:
            Dict[str, Any]: Migration results
        """
        self.logger.info("Running migration 001: Add alert and incident collections")
        results = {}
        
        # Create alerts collection
        try:
            self.db.create_collection("alerts")
            results["alerts_created"] = True
            self.logger.info("Created alerts collection")
        except Exception as e:
            if "already exists" in str(e):
                results["alerts_created"] = "already_exists"
            else:
                results["alerts_created"] = f"failed: {e}"
                self.logger.error(f"Failed to create alerts collection: {e}")
        
        # Create incidents collection
        try:
            self.db.create_collection("incidents")
            results["incidents_created"] = True
            self.logger.info("Created incidents collection")
        except Exception as e:
            if "already exists" in str(e):
                results["incidents_created"] = "already_exists"
            else:
                results["incidents_created"] = f"failed: {e}"
                self.logger.error(f"Failed to create incidents collection: {e}")
        
        # Add indexes to alerts
        try:
            alerts = self.db["alerts"]
            alerts.create_index("alert_id", unique=True)
            alerts.create_index("status")
            alerts.create_index("severity")
            alerts.create_index("created_at", -1)
            results["alert_indexes"] = "created"
            self.logger.info("Created alert indexes")
        except Exception as e:
            results["alert_indexes"] = f"failed: {e}"
            self.logger.error(f"Failed to create alert indexes: {e}")
        
        # Add indexes to incidents
        try:
            incidents = self.db["incidents"]
            incidents.create_index("incident_id", unique=True)
            incidents.create_index("status")
            incidents.create_index("severity")
            incidents.create_index("started_at", -1)
            results["incident_indexes"] = "created"
            self.logger.info("Created incident indexes")
        except Exception as e:
            results["incident_indexes"] = f"failed: {e}"
            self.logger.error(f"Failed to create incident indexes: {e}")
        
        results["migration_id"] = "001"
        results["timestamp"] = datetime.utcnow().isoformat() + "Z"
        
        return results
    
    def down(self) -> Dict[str, Any]:
        """
        Rollback the migration.
        
        Returns:
            Dict[str, Any]: Rollback results
        """
        self.logger.info("Rolling back migration 001")
        results = {}
        
        # Drop alerts collection
        try:
            self.db["alerts"].drop()
            results["alerts_dropped"] = True
            self.logger.info("Dropped alerts collection")
        except Exception as e:
            results["alerts_dropped"] = f"failed: {e}"
            self.logger.error(f"Failed to drop alerts collection: {e}")
        
        # Drop incidents collection
        try:
            self.db["incidents"].drop()
            results["incidents_dropped"] = True
            self.logger.info("Dropped incidents collection")
        except Exception as e:
            results["incidents_dropped"] = f"failed: {e}"
            self.logger.error(f"Failed to drop incidents collection: {e}")
        
        results["migration_id"] = "001"
        results["timestamp"] = datetime.utcnow().isoformat() + "Z"
        
        return results