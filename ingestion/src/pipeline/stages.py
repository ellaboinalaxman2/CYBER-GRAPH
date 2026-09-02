"""Pipeline stage definitions."""

from enum import Enum
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime


class StageStatus(str, Enum):
    """Status of a pipeline stage."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class StageType(str, Enum):
    """Types of pipeline stages."""
    COLLECT = "collect"
    PARSE = "parse"
    NORMALIZE = "normalize"
    VALIDATE = "validate"
    ENRICH = "enrich"
    OUTPUT = "output"


@dataclass
class StageResult:
    """Result of a pipeline stage."""
    stage_type: StageType
    status: StageStatus
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "stage": self.stage_type.value,
            "status": self.status.value,
            "has_data": self.data is not None,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata or {},
        }


class PipelineStage:
    """Represents a single pipeline stage."""
    
    def __init__(
        self,
        stage_type: StageType,
        name: str,
        processor: Callable,
        required: bool = True,
        retry_count: int = 0,
    ):
        """
        Initialize a pipeline stage.
        
        Args:
            stage_type: Type of stage
            name: Display name
            processor: Function to execute
            required: Whether this stage is required
            retry_count: Number of retries on failure
        """
        self.stage_type = stage_type
        self.name = name
        self.processor = processor
        self.required = required
        self.retry_count = retry_count
        self.retries_used = 0
    
    def execute(self, data: Dict[str, Any]) -> StageResult:
        """
        Execute the stage.
        
        Args:
            data: Input data for the stage
            
        Returns:
            StageResult: Result of execution
        """
        start_time = datetime.utcnow()
        
        try:
            result = self.processor(data)
            
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return StageResult(
                stage_type=self.stage_type,
                status=StageStatus.COMPLETED,
                data=result,
                duration_ms=duration,
            )
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            if self.retries_used < self.retry_count:
                self.retries_used += 1
                return self.execute(data)
            
            return StageResult(
                stage_type=self.stage_type,
                status=StageStatus.FAILED,
                error=str(e),
                duration_ms=duration,
            )