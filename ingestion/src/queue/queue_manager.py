"""Queue manager for managing multiple queues."""

import json
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import threading
import time

from src.queue.redis_client import RedisClient
from src.queue.dead_letter import DeadLetterQueue
from src.queue.retry import RetryHandler
from src.core.logging import get_logger


class QueueManager:
    """
    Manages multiple queues with reliability features.
    
    Features:
    - Multiple queue management
    - Producer/consumer patterns
    - Dead letter queue
    - Retry logic
    - Monitoring
    """
    
    def __init__(self):
        """Initialize the queue manager."""
        self.logger = get_logger("queue.manager")
        self.redis = RedisClient()
        self.dead_letter = DeadLetterQueue()
        self.retry_handler = RetryHandler()
        
        self._queues: Dict[str, Dict[str, Any]] = {}
        self._consumers: Dict[str, threading.Thread] = {}
        self._is_running = False
        self._stats = {
            "messages_produced": 0,
            "messages_consumed": 0,
            "messages_failed": 0,
            "messages_retried": 0,
            "messages_dead": 0,
        }
    
    def create_queue(
        self,
        name: str,
        max_retries: int = 3,
        batch_size: int = 10,
        consumer_count: int = 1,
    ) -> None:
        """
        Create a new queue.
        
        Args:
            name: Queue name
            max_retries: Maximum retry attempts
            batch_size: Batch size for consumption
            consumer_count: Number of consumers
        """
        self._queues[name] = {
            "name": name,
            "max_retries": max_retries,
            "batch_size": batch_size,
            "consumer_count": consumer_count,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "active": True,
        }
        self.logger.info(f"Created queue: {name}")
    
    def produce(self, queue_name: str, message: Dict[str, Any]) -> bool:
        """
        Produce a message to a queue.
        
        Args:
            queue_name: Name of the queue
            message: Message to produce
            
        Returns:
            bool: True if successful
        """
        if queue_name not in self._queues:
            self.logger.error(f"Queue not found: {queue_name}")
            return False
        
        try:
            # Add metadata
            message['_queue'] = {
                'queue_name': queue_name,
                'produced_at': datetime.utcnow().isoformat() + "Z",
                'message_id': f"MSG-{datetime.utcnow().timestamp()}-{hash(str(message))}",
            }
            
            data = json.dumps(message, default=str)
            result = self.redis.execute('rpush', queue_name, data)
            
            if result:
                self._stats["messages_produced"] += 1
                self.logger.debug(f"Produced message to {queue_name}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to produce message: {e}")
            return False
    
    def consume(self, queue_name: str, callback: Callable) -> bool:
        """
        Consume messages from a queue.
        
        Args:
            queue_name: Name of the queue
            callback: Function to process messages
            
        Returns:
            bool: True if successful
        """
        if queue_name not in self._queues:
            self.logger.error(f"Queue not found: {queue_name}")
            return False
        
        queue_config = self._queues[queue_name]
        
        # Start consumer threads
        for i in range(queue_config["consumer_count"]):
            thread = threading.Thread(
                target=self._consume_loop,
                args=(queue_name, callback, queue_config["max_retries"]),
                daemon=True,
                name=f"consumer-{queue_name}-{i}",
            )
            thread.start()
            self._consumers[f"{queue_name}-{i}"] = thread
        
        self.logger.info(f"Started {queue_config['consumer_count']} consumers for {queue_name}")
        return True
    
    def _consume_loop(self, queue_name: str, callback: Callable, max_retries: int) -> None:
        """
        Main consumer loop.
        
        Args:
            queue_name: Name of the queue
            callback: Function to process messages
            max_retries: Maximum retry attempts
        """
        self.logger.info(f"Consumer started for {queue_name}")
        
        while self._is_running:
            try:
                # Pop message from queue
                data = self.redis.execute('lpop', queue_name)
                
                if data:
                    try:
                        message = json.loads(data)
                        retry_count = message.get('_retry_count', 0)
                        
                        # Process message
                        try:
                            callback(message)
                            self._stats["messages_consumed"] += 1
                            
                        except Exception as e:
                            self._stats["messages_failed"] += 1
                            self.logger.error(f"Callback failed: {e}")
                            
                            # Handle retry
                            if retry_count < max_retries:
                                message['_retry_count'] = retry_count + 1
                                self.retry_handler.handle_failure(
                                    message, e, retry_count, queue_name
                                )
                                self._stats["messages_retried"] += 1
                            else:
                                # Send to dead letter queue
                                self.dead_letter.add(
                                    message=message,
                                    error=str(e),
                                    retry_count=retry_count,
                                    source_queue=queue_name,
                                )
                                self._stats["messages_dead"] += 1
                    
                    except json.JSONDecodeError as e:
                        self.logger.error(f"Failed to decode message: {e}")
                
                else:
                    # No messages, process delayed messages
                    self.retry_handler.process_delayed(queue_name, callback)
                    
                    # Small sleep to prevent CPU spinning
                    time.sleep(0.1)
                    
            except Exception as e:
                self.logger.error(f"Consumer loop error: {e}")
                time.sleep(1.0)
    
    def get_queue_stats(self, queue_name: str) -> Dict[str, Any]:
        """
        Get statistics for a queue.
        
        Args:
            queue_name: Name of the queue
            
        Returns:
            Dict[str, Any]: Queue statistics
        """
        if queue_name not in self._queues:
            return {}
        
        try:
            size = self.redis.execute('llen', queue_name)
            delayed = self.redis.execute('zcard', f"{queue_name}:delayed")
        except Exception:
            size = 0
            delayed = 0
        
        return {
            "name": queue_name,
            "size": size,
            "delayed": delayed,
            "config": self._queues[queue_name],
            "total_messages": {
                "produced": self._stats["messages_produced"],
                "consumed": self._stats["messages_consumed"],
                "failed": self._stats["messages_failed"],
                "retried": self._stats["messages_retried"],
                "dead": self._stats["messages_dead"],
            },
        }
    
    def start(self) -> None:
        """Start the queue manager."""
        if self._is_running:
            return
        
        self._is_running = True
        self.logger.info("Queue manager started")
    
    def stop(self) -> None:
        """Stop the queue manager."""
        self._is_running = False
        
        # Wait for consumers to finish
        for name, thread in self._consumers.items():
            thread.join(timeout=5.0)
            self.logger.info(f"Stopped consumer: {name}")
        
        self._consumers.clear()
        self.logger.info("Queue manager stopped")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get queue manager statistics.
        
        Returns:
            Dict[str, Any]: Statistics
        """
        return {
            **self._stats,
            "queues": list(self._queues.keys()),
            "active_consumers": len(self._consumers),
            "is_running": self._is_running,
            "dead_letter_count": self.dead_letter.get_count(),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }