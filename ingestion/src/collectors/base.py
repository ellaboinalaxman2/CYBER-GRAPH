"""Base collector interface for all data sources."""

from abc import ABC, abstractmethod
from typing import Optional, Generator, List, Dict, Any
from datetime import datetime
import uuid

from src.core.logging import get_logger
from src.core.exceptions import CollectorError
from src.models.raw_event import RawEvent, RawSourceType


class BaseCollector(ABC):
    """
    Abstract base class for all collectors.
    
    Collectors are responsible ONLY for getting raw security data.
    They DO NOT parse, normalize, or enrich - just collect.
    
    Each collector implements:
    - connect(): Establish connection to the data source
    - disconnect(): Close the connection
    - collect_one(): Get a single event
    - collect_batch(): Get multiple events
    - collect_stream(): Stream events (generator)
    """
    
    def __init__(
        self,
        source_type: RawSourceType,
        source_name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the collector.
        
        Args:
            source_type: Type of source (syslog, windows, etc.)
            source_name: Name/ID of the source for logging
            config: Optional configuration dictionary
        """
        self.source_type = source_type
        self.source_name = source_name or f"{source_type}-collector"
        self.config = config or {}
        self.logger = get_logger(f"collector.{self.source_name}")
        self._is_connected = False
        self._stats = {
            "events_collected": 0,
            "events_failed": 0,
            "connection_attempts": 0,
            "last_collect_time": None,
        }
        
    @abstractmethod
    def connect(self) -> bool:
        """
        Establish connection to the data source.
        
        Returns:
            bool: True if connection successful, False otherwise.
            
        Raises:
            CollectorError: If connection fails critically.
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close connection to the data source."""
        pass
    
    @abstractmethod
    def collect_one(self) -> Optional[RawEvent]:
        """
        Collect a single raw event.
        
        Returns:
            RawEvent: If an event was collected.
            None: If no events available or timeout.
            
        Raises:
            CollectorError: If collection fails critically.
        """
        pass
    
    @abstractmethod
    def collect_batch(self, batch_size: int = 100) -> List[RawEvent]:
        """
        Collect a batch of raw events.
        
        Args:
            batch_size: Maximum number of events to collect.
            
        Returns:
            List[RawEvent]: List of collected events (may be empty).
            
        Raises:
            CollectorError: If collection fails critically.
        """
        pass
    
    def collect_stream(self) -> Generator[RawEvent, None, None]:
        """
        Stream events as they arrive (infinite generator).
        
        Yields:
            RawEvent: Events as they are collected.
        """
        while self._is_connected:
            try:
                event = self.collect_one()
                if event:
                    yield event
            except CollectorError as e:
                self.logger.error(f"Stream collection error: {e}")
                break
            except Exception as e:
                self.logger.error(f"Unexpected stream error: {e}")
                break
    
    @property
    def is_connected(self) -> bool:
        """Check if collector is connected."""
        return self._is_connected
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        return self._stats.copy()
    
    def _generate_event_id(self) -> str:
        """Generate a unique event ID."""
        return f"RAW-{uuid.uuid4().hex[:12].upper()}"
    
    def _create_raw_event(
        self,
        raw_content: str,
        source_host: Optional[str] = None,
        original_timestamp: Optional[str] = None,
        raw_json: Optional[Dict[str, Any]] = None,
        collection_metadata: Optional[Dict[str, Any]] = None,
    ) -> RawEvent:
        """
        Helper to create a RawEvent with standard fields.
        
        Args:
            raw_content: The raw log content
            source_host: Host that sent the event
            original_timestamp: Original timestamp string
            raw_json: Optional JSON structure
            collection_metadata: Additional metadata
            
        Returns:
            RawEvent: The created event.
        """
        return RawEvent(
            raw_source=self.source_type,
            raw_content=raw_content,
            raw_json=raw_json,
            source_host=source_host or self.source_name,
            original_timestamp=original_timestamp,
            collected_at=datetime.utcnow(),
            collection_metadata=collection_metadata or {},
        )
    
    def _update_stats(self, success: bool = True) -> None:
        """Update collection statistics."""
        if success:
            self._stats["events_collected"] += 1
        else:
            self._stats["events_failed"] += 1
        self._stats["last_collect_time"] = datetime.utcnow()
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()