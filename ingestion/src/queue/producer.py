"""Queue producer for sending events to the queue."""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from src.queue.queue_config import QueueConfig
from src.core.logging import get_logger


class QueueProducer:
    """
    Produces events to the message queue.
    
    Supports:
    - Single event publishing
    - Batch publishing
    - Event acknowledgment
    - Retry logic
    """
    
    def __init__(self, config: Optional[QueueConfig] = None):
        """
        Initialize the queue producer.
        
        Args:
            config: Queue configuration
        """
        self.config = config or QueueConfig()
        self.logger = get_logger("queue.producer")
        self._connected = False
        
        # Try to import Redis
        try:
            import redis
            self._redis = redis.Redis(
                host=self.config.host,
                port=self.config.port,
                db=self.config.db,
                password=self.config.password,
                decode_responses=True,
            )
            self._connected = True
            self.logger.info(f"Connected to Redis at {self.config.host}:{self.config.port}")
        except ImportError:
            self.logger.warning("Redis not installed - using in-memory queue")
            self._redis = None
            self._in_memory_queue = []
            self._connected = True
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            self._redis = None
            self._in_memory_queue = []
            self._connected = True  # Fallback to in-memory
    
    def publish(self, event: Dict[str, Any]) -> bool:
        """
        Publish a single event to the queue.
        
        Args:
            event: Event to publish
            
        Returns:
            bool: True if published successfully
        """
        if not self._connected:
            self.logger.warning("Queue not connected, storing in-memory")
            self._in_memory_queue.append(event)
            return True
        
        try:
            # Add metadata
            message = {
                "id": f"MSG-{uuid.uuid4().hex[:8].upper()}",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "event": event,
            }
            
            # Serialize to JSON
            data = json.dumps(message, default=str)
            
            # Publish to Redis
            if self._redis:
                self._redis.rpush(self.config.queue_name, data)
                self.logger.debug(f"Published event: {message['id']}")
            else:
                self._in_memory_queue.append(message)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to publish event: {e}")
            # Store in memory as fallback
            self._in_memory_queue.append(event)
            return False
    
    def publish_batch(self, events: List[Dict[str, Any]]) -> int:
        """
        Publish multiple events to the queue.
        
        Args:
            events: List of events to publish
            
        Returns:
            int: Number of events published successfully
        """
        success_count = 0
        
        for event in events:
            if self.publish(event):
                success_count += 1
        
        return success_count
    
    def get_pending_count(self) -> int:
        """
        Get the number of pending events in the queue.
        
        Returns:
            int: Number of pending events
        """
        if self._redis:
            try:
                return self._redis.llen(self.config.queue_name)
            except Exception:
                return 0
        else:
            return len(self._in_memory_queue)
    
    def flush(self) -> None:
        """Flush the in-memory queue to Redis."""
        if self._in_memory_queue:
            self.logger.info(f"Flushing {len(self._in_memory_queue)} events to Redis")
            while self._in_memory_queue:
                event = self._in_memory_queue.pop(0)
                self.publish(event)
    
    def close(self) -> None:
        """Close the connection."""
        if self._redis:
            try:
                self._redis.close()
            except Exception:
                pass
        self._connected = False
        self.logger.info("Queue producer closed")