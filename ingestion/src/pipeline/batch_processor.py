"""Batch processor for handling multiple events."""

from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from src.pipeline.context import PipelineContext
from src.pipeline.event_processor import EventProcessor
from src.core.logging import get_logger


class BatchProcessor:
    """
    Processes batches of events through the pipeline.
    
    Supports:
    - Sequential processing
    - Parallel processing (with thread pool)
    - Batch statistics
    - Failed event handling
    """
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize the batch processor.
        
        Args:
            max_workers: Maximum number of parallel workers
        """
        self.logger = get_logger("pipeline.batch")
        self.max_workers = max_workers
        self.event_processor = EventProcessor()
    
    def process_batch(
        self,
        events: List[Dict[str, Any]],
        parallel: bool = False,
    ) -> List[PipelineContext]:
        """
        Process a batch of events.
        
        Args:
            events: List of events to process
            parallel: Whether to process in parallel
            
        Returns:
            List[PipelineContext]: Processing results
        """
        if parallel:
            return self._process_parallel(events)
        else:
            return self._process_sequential(events)
    
    def _process_sequential(self, events: List[Dict[str, Any]]) -> List[PipelineContext]:
        """Process events sequentially."""
        results = []
        
        for i, event in enumerate(events):
            self.logger.debug(f"Processing event {i+1}/{len(events)}")
            context = self.event_processor.process(event)
            results.append(context)
        
        return results
    
    def _process_parallel(self, events: List[Dict[str, Any]]) -> List[PipelineContext]:
        """Process events in parallel."""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.event_processor.process, event): i
                for i, event in enumerate(events)
            }
            
            for future in as_completed(futures):
                try:
                    context = future.result()
                    results.append(context)
                except Exception as e:
                    self.logger.error(f"Parallel processing error: {e}")
        
        return results
    
    def get_batch_stats(self, contexts: List[PipelineContext]) -> Dict[str, Any]:
        """
        Get statistics for a batch of results.
        
        Args:
            contexts: List of pipeline contexts
            
        Returns:
            Dict[str, Any]: Batch statistics
        """
        total = len(contexts)
        successful = sum(1 for c in contexts if c.is_successful)
        failed = total - successful
        
        total_errors = sum(len(c.errors) for c in contexts)
        total_warnings = sum(len(c.warnings) for c in contexts)
        
        avg_time = sum(c.processing_time_ms for c in contexts) / total if total > 0 else 0
        
        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "avg_processing_time_ms": avg_time,
            "total_processing_time_ms": sum(c.processing_time_ms for c in contexts),
        }