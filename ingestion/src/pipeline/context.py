"""Pipeline execution context."""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class PipelineContext:
    """
    Execution context for a pipeline run.
    
    Tracks the state of a single event or batch through the pipeline.
    """
    
    # Core identifiers
    run_id: str = field(default_factory=lambda: f"RUN-{uuid.uuid4().hex[:8].upper()}")
    event_id: Optional[str] = None
    source_type: Optional[str] = None
    
    # Data
    original_data: Optional[Dict[str, Any]] = None
    current_data: Optional[Dict[str, Any]] = None
    results: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    stage_results: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time_ms: float = 0.0
    
    def add_stage_result(self, result: Dict[str, Any]) -> None:
        """Add a stage result."""
        self.stage_results.append(result)
    
    def add_error(self, error: str) -> None:
        """Add an error."""
        self.errors.append(error)
    
    def add_warning(self, warning: str) -> None:
        """Add a warning."""
        self.warnings.append(warning)
    
    def complete(self) -> None:
        """Mark the pipeline as complete."""
        self.completed_at = datetime.utcnow()
        self.processing_time_ms = (
            (self.completed_at - self.started_at).total_seconds() * 1000
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "run_id": self.run_id,
            "event_id": self.event_id,
            "source_type": self.source_type,
            "started_at": self.started_at.isoformat() + "Z" if self.started_at else None,
            "completed_at": self.completed_at.isoformat() + "Z" if self.completed_at else None,
            "processing_time_ms": self.processing_time_ms,
            "stage_results": self.stage_results,
            "errors": self.errors,
            "warnings": self.warnings,
            "has_data": self.current_data is not None,
            "metadata": self.metadata,
        }
    
    @property
    def is_successful(self) -> bool:
        """Check if the pipeline completed successfully."""
        return len(self.errors) == 0 and self.completed_at is not None
    
    @property
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0