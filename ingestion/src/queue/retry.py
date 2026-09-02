"""Retry logic for failed messages."""

import json
import time
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from functools import wraps

from src.queue.redis_client import RedisClient
from src.core.logging import get_logger


class RetryHandler:
    """
    Handles retry logic for failed messages.
    
    Supports:
    - Exponential backoff
    - Max retry limits
    - Different retry strategies
    """
    
    def __init__(self, max_retries: int = 3, backoff_base: int = 2):
        """
        Initialize the retry handler.
        
        Args:
            max_retries: Maximum number of retry attempts
            backoff_base: Base for exponential backoff
        """
        self.logger = get_logger("queue.retry")
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.redis = RedisClient()
    
    def should_retry(self, error: Exception, retry_count: int) -> bool:
        """
        Check if a message should be retried.
        
        Args:
            error: The error that occurred
            retry_count: Current retry count
            
        Returns:
            bool: True if should retry
        """
        # Don't retry if max retries exceeded
        if retry_count >= self.max_retries:
            return False
        
        # Don't retry certain errors
        non_retryable = [
            "ValidationError",
            "SchemaError",
            "ParserError",
        ]
        
        error_class = error.__class__.__name__
        if any(ec in error_class for ec in non_retryable):
            return False
        
        return True
    
    def get_delay(self, retry_count: int) -> int:
        """
        Calculate delay for retry using exponential backoff.
        
        Args:
            retry_count: Current retry count
            
        Returns:
            int: Delay in seconds
        """
        return min(self.backoff_base ** retry_count, 300)  # Max 5 minutes
    
    def handle_failure(
        self,
        message: Dict[str, Any],
        error: Exception,
        retry_count: int,
        queue_name: str,
    ) -> None:
        """
        Handle a failed message.
        
        Args:
            message: The failed message
            error: The error that occurred
            retry_count: Current retry count
            queue_name: Name of the queue
        """
        from src.queue.dead_letter import DeadLetterQueue
        
        if self.should_retry(error, retry_count):
            # Requeue with delay
            delay = self.get_delay(retry_count)
            self._requeue_with_delay(message, queue_name, delay)
            self.logger.info(f"Requeued message with {delay}s delay (retry {retry_count + 1}/{self.max_retries})")
        else:
            # Send to dead letter queue
            dlq = DeadLetterQueue()
            dlq.add(
                message=message,
                error=str(error),
                retry_count=retry_count,
                source_queue=queue_name,
            )
            self.logger.error(f"Message sent to dead letter queue: {error}")
    
    def _requeue_with_delay(self, message: Dict[str, Any], queue_name: str, delay: int) -> None:
        """
        Requeue a message with delay.
        
        Args:
            message: The message to requeue
            queue_name: Name of the queue
            delay: Delay in seconds
        """
        try:
            # Add retry metadata
            message['_retry'] = {
                'timestamp': datetime.utcnow().isoformat() + "Z",
                'delay': delay,
                'queue': queue_name,
            }
            
            data = json.dumps(message, default=str)
            
            # Use Redis sorted set for delayed queue
            scheduled_time = time.time() + delay
            self.redis.execute('zadd', f"{queue_name}:delayed", {data: scheduled_time})
            
        except Exception as e:
            self.logger.error(f"Failed to requeue message: {e}")
    
    def process_delayed(self, queue_name: str, processor: Callable) -> None:
        """
        Process delayed messages.
        
        Args:
            queue_name: Name of the queue
            processor: Function to process messages
        """
        delayed_key = f"{queue_name}:delayed"
        
        try:
            # Get messages that are ready
            now = time.time()
            messages = self.redis.execute(
                'zrangebyscore', delayed_key, 0, now, 'limit', 0, 100
            )
            
            for message_data in messages:
                # Remove from delayed set
                removed = self.redis.execute('zrem', delayed_key, message_data)
                if not removed:
                    continue
                
                # Process the message
                try:
                    message = json.loads(message_data)
                    processor(message)
                except Exception as e:
                    self.logger.error(f"Failed to process delayed message: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error processing delayed messages: {e}")
    
    @staticmethod
    def retry_on_failure(
        max_retries: int = 3,
        backoff_base: int = 2,
        retryable_exceptions: tuple = (Exception,),
    ):
        """
        Decorator to retry a function on failure.
        
        Args:
            max_retries: Maximum number of retries
            backoff_base: Base for exponential backoff
            retryable_exceptions: Exceptions to retry on
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except retryable_exceptions as e:
                        last_exception = e
                        if attempt < max_retries:
                            delay = min(backoff_base ** attempt, 60)
                            time.sleep(delay)
                            continue
                        raise
                
                if last_exception:
                    raise last_exception
            
            return wrapper
        return decorator