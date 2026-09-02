"""MongoDB connection management."""

from typing import Optional, Dict, Any
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import MongoDBError


class MongoDBConnection:
    """
    MongoDB connection manager with connection pooling.
    
    Features:
    - Connection pooling
    - Health checks
    - Singleton pattern
    """
    
    _instance = None
    _client = None
    _database = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the MongoDB connection."""
        if not hasattr(self, '_initialized'):
            self.logger = get_logger("mongodb.connection")
            self._initialized = True
            self._connected = False
            self._connect()
    
    def _connect(self) -> None:
        """Establish connection to MongoDB."""
        try:
            self._client = MongoClient(
                settings.mongodb_uri,
                maxPoolSize=100,
                minPoolSize=10,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
            )
            
            # Test connection
            self._client.admin.command('ping')
            self._database = self._client[settings.mongodb_db]
            self._connected = True
            
            self.logger.info(
                f"Connected to MongoDB: {settings.mongodb_db}"
            )
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            self._connected = False
            self.logger.error(f"Failed to connect to MongoDB: {e}")
            raise MongoDBError(f"MongoDB connection failed: {e}")
        except Exception as e:
            self._connected = False
            self.logger.error(f"Unexpected MongoDB error: {e}")
            raise MongoDBError(f"MongoDB error: {e}")
    
    def get_client(self) -> MongoClient:
        """Get the MongoDB client."""
        if not self._connected or self._client is None:
            self._connect()
        return self._client
    
    def get_database(self):
        """Get the MongoDB database."""
        if not self._connected or self._database is None:
            self._connect()
        return self._database
    
    def get_collection(self, collection_name: str):
        """Get a MongoDB collection."""
        db = self.get_database()
        return db[collection_name]
    
    def is_connected(self) -> bool:
        """Check if connected to MongoDB."""
        try:
            if self._client:
                self._client.admin.command('ping')
                return True
            return False
        except Exception:
            return False
    
    def close(self) -> None:
        """Close the MongoDB connection."""
        if self._client:
            try:
                self._client.close()
                self._connected = False
                self.logger.info("MongoDB connection closed")
            except Exception as e:
                self.logger.error(f"Error closing MongoDB connection: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a health check."""
        try:
            if self.is_connected():
                return {
                    "status": "healthy",
                    "database": settings.mongodb_db,
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": "Connection failed",
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
            }


# Singleton instance
mongodb = MongoDBConnection()