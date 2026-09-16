from typing import Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import logging
from .settings import MongoSettings

logger = logging.getLogger(__name__)

class MongoDBConnection:
    """MongoDB connection manager with singleton pattern"""
    
    _instance = None
    _client: Optional[MongoClient] = None
    _database = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.settings = MongoSettings()
        self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB"""
        try:
            self._client = MongoClient(
                self.settings.connection_string,
                maxPoolSize=self.settings.max_pool_size,
                minPoolSize=self.settings.min_pool_size,
                maxIdleTimeMS=self.settings.max_idle_time_ms,
                connectTimeoutMS=self.settings.connect_timeout_ms,
                socketTimeoutMS=self.settings.socket_timeout_ms,
                serverSelectionTimeoutMS=5000
            )
            # Test connection
            self._client.admin.command('ping')
            self._database = self._client[self.settings.database]
            logger.info(f"Connected to MongoDB at {self.settings.host}:{self.settings.port}")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    @property
    def client(self) -> MongoClient:
        """Get MongoDB client"""
        if self._client is None:
            self._connect()
        return self._client
    
    @property
    def database(self):
        """Get database instance"""
        if self._database is None:
            self._connect()
        return self._database
    
    def get_collection(self, collection_name: str):
        """Get a specific collection"""
        return self.database[collection_name]
    
    def close(self):
        """Close the connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None
            logger.info("MongoDB connection closed")
    
    def health_check(self) -> bool:
        """Check if connection is healthy"""
        try:
            self._client.admin.command('ping')
            return True
        except Exception:
            return False
    
    def get_stats(self) -> dict:
        """Get database statistics"""
        try:
            return {
                "connected": self.health_check(),
                "database": self.settings.database,
                "collections": self.database.list_collection_names(),
                "host": self.settings.host,
                "port": self.settings.port
            }
        except Exception as e:
            return {"connected": False, "error": str(e)}

# Singleton instance
mongodb_connection = MongoDBConnection()