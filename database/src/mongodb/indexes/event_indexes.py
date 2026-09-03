"""Event index management for MongoDB."""
from typing import Dict, Any, List
from src.core.logging import get_logger
from src.mongodb.connection import mongodb


class EventIndexManager:
    """
    Manages indexes for the events collection.
    
    Features:
    - Create optimized indexes
    - Drop unused indexes
    - Index statistics
    """
    
    def __init__(self):
        """Initialize the index manager."""
        self.logger = get_logger("mongodb.event_indexes")
        self.collection = mongodb.get_collection("events")
    
    def create_indexes(self) -> Dict[str, Any]:
        """
        Create all recommended indexes.
        
        Returns:
            Dict[str, Any]: Index creation results
        """
        results = {}
        
        # Single field indexes
        indexes = [
            ("event_id", {"unique": True}),
            ("timestamp", None),
            ("event_type", None),
            ("severity", None),
            ("source_ip", None),
            ("destination_ip", None),
        ]
        
        for field, options in indexes:
            try:
                if options:
                    self.collection.create_index(field, **options)
                else:
                    self.collection.create_index(field)
                results[field] = "created"
            except Exception as e:
                results[field] = f"failed: {e}"
        
        # Compound indexes
        compound_indexes = [
            [("timestamp", -1), ("event_type", 1)],
            [("source_ip", 1), ("destination_ip", 1)],
            [("severity", 1), ("timestamp", -1)],
        ]
        
        for idx in compound_indexes:
            try:
                self.collection.create_index(idx)
                results[f"compound_{len(idx)}"] = "created"
            except Exception as e:
                results[f"compound_{len(idx)}"] = f"failed: {e}"
        
        # Text index
        try:
            self.collection.create_index([
                ("message", "text"),
                ("event_id", "text"),
            ])
            results["text"] = "created"
        except Exception as e:
            results["text"] = f"failed: {e}"
        
        self.logger.info(f"Index creation results: {results}")
        return results
    
    def list_indexes(self) -> List[Dict[str, Any]]:
        """List all indexes on the collection."""
        try:
            return list(self.collection.list_indexes())
        except Exception as e:
            self.logger.error(f"Failed to list indexes: {e}")
            return []
    
    def drop_index(self, index_name: str) -> bool:
        """Drop a specific index."""
        try:
            self.collection.drop_index(index_name)
            self.logger.info(f"Dropped index: {index_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to drop index {index_name}: {e}")
            return False
    
    def get_index_sizes(self) -> Dict[str, int]:
        """Get index sizes."""
        try:
            stats = self.collection.aggregate([
                {"$indexStats": {}},
                {"$project": {"name": 1, "size": 1}},
            ])
            return {doc["name"]: doc["size"] for doc in stats}
        except Exception as e:
            self.logger.error(f"Failed to get index sizes: {e}")
            return {}