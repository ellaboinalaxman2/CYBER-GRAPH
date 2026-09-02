"""Event processing worker."""

from typing import Dict, Any, Optional

from src.workers.base_worker import BaseWorker
from src.pipeline import Pipeline
from src.core.logging import get_logger


class EventWorker(BaseWorker):
    """
    Worker that processes events through the pipeline.
    
    Handles:
    - Event processing
    - Pipeline execution
    - Error handling
    - Result tracking
    """
    
    def __init__(self, name: Optional[str] = None):
        """
        Initialize the event worker.
        
        Args:
            name: Worker name
        """
        super().__init__(name=name or "event-worker")
        self.pipeline = Pipeline()
        self.logger = get_logger("worker.event")
    
    def process(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an event through the pipeline.
        
        Args:
            message: Event message to process
            
        Returns:
            Dict[str, Any]: Processing result
        """
        self.logger.info(f"Processing event: {message.get('event_id', 'unknown')}")
        
        # Extract event from message
        event = message.get('event', message)
        
        # Run through pipeline
        context = self.pipeline.process_event(event)
        
        if not context.is_successful:
            raise Exception(f"Pipeline failed: {context.errors}")
        
        return {
            "status": "success",
            "event_id": event.get('event_id', 'unknown'),
            "run_id": context.run_id,
            "processing_time_ms": context.processing_time_ms,
            "stage_count": len(context.stage_results),
        }