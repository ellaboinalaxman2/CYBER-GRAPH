from typing import Optional, Dict, Any
from neo4j import GraphDatabase, Driver, Session, AsyncSession
from neo4j.exceptions import Neo4jError, ServiceUnavailable
import logging
from .settings import Neo4jSettings

logger = logging.getLogger(__name__)

class Neo4jConnection:
    """Neo4j connection manager with singleton pattern"""
    
    _instance = None
    _driver: Optional[Driver] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.settings = Neo4jSettings()
        self._connect()
    
    def _connect(self):
        """Establish connection to Neo4j"""
        try:
            self._driver = GraphDatabase.driver(
                self.settings.connection_url,
                auth=(self.settings.username, self.settings.password),
                max_connection_pool_size=self.settings.max_connection_pool_size,
                connection_timeout=self.settings.connection_timeout,
                max_transaction_retry_time=self.settings.max_transaction_retry_time
            )
            # Test connection
            with self._driver.session(database=self.settings.database) as session:
                result = session.run("RETURN 1 as test")
                result.single()
            logger.info(f"Connected to Neo4j at {self.settings.host}:{self.settings.port}")
        except (ServiceUnavailable, Neo4jError) as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    
    @property
    def driver(self) -> Driver:
        """Get Neo4j driver"""
        if self._driver is None:
            self._connect()
        return self._driver
    
    def get_session(self) -> Session:
        """Get a session for database operations"""
        return self.driver.session(database=self.settings.database)
    
    def get_async_session(self) -> AsyncSession:
        """Get an async session for database operations"""
        return self.driver.session(database=self.settings.database, default_access_mode="WRITE")
    
    def close(self):
        """Close the driver connection"""
        if self._driver:
            self._driver.close()
            self._driver = None
            logger.info("Neo4j connection closed")
    
    def health_check(self) -> bool:
        """Check if connection is healthy"""
        try:
            with self.get_session() as session:
                session.run("RETURN 1")
            return True
        except Exception:
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with self.get_session() as session:
                # Get node count
                node_count = session.run("MATCH (n) RETURN COUNT(n) as count").single()["count"]
                # Get relationship count
                rel_count = session.run("MATCH ()-[r]->() RETURN COUNT(r) as count").single()["count"]
                # Get database version
                version = session.run("CALL dbms.components() YIELD versions RETURN versions[0] as version").single()["version"]
                
            return {
                "connected": self.health_check(),
                "version": version,
                "database": self.settings.database,
                "nodes": node_count,
                "relationships": rel_count,
                "host": self.settings.host,
                "port": self.settings.port
            }
        except Exception as e:
            return {"connected": False, "error": str(e)}

# Singleton instance
neo4j_connection = Neo4jConnection()