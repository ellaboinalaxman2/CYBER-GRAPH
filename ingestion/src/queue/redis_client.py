"""Redis connection manager."""

import redis
from typing import Optional, Dict, Any
from datetime import datetime
import json

from src.core.logging import get_logger
from src.core.config import settings


class RedisClient:
    """
    Redis connection manager with connection pooling.
    
    Handles:
    - Connection management
    - Connection pooling
    - Health checks
    - Reconnection
    """
    
    _instance = None
    _connection = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the Redis client."""
        if not hasattr(self, '_initialized'):
            self.logger = get_logger("queue.redis")
            self._initialized = True
            self._config = {
                "host": getattr(settings, 'redis_host', 'localhost'),
                "port": getattr(settings, 'redis_port', 6379),
                "db": getattr(settings, 'redis_db', 0),
                "password": getattr(settings, 'redis_password', None),
                "decode_responses": True,
                "socket_keepalive": True,
                "socket_timeout": 5,
                "retry_on_timeout": True,
            }
            self._connect()
    
    def _connect(self) -> None:
        """Establish connection to Redis."""
        try:
            self._connection = redis.Redis(**self._config)
            # Test connection
            self._connection.ping()
            self.logger.info(
                f"Connected to Redis at {self._config['host']}:{self._config['port']}"
            )
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            self._connection = None
    
    def get_connection(self) -> Optional[redis.Redis]:
        """
        Get the Redis connection.
        
        Returns:
            Optional[redis.Redis]: Redis connection or None
        """
        if self._connection is None:
            self._connect()
        return self._connection
    
    def ping(self) -> bool:
        """
        Check if Redis is reachable.
        
        Returns:
            bool: True if reachable
        """
        try:
            conn = self.get_connection()
            if conn:
                return conn.ping()
            return False
        except Exception:
            return False
    
    def close(self) -> None:
        """Close the Redis connection."""
        if self._connection:
            try:
                self._connection.close()
                self.logger.info("Redis connection closed")
            except Exception as e:
                self.logger.error(f"Error closing Redis connection: {e}")
            finally:
                self._connection = None
    
    def execute(self, command: str, *args, **kwargs) -> Any:
        """
        Execute a Redis command.
        
        Args:
            command: Redis command name
            *args: Command arguments
            **kwargs: Command keyword arguments
            
        Returns:
            Any: Command result
        """
        conn = self.get_connection()
        if not conn:
            raise Exception("Redis connection not available")
        
        try:
            method = getattr(conn, command)
            return method(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Redis command failed: {command} - {e}")
            raise
    
    def publish(self, channel: str, message: Dict[str, Any]) -> int:
        """
        Publish a message to a channel.
        
        Args:
            channel: Channel name
            message: Message to publish
            
        Returns:
            int: Number of subscribers that received the message
        """
        try:
            data = json.dumps(message, default=str)
            return self.execute('publish', channel, data)
        except Exception as e:
            self.logger.error(f"Failed to publish to {channel}: {e}")
            return 0
    
    def subscribe(self, channel: str, callback) -> None:
        """
        Subscribe to a channel.
        
        Args:
            channel: Channel name
            callback: Callback function for messages
        """
        def _listener():
            conn = self.get_connection()
            if not conn:
                self.logger.error("Cannot subscribe: no Redis connection")
                return
            
            pubsub = conn.pubsub()
            pubsub.subscribe(channel)
            
            for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        callback(data)
                    except Exception as e:
                        self.logger.error(f"Error processing subscription message: {e}")
        
        import threading
        thread = threading.Thread(target=_listener, daemon=True)
        thread.start()
        self.logger.info(f"Subscribed to channel: {channel}")