import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class MongoSettings:
    """MongoDB configuration settings"""
    
    # Connection settings
    host: str = os.getenv("MONGODB_HOST", "localhost")
    port: int = int(os.getenv("MONGODB_PORT", "27017"))
    username: Optional[str] = os.getenv("MONGODB_USERNAME")
    password: Optional[str] = os.getenv("MONGODB_PASSWORD")
    database: str = os.getenv("MONGODB_DATABASE", "cyber_graph")
    
    # Connection pool settings
    max_pool_size: int = int(os.getenv("MONGODB_MAX_POOL_SIZE", "100"))
    min_pool_size: int = int(os.getenv("MONGODB_MIN_POOL_SIZE", "10"))
    max_idle_time_ms: int = int(os.getenv("MONGODB_MAX_IDLE_TIME_MS", "30000"))
    connect_timeout_ms: int = int(os.getenv("MONGODB_CONNECT_TIMEOUT_MS", "10000"))
    socket_timeout_ms: int = int(os.getenv("MONGODB_SOCKET_TIMEOUT_MS", "30000"))
    
    # Collection names
    USERS_COLLECTION: str = "users"
    EVENTS_COLLECTION: str = "events"
    ALERTS_COLLECTION: str = "alerts"
    INCIDENTS_COLLECTION: str = "incidents"
    AUDIT_LOGS_COLLECTION: str = "audit_logs"
    
    @property
    def connection_string(self) -> str:
        """Build MongoDB connection string"""
        if self.username and self.password:
            return f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"mongodb://{self.host}:{self.port}"
    
    def get_database_url(self) -> str:
        """Get full database URL with database name"""
        return f"{self.connection_string}/{self.database}"