import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Neo4jSettings:
    """Neo4j configuration settings"""
    
    # Connection settings
    host: str = os.getenv("NEO4J_HOST", "localhost")
    port: int = int(os.getenv("NEO4J_PORT", "7687"))
    username: str = os.getenv("NEO4J_USERNAME", "neo4j")
    password: str = os.getenv("NEO4J_PASSWORD", "password")
    database: str = os.getenv("NEO4J_DATABASE", "neo4j")
    
    # Connection pool settings
    max_connection_pool_size: int = int(os.getenv("NEO4J_MAX_POOL_SIZE", "50"))
    connection_timeout: int = int(os.getenv("NEO4J_CONNECTION_TIMEOUT", "30"))
    max_transaction_retry_time: int = int(os.getenv("NEO4J_MAX_RETRY_TIME", "30"))
    
    @property
    def connection_url(self) -> str:
        """Build Neo4j connection URL"""
        return f"bolt://{self.host}:{self.port}"