"""Queue consumer for receiving events from the queue."""

import json
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
import threading
import time

from src.queue.queue_config import QueueConfig
from src.core.logging import get_logger


class QueueConsumer:
    """
    Consumes events from the message queue.
    
    Supports:
    - Event consumption
    - Callback registration
    - Batch processing
    - Error handling
    """
    
    def __init__(
        self,
        config: Optional[QueueConfig] = None,
        callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        """
        Initialize the queue consumer.
        
        Args:
            config: Queue configuration
            callback: Function to process events
        """
        self.config = config or QueueConfig()
        self.callback = callback
        self.logger = get_logger("queue.consumer")
        
        self._connected = False
        self._is_running = False
        self._thread = None
        
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
            self._connected = True
    
    def start(self) -> None:
        """Start consuming events."""
        if self._is_running:
            self.logger.warning("Consumer is already running")
            return
        
        if not self.callback:
            self.logger.error("No callback registered")
            return
        
        self._is_running = True
        self._thread = threading.Thread(target=self._consume_loop, daemon=True)
        self._thread.start()
        self.logger.info("Consumer started")
    
    def stop(self) -> None:
        """Stop consuming events."""
        self._is_running = False
        if self._thread:
            self._thread.join(timeout=5.0)
        self.logger.info("Consumer stopped")
    
    def _consume_loop(self) -> None:
        """Main consumption loop."""
        self.logger.info("Consumer loop started")
        
        while self._is_running:
            try:
                # Get event from queue
                message = self._get_event()
                
                if message:
                    # Process the event
                    try:
                        event = message.get("event", {})
                        self.callback(event)
                    except Exception as e:
                        self.logger.error(f"Callback error: {e}")
                        # Move to dead letter queue
                        self._handle_dead_letter(message)
                else:
                    # No events, sleep
                    time.sleep(0.1)
                    
            except Exception as e:
                self.logger.error(f"Consumer loop error: {e}")
                time.sleep(1.0)
    
    def _get_event(self) -> Optional[Dict[str, Any]]:
        """Get an event from the queue."""
        if self._redis:
            try:
                # Pop from Redis list
                data = self._redis.lpop(self.config.queue_name)
                if data:
                    return json.loads(data)
            except Exception as e:
                self.logger.error(f"Failed to get event from Redis: {e}")
        else:
            # In-memory
            if self._in_memory_queue:
                return self._in_memory_queue.pop(0)
        
        return None
    
    def _handle_dead_letter(self, message: Dict[str, Any]) -> None:
        """Handle a failed message (move to dead letter queue)."""
        try:
            message["dead_letter_time"] = datetime.utcnow().isoformat() + "Z"
            data = json.dumps(message, default=str)
            
            if self._redis:
                self._redis.rpush(self.config.dead_letter_queue, data)
            else:
                self.logger.warning(f"Dead letter: {message}")
                
        except Exception as e:
            self.logger.error(f"Failed to handle dead letter: {e}")
    
    def register_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Register a callback for processing events.
        
        Args:
            callback: Function to process events
        """
        self.callback = callback
        self.logger.info("Callback registered")
    
    @property
    def is_running(self) -> bool:
        """Check if the consumer is running."""
        return self._is_running
    
    @property
    def pending_count(self) -> int:
        """Get the number of pending events."""
        if self._redis:
            try:
                return self._redis.llen(self.config.queue_name)
            except Exception:
                return 0
        else:
            return len(self._in_memory_queue)
    
    def close(self) -> None:
        """Close the connection."""
        self.stop()
        if self._redis:
            try:
                self._redis.close()
            except Exception:
                pass
        self._connected = False
        self.logger.info("Queue consumer closed")