"""Complete pipeline orchestrator."""

from typing import Dict, Any, Optional, List, Callable
from datetime import datetime

from src.pipeline.stages import PipelineStage, StageType
from src.pipeline.context import PipelineContext
from src.pipeline.event_processor import EventProcessor
from src.pipeline.batch_processor import BatchProcessor
from src.pipeline.stream_processor import StreamProcessor
from src.core.logging import get_logger


class Pipeline:
    """
    Complete pipeline orchestrator.
    
    Integrates all components:
    - Event processing
    - Batch processing
    - Stream processing
    - Pipeline configuration
    """
    
    def __init__(self):
        """Initialize the pipeline."""
        self.logger = get_logger("pipeline.main")
        self.event_processor = EventProcessor()
        self.batch_processor = BatchProcessor()
        self.stream_processor = StreamProcessor()
        
        self._setup_default_stages()
    
    def _setup_default_stages(self) -> None:
        """Set up the default pipeline stages."""
        from src.collectors import (
            SyslogCollector, FirewallCollector,
            WindowsCollector, LinuxCollector,
            NetworkCollector, ApplicationCollector
        )
        from src.parsers import (
            SyslogParser, FirewallParser,
            WindowsParser, LinuxParser, JSONParser
        )
        from src.normalizers import EventNormalizer
        from src.validators import ValidatorPipeline
        from src.enrichers import EnrichmentPipeline
        
        # Stage 1: Collection
        def collect_stage(data):
            # This would be implemented with actual collectors
            return data
        
        # Stage 2: Parsing
        def parse_stage(data):
            parser = self._get_parser(data.get("raw_source", "unknown"))
            if parser:
                parsed = parser.parse(data)
                if parsed:
                    return parsed
            return data
        
        # Stage 3: Normalization
        def normalize_stage(data):
            normalizer = EventNormalizer()
            return normalizer.normalize(data)
        
        # Stage 4: Validation
        def validate_stage(data):
            validator = ValidatorPipeline()
            result = validator.validate(data)
            if not result.is_valid:
                raise Exception(f"Validation failed: {result.get_error_messages()}")
            return data
        
        # Stage 5: Enrichment
        def enrich_stage(data):
            enricher = EnrichmentPipeline()
            return enricher.enrich(data)
        
        # Add stages to processor
        self.event_processor.add_stage(
            PipelineStage(StageType.COLLECT, "Collection", collect_stage, required=False)
        )
        self.event_processor.add_stage(
            PipelineStage(StageType.PARSE, "Parsing", parse_stage, required=False)
        )
        self.event_processor.add_stage(
            PipelineStage(StageType.NORMALIZE, "Normalization", normalize_stage)
        )
        self.event_processor.add_stage(
            PipelineStage(StageType.VALIDATE, "Validation", validate_stage)
        )
        self.event_processor.add_stage(
            PipelineStage(StageType.ENRICH, "Enrichment", enrich_stage, required=False)
        )
    
    def _get_parser(self, source_type: str):
        """Get parser for source type."""
        from src.parsers import (
            SyslogParser, FirewallParser,
            WindowsParser, LinuxParser, JSONParser
        )
        
        parsers = {
            "syslog": SyslogParser(),
            "firewall": FirewallParser(),
            "windows": WindowsParser(),
            "linux": LinuxParser(),
            "network": JSONParser(),
            "application": JSONParser(),
            "json": JSONParser(),
        }
        
        return parsers.get(source_type)
    
    def process_event(self, event: Dict[str, Any]) -> PipelineContext:
        """
        Process a single event through the pipeline.
        
        Args:
            event: Event to process
            
        Returns:
            PipelineContext: Processing result
        """
        return self.event_processor.process(event)
    
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
        return self.batch_processor.process_batch(events, parallel)
    
    def process_stream(self, event: Dict[str, Any]) -> None:
        """
        Submit an event to the stream processor.
        
        Args:
            event: Event to process
        """
        self.stream_processor.submit(event)
    
    def start_stream(self) -> None:
        """Start the stream processor."""
        self.stream_processor.start()
    
    def stop_stream(self) -> None:
        """Stop the stream processor."""
        self.stream_processor.stop()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get pipeline statistics.
        
        Returns:
            Dict[str, Any]: Pipeline statistics
        """
        return {
            "event_processor": self.event_processor.__class__.__name__,
            "batch_processor": {
                "max_workers": self.batch_processor.max_workers,
            },
            "stream_processor": {
                "is_running": self.stream_processor.is_running,
                "queue_size": self.stream_processor.queue_size,
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    
    def on_success(self, callback: Callable) -> None:
        """Register a callback for successful events."""
        self.stream_processor.on_success(callback)
    
    def on_failure(self, callback: Callable) -> None:
        """Register a callback for failed events."""
        self.stream_processor.on_failure(callback)
    
    def on_event(self, callback: Callable) -> None:
        """Register a callback for all events."""
        self.stream_processor.on_event(callback)
    
    def add_stage(self, stage: PipelineStage) -> None:
        """
        Add a custom stage to the pipeline.
        
        Args:
            stage: Pipeline stage to add
        """
        self.event_processor.add_stage(stage)
        self.logger.info(f"Added custom stage: {stage.name}")