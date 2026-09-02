"""Queue configuration."""

from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class QueueConfig:
    """Configuration for message queue."""
    
    # Redis configuration
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    
    # Queue settings
    queue_name: str = "ingestion_events"
    dead_letter_queue: str = "ingestion_events_dead"
    max_retries: int = 3
    retry_delay: int = 60  # seconds
    
    # Performance
    batch_size: int = 100
    flush_interval: int = 5  # seconds
    consumer_count: int = 4
    
    # Timeouts
    connection_timeout: int = 5  # seconds
    socket_timeout: int = 5  # seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "host": self.host,
            "port": self.port,
            "db": self.db,
            "queue_name": self.queue_name,
            "dead_letter_queue": self.dead_letter_queue,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "batch_size": self.batch_size,
            "consumer_count": self.consumer_count,
        }