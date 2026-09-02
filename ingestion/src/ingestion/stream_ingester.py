"""Stream ingester for real-time data."""

from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
import threading
import time

from src.ingestion.data_source import DataSource, DataSourceType
from src.collectors import (
    SyslogCollector,
    FirewallCollector,
    WindowsCollector,
    LinuxCollector,
)
from src.pipeline import Pipeline
from src.core.logging import get_logger


class StreamIngester:
    """
    Stream ingester for real-time events.
    
    Supports:
    - Multiple stream sources
    - Real-time processing
    - Collector integration
    - Error handling
    """
    
    def __init__(self):
        """Initialize the stream ingester."""
        self.logger = get_logger("ingestion.stream")
        self.pipeline = Pipeline()
        self.sources: Dict[str, Any] = {}
        self._is_running = False
        self._threads = []
        self._stats = {
            "events_received": 0,
            "events_processed": 0,
            "events_failed": 0,
            "sources_active": 0,
            "last_event": None,
        }
    
    def add_source(self, source: DataSource, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a stream source.
        
        Args:
            source: Data source configuration
            config: Additional configuration
            
        Returns:
            bool: True if added successfully
        """
        if source.type != DataSourceType.STREAM and source.type != DataSourceType.SYSLOG:
            self.logger.warning(f"Source {source.name} is not a stream source")
            return False
        
        try:
            # Create appropriate collector
            collector = self._create_collector(source, config)
            
            if collector:
                self.sources[source.name] = {
                    "source": source,
                    "collector": collector,
                    "config": config or {},
                    "active": False,
                }
                self.logger.info(f"Added stream source: {source.name}")
                return True
            else:
                self.logger.error(f"Failed to create collector for: {source.name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to add stream source {source.name}: {e}")
            return False
    
    def _create_collector(self, source: DataSource, config: Optional[Dict[str, Any]] = None):
        """Create a collector for the source."""
        config = config or {}
        
        if source.format.value == "syslog":
            return SyslogCollector(
                host=source.host or "0.0.0.0",
                port=source.port or 514,
                timeout=config.get("timeout", 5.0),
            )
        
        # Other collectors can be added here
        return None
    
    def start(self) -> None:
        """Start all stream sources."""
        if self._is_running:
            self.logger.warning("Stream ingester is already running")
            return
        
        self._is_running = True
        
        for name, source_data in self.sources.items():
            if not source_data["active"]:
                thread = threading.Thread(
                    target=self._consume_stream,
                    args=(name, source_data),
                    daemon=True,
                )
                thread.start()
                self._threads.append(thread)
                source_data["active"] = True
                self._stats["sources_active"] += 1
                self.logger.info(f"Started stream source: {name}")
    
    def stop(self) -> None:
        """Stop all stream sources."""
        self._is_running = False
        
        # Disconnect collectors
        for name, source_data in self.sources.items():
            if source_data["active"]:
                try:
                    source_data["collector"].disconnect()
                    source_data["active"] = False
                    self._stats["sources_active"] -= 1
                    self.logger.info(f"Stopped stream source: {name}")
                except Exception as e:
                    self.logger.error(f"Failed to stop {name}: {e}")
        
        # Wait for threads
        for thread in self._threads:
            thread.join(timeout=2.0)
        
        self._threads.clear()
        self.logger.info("Stream ingester stopped")
    
    def _consume_stream(self, name: str, source_data: Dict[str, Any]) -> None:
        """
        Consume events from a stream.
        
        Args:
            name: Source name
            source_data: Source data
        """
        collector = source_data["collector"]
        
        try:
            collector.connect()
            self.logger.info(f"Connected to stream: {name}")
            
            while self._is_running and source_data["active"]:
                try:
                    # Collect one event
                    raw_event = collector.collect_one()
                    
                    if raw_event:
                        # Process through pipeline
                        self._stats["events_received"] += 1
                        event_data = raw_event.dict()
                        
                        # Process the event
                        context = self.pipeline.process_event(event_data)
                        
                        if context.is_successful:
                            self._stats["events_processed"] += 1
                        else:
                            self._stats["events_failed"] += 1
                        
                        self._stats["last_event"] = datetime.utcnow()
                
                except Exception as e:
                    self.logger.error(f"Error consuming stream {name}: {e}")
                    time.sleep(1.0)
        
        except Exception as e:
            self.logger.error(f"Failed to connect to stream {name}: {e}")
            source_data["active"] = False
            self._stats["sources_active"] -= 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get stream ingestion statistics."""
        return {
            **self._stats,
            "sources": len(self.sources),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    
    @property
    def is_running(self) -> bool:
        """Check if the stream ingester is running."""
        return self._is_running