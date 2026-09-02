"""Batch ingestion for files."""

import os
import shutil
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import json

from src.ingestion.data_source import DataSource, DataSourceType
from src.processors.file_processor import JSONProcessor, CSVProcessor, LogProcessor
from src.pipeline import Pipeline
from src.core.logging import get_logger
from src.core.config import settings


class BatchIngester:
    """
    Batch ingester for processing files.
    
    Supports:
    - Multiple file formats (JSON, CSV, LOG)
    - Directory watching
    - File archiving
    - Error handling
    """
    
    def __init__(self):
        """Initialize the batch ingester."""
        self.logger = get_logger("ingestion.batch")
        self.pipeline = Pipeline()
        
        # Register processors
        self.processors = [
            JSONProcessor(),
            CSVProcessor(),
            LogProcessor(),
        ]
        
        # Input/output directories
        self.input_dir = Path("data/input/batch")
        self.processed_dir = Path("data/processed")
        self.failed_dir = Path("data/failed")
        
        # Create directories
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.failed_dir.mkdir(parents=True, exist_ok=True)
        
        self._stats = {
            "files_processed": 0,
            "events_processed": 0,
            "events_failed": 0,
            "files_failed": 0,
            "last_run": None,
        }
    
    def ingest_file(self, file_path: str, source_name: str = "unknown") -> Dict[str, Any]:
        """
        Ingest a single file.
        
        Args:
            file_path: Path to the file
            source_name: Name of the data source
            
        Returns:
            Dict[str, Any]: Ingestion results
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                "status": "failed",
                "error": f"File not found: {file_path}",
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
        
        self.logger.info(f"Processing file: {file_path}")
        
        # Find appropriate processor
        processor = self._get_processor(str(file_path))
        
        if not processor:
            return {
                "status": "failed",
                "error": f"No processor found for: {file_path}",
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
        
        try:
            # Process the file
            events = processor.process_file(str(file_path))
            
            if not events:
                return {
                    "status": "completed",
                    "events_count": 0,
                    "message": "No events found in file",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                }
            
            # Process through pipeline
            results = self.pipeline.process_batch(events, parallel=False)
            
            successful = sum(1 for r in results if r.is_successful)
            failed = len(results) - successful
            
            # Move processed file
            self._archive_file(file_path, successful > 0)
            
            # Update stats
            self._stats["files_processed"] += 1
            self._stats["events_processed"] += len(events)
            self._stats["events_failed"] += failed
            self._stats["last_run"] = datetime.utcnow()
            
            return {
                "status": "completed",
                "file": str(file_path),
                "events_total": len(events),
                "events_successful": successful,
                "events_failed": failed,
                "source": source_name,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
            
        except Exception as e:
            self.logger.error(f"Failed to ingest file {file_path}: {e}")
            self._stats["files_failed"] += 1
            
            # Move to failed directory
            self._archive_file(file_path, False, is_failed=True)
            
            return {
                "status": "failed",
                "file": str(file_path),
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
    
    def ingest_directory(self, directory_path: str, pattern: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Ingest all files in a directory.
        
        Args:
            directory_path: Directory to process
            pattern: Optional file pattern to match
            
        Returns:
            List[Dict[str, Any]]: Results for each file
        """
        directory = Path(directory_path)
        
        if not directory.exists():
            self.logger.error(f"Directory not found: {directory_path}")
            return []
        
        results = []
        
        # Find files
        if pattern:
            files = list(directory.glob(pattern))
        else:
            files = list(directory.glob('*'))
            # Exclude directories
            files = [f for f in files if f.is_file()]
        
        self.logger.info(f"Found {len(files)} files in {directory_path}")
        
        for file_path in files:
            result = self.ingest_file(str(file_path), directory_path)
            results.append(result)
        
        return results
    
    def _get_processor(self, file_path: str):
        """Get the appropriate processor for the file."""
        for processor in self.processors:
            if processor.supports(file_path):
                return processor
        return None
    
    def _archive_file(self, file_path: Path, success: bool, is_failed: bool = False) -> None:
        """Archive a processed file."""
        try:
            if is_failed:
                dest_dir = self.failed_dir
            elif success:
                dest_dir = self.processed_dir
            else:
                dest_dir = self.failed_dir
            
            # Create timestamped filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            dest_path = dest_dir / f"{file_path.stem}_{timestamp}{file_path.suffix}"
            
            # Move file
            shutil.move(str(file_path), str(dest_path))
            self.logger.info(f"Archived file to: {dest_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to archive file: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get ingestion statistics."""
        return {
            **self._stats,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }