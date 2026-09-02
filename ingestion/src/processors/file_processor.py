"""Base file processor."""

import os
import json
import csv
from typing import Dict, Any, Optional, List, Iterator
from pathlib import Path
from abc import ABC, abstractmethod

from src.core.logging import get_logger
from src.core.exceptions import ParserError


class FileProcessor(ABC):
    """Base class for file processors."""
    
    def __init__(self):
        """Initialize the file processor."""
        self.logger = get_logger(f"processor.{self.__class__.__name__}")
        self._stats = {
            "files_processed": 0,
            "events_processed": 0,
            "events_failed": 0,
            "total_size": 0,
        }
    
    @abstractmethod
    def process_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Process a file and extract events.
        
        Args:
            file_path: Path to the file
            
        Returns:
            List[Dict[str, Any]]: Extracted events
        """
        pass
    
    @abstractmethod
    def supports(self, file_path: str) -> bool:
        """
        Check if the processor supports the file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            bool: True if supported
        """
        pass
    
    def _update_stats(self, events_count: int, failed_count: int = 0, size: int = 0) -> None:
        """Update processing statistics."""
        self._stats["events_processed"] += events_count
        self._stats["events_failed"] += failed_count
        if size:
            self._stats["total_size"] += size
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return self._stats.copy()


class JSONProcessor(FileProcessor):
    """Processes JSON files."""
    
    def process_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Process a JSON file.
        
        Supports:
        - Array of objects
        - Single object
        - JSONL (newline-delimited JSON)
        """
        events = []
        
        try:
            file_size = os.path.getsize(file_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Try as JSON array
                try:
                    data = json.loads(content)
                    if isinstance(data, list):
                        events = data
                    elif isinstance(data, dict):
                        events = [data]
                except json.JSONDecodeError:
                    # Try as JSONL (newline-delimited)
                    lines = content.strip().split('\n')
                    for line in lines:
                        if line.strip():
                            try:
                                event = json.loads(line)
                                events.append(event)
                            except json.JSONDecodeError:
                                self.logger.warning(f"Failed to parse JSONL line: {line[:100]}")
                                self._stats["events_failed"] += 1
            
            self._update_stats(len(events), 0, file_size)
            self.logger.info(f"Processed {len(events)} events from {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to process JSON file {file_path}: {e}")
            raise
        
        return events
    
    def supports(self, file_path: str) -> bool:
        """Check if the file is JSON."""
        return file_path.lower().endswith(('.json', '.jsonl'))


class CSVProcessor(FileProcessor):
    """Processes CSV files."""
    
    def process_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Process a CSV file.
        
        Expects:
        - Header row with column names
        - Each row becomes a dictionary
        """
        events = []
        
        try:
            file_size = os.path.getsize(file_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert empty strings to None
                    event = {k: (v if v else None) for k, v in row.items()}
                    events.append(event)
            
            self._update_stats(len(events), 0, file_size)
            self.logger.info(f"Processed {len(events)} events from {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to process CSV file {file_path}: {e}")
            raise
        
        return events
    
    def supports(self, file_path: str) -> bool:
        """Check if the file is CSV."""
        return file_path.lower().endswith('.csv')


class LogProcessor(FileProcessor):
    """Processes log files."""
    
    def __init__(self, parser=None):
        """
        Initialize log processor.
        
        Args:
            parser: Parser to use for log lines
        """
        super().__init__()
        self.parser = parser
    
    def process_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Process a log file.
        
        Each line is treated as a separate event.
        """
        events = []
        failed_count = 0
        
        try:
            file_size = os.path.getsize(file_path)
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    if self.parser:
                        try:
                            parsed = self.parser.parse(line)
                            if parsed:
                                events.append(parsed)
                            else:
                                failed_count += 1
                        except Exception as e:
                            self.logger.warning(f"Failed to parse line {line_num}: {e}")
                            failed_count += 1
                    else:
                        # Raw line as event
                        events.append({
                            "raw_content": line,
                            "line_number": line_num,
                            "source": os.path.basename(file_path),
                        })
            
            self._update_stats(len(events), failed_count, file_size)
            self.logger.info(f"Processed {len(events)} events from {file_path} ({failed_count} failed)")
            
        except Exception as e:
            self.logger.error(f"Failed to process log file {file_path}: {e}")
            raise
        
        return events
    
    def supports(self, file_path: str) -> bool:
        """Check if the file is a log file."""
        extensions = ['.log', '.txt', '.syslog', '.auth']
        return any(file_path.lower().endswith(ext) for ext in extensions)