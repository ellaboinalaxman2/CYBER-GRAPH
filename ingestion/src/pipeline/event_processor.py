"""Event processor for individual events."""

from typing import Dict, Any, Optional, Callable
from datetime import datetime

from src.pipeline.stages import PipelineStage, StageType, StageResult, StageStatus
from src.pipeline.context import PipelineContext
from src.core.logging import get_logger


class EventProcessor:
    """
    Processes individual events through the pipeline.
    
    Handles:
    - Collection
    - Parsing
    - Normalization
    - Validation
    - Enrichment
    - Output
    """
    
    def __init__(self):
        """Initialize the event processor."""
        self.logger = get_logger("pipeline.processor")
        self.stages = []
        self._setup_stages()
    
    def _setup_stages(self) -> None:
        """Set up the pipeline stages."""
        # Stage definitions will be added
        pass
    
    def process(self, event: Dict[str, Any], context: Optional[PipelineContext] = None) -> PipelineContext:
        """
        Process a single event through the pipeline.
        
        Args:
            event: Event data to process
            context: Optional pipeline context
            
        Returns:
            PipelineContext: Processing context with results
        """
        if context is None:
            context = PipelineContext()
        
        context.original_data = event
        context.current_data = event
        context.started_at = datetime.utcnow()
        
        self.logger.info(f"Starting pipeline for event: {context.run_id}")
        
        # Process through each stage
        for stage in self.stages:
            result = stage.execute(context.current_data)
            context.add_stage_result(result.to_dict())
            
            if result.status == StageStatus.COMPLETED and result.data is not None:
                context.current_data = result.data
                context.results[stage.stage_type.value] = result.data
            elif result.status == StageStatus.FAILED and stage.required:
                context.add_error(f"Stage {stage.name} failed: {result.error}")
                break
            elif result.status == StageStatus.FAILED and not stage.required:
                context.add_warning(f"Non-required stage {stage.name} failed: {result.error}")
        
        context.complete()
        
        self.logger.info(
            f"Pipeline completed for event: {context.run_id}",
            extra={
                "success": context.is_successful,
                "duration_ms": context.processing_time_ms,
                "errors": len(context.errors),
            }
        )
        
        return context
    
    def add_stage(self, stage: PipelineStage) -> None:
        """Add a stage to the pipeline."""
        self.stages.append(stage)
        self.logger.info(f"Added stage: {stage.name}")
    
    def remove_stage(self, stage_name: str) -> None:
        """Remove a stage from the pipeline."""
        self.stages = [s for s in self.stages if s.name != stage_name]
        self.logger.info(f"Removed stage: {stage_name}")