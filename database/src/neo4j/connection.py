"""Neo4j connection management."""

from typing import Optional, Dict, Any, List
from neo4j import GraphDatabase, Driver, Session
from neo4j.exceptions import ServiceUnavailable, AuthError

from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import Neo4jError


class Neo4jConnection:
    """
    Neo4j connection manager with connection pooling.
    
    Features:
    - Connection pooling
    - Health checks
    - Session management
    - Query execution
    """
    
    _instance = None
    _driver = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the Neo4j connection."""
        if not hasattr(self, '_initialized'):
            self.logger = get_logger("neo4j.connection")
            self._initialized = True
            self._connected = False
            self._connect()
    
    def _connect(self) -> None:
        """Establish connection to Neo4j."""
        try:
            # Check if Neo4j settings are available
            if not hasattr(settings, 'neo4j_uri'):
                self.logger.warning("Neo4j settings not configured, skipping connection")
                self._connected = False
                return
            
            self._driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
                max_connection_pool_size=50,
                connection_acquisition_timeout=30,
                connection_timeout=30,
            )
            
            # Test connection
            with self._driver.session() as session:
                result = session.run("RETURN 1 as test")
                result.single()
            
            self._connected = True
            self.logger.info(f"Connected to Neo4j: {settings.neo4j_uri}")
            
        except (ServiceUnavailable, AuthError) as e:
            self._connected = False
            self.logger.warning(f"Failed to connect to Neo4j: {e}")
            # Don't raise exception, just log warning
        except Exception as e:
            self._connected = False
            self.logger.warning(f"Unexpected Neo4j error: {e}")
            # Don't raise exception, just log warning
    
    def get_driver(self) -> Optional[Driver]:
        """Get the Neo4j driver."""
        if not self._connected or self._driver is None:
            self._connect()
        return self._driver
    
    def get_session(self) -> Optional[Session]:
        """Get a Neo4j session."""
        driver = self.get_driver()
        if driver:
            return driver.session()
        return None
    
    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query.
        
        Args:
            query: Cypher query
            parameters: Query parameters
            
        Returns:
            List[Dict[str, Any]]: Query results
        """
        if not self._connected:
            self.logger.warning("Neo4j not connected, returning empty results")
            return []
        
        results = []
        try:
            with self.get_session() as session:
                if session:
                    result = session.run(query, parameters or {})
                    for record in result:
                        results.append(record.data())
            return results
        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            return []
    
    def execute_transaction(self, queries: List[tuple]) -> List[Dict[str, Any]]:
        """
        Execute multiple queries in a transaction.
        
        Args:
            queries: List of (query, parameters) tuples
            
        Returns:
            List[Dict[str, Any]]: Query results
        """
        if not self._connected:
            self.logger.warning("Neo4j not connected, returning empty results")
            return []
        
        results = []
        try:
            with self.get_session() as session:
                if session:
                    with session.begin_transaction() as tx:
                        for query, params in queries:
                            result = tx.run(query, params or {})
                            for record in result:
                                results.append(record.data())
                        tx.commit()
            return results
        except Exception as e:
            self.logger.error(f"Transaction execution failed: {e}")
            return []
    
    def is_connected(self) -> bool:
        """Check if connected to Neo4j."""
        if not self._connected or self._driver is None:
            return False
        
        try:
            with self._driver.session() as session:
                session.run("RETURN 1")
            return True
        except Exception:
            return False
    
    def close(self) -> None:
        """Close the Neo4j connection."""
        if self._driver:
            try:
                self._driver.close()
                self._connected = False
                self.logger.info("Neo4j connection closed")
            except Exception as e:
                self.logger.error(f"Error closing Neo4j connection: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check.
        
        Returns:
            Dict[str, Any]: Health status
        """
        if not self._connected:
            return {
                "status": "unavailable",
                "error": "Neo4j not connected",
            }
        
        try:
            if self.is_connected():
                # Get some stats
                result = self.execute_query(
                    "MATCH (n) RETURN count(n) as node_count LIMIT 1"
                )
                stats = result[0] if result else {"node_count": 0}
                
                return {
                    "status": "healthy",
                    "uri": settings.neo4j_uri if hasattr(settings, 'neo4j_uri') else "not configured",
                    "node_count": stats.get("node_count", 0),
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
neo4j = Neo4jConnection()