"""Stream processor for real-time event processing."""

from typing import Dict, Any, Optional, Callable, Generator
from queue import Queue, Empty
import threading
import time

from src.pipeline.context import PipelineContext
from src.pipeline.event_processor import EventProcessor
from src.core.logging import get_logger


class StreamProcessor:
    """
    Processes events in real-time as they arrive.
    
    Supports:
    - Event streaming
    - Async processing
    - Callback registration
    - Error handling
    """
    
    def __init__(self, buffer_size: int = 1000):
        """
        Initialize the stream processor.
        
        Args:
            buffer_size: Size of the event buffer
        """
        self.logger = get_logger("pipeline.stream")
        self.buffer_size = buffer_size
        self.event_queue = Queue(maxsize=buffer_size)
        self.event_processor = EventProcessor()
        
        self._is_running = False
        self._thread = None
        
        # Callbacks
        self._on_success_callbacks = []
        self._on_failure_callbacks = []
        self._on_event_callbacks = []
    
    def start(self) -> None:
        """Start the stream processor."""
        if self._is_running:
            self.logger.warning("Stream processor is already running")
            return
        
        self._is_running = True
        self._thread = threading.Thread(target=self._process_loop, daemon=True)
        self._thread.start()
        self.logger.info("Stream processor started")
    
    def stop(self) -> None:
        """Stop the stream processor."""
        self._is_running = False
        if self._thread:
            self._thread.join(timeout=5.0)
        self.logger.info("Stream processor stopped")
    
    def submit(self, event: Dict[str, Any]) -> None:
        """
        Submit an event for processing.
        
        Args:
            event: Event to process
        """
        try:
            self.event_queue.put(event, timeout=1.0)
            self.logger.debug(f"Event submitted to queue (queue size: {self.event_queue.qsize()})")
        except Exception as e:
            self.logger.error(f"Failed to submit event: {e}")
    
    def submit_batch(self, events: list) -> None:
        """
        Submit multiple events for processing.
        
        Args:
            events: List of events to process
        """
        for event in events:
            self.submit(event)
    
    def _process_loop(self) -> None:
        """Main processing loop."""
        self.logger.info("Stream processor loop started")
        
        while self._is_running:
            try:
                # Get event from queue with timeout
                event = self.event_queue.get(timeout=1.0)
                
                # Process the event
                context = self.event_processor.process(event)
                
                # Call callbacks
                self._trigger_callbacks(context)
                
            except Empty:
                # Queue is empty, continue
                continue
            except Exception as e:
                self.logger.error(f"Stream processing error: {e}")
    
    def _trigger_callbacks(self, context: PipelineContext) -> None:
        """Trigger registered callbacks."""
        # On event callbacks
        for callback in self._on_event_callbacks:
            try:
                callback(context)
            except Exception as e:
                self.logger.error(f"Event callback error: {e}")
        
        # Success/Failure callbacks
        if context.is_successful:
            for callback in self._on_success_callbacks:
                try:
                    callback(context)
                except Exception as e:
                    self.logger.error(f"Success callback error: {e}")
        else:
            for callback in self._on_failure_callbacks:
                try:
                    callback(context)
                except Exception as e:
                    self.logger.error(f"Failure callback error: {e}")
    
    def on_success(self, callback: Callable[[PipelineContext], None]) -> None:
        """Register a callback for successful events."""
        self._on_success_callbacks.append(callback)
    
    def on_failure(self, callback: Callable[[PipelineContext], None]) -> None:
        """Register a callback for failed events."""
        self._on_failure_callbacks.append(callback)
    
    def on_event(self, callback: Callable[[PipelineContext], None]) -> None:
        """Register a callback for all events."""
        self._on_event_callbacks.append(callback)
    
    @property
    def is_running(self) -> bool:
        """Check if the stream processor is running."""
        return self._is_running
    
    @property
    def queue_size(self) -> int:
        """Get the current queue size."""
        return self.event_queue.qsize()