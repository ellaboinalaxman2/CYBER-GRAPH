"""Application log collector implementation."""

from typing import Optional, List, Dict, Any
import json
import os
from datetime import datetime

from src.collectors.base import BaseCollector
from src.models.raw_event import RawEvent
from src.core.exceptions import CollectorError
from src.core.config import settings


class ApplicationCollector(BaseCollector):
    """
    Collects application-generated security events.
    
    This collector handles logs from various applications like:
    - Web servers (Apache, Nginx)
    - Databases (MySQL, PostgreSQL)
    - Applications with security logging
    
    This is a placeholder for development that reads sample data.
    """
    
    def __init__(
        self,
        app_name: str = "webapp",
        source_path: Optional[str] = None,
        source_name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize application collector.
        
        Args:
            app_name: Name of the application
            source_path: Path to sample data file
            source_name: Name for logging
            config: Additional configuration
        """
        super().__init__(
            source_type="application",
            source_name=source_name or f"app-{app_name}",
            config=config,
        )
        self.app_name = app_name
        self.source_path = source_path
        self._file_handle = None
        self._line_count = 0
        
    def connect(self) -> bool:
        """Connect to application log source."""
        try:
            if not self.source_path:
                sample_file = os.path.join(
                    settings.sample_data_dir,
                    "application_sample.log"
                )
                if os.path.exists(sample_file):
                    self.source_path = sample_file
                else:
                    self._create_sample_file()
            
            self._file_handle = open(self.source_path, 'r', encoding='utf-8')
            self._is_connected = True
            self._stats["connection_attempts"] += 1
            
            self.logger.info(
                f"Application collector connected to: {self.source_path}",
                extra={"app_name": self.app_name}
            )
            return True
            
        except Exception as e:
            self._is_connected = False
            self._stats["connection_attempts"] += 1
            error_msg = f"Failed to connect application collector: {e}"
            self.logger.error(error_msg)
            raise CollectorError(error_msg)
    
    def disconnect(self) -> None:
        """Close the file handle."""
        if self._file_handle:
            try:
                self._file_handle.close()
            except Exception as e:
                self.logger.warning(f"Error closing application log: {e}")
            finally:
                self._file_handle = None
        self._is_connected = False
        self.logger.info("Application collector disconnected")
    
    def collect_one(self) -> Optional[RawEvent]:
        """Read one application log entry."""
        if not self._is_connected:
            raise CollectorError("Application collector not connected")
        
        if not self._file_handle:
            return None
        
        try:
            line = self._file_handle.readline()
            
            if not line:
                return None
            
            line = line.strip()
            if not line:
                return None
            
            self._line_count += 1
            
            raw_json = None
            try:
                raw_json = json.loads(line)
            except json.JSONDecodeError:
                pass
            
            event = self._create_raw_event(
                raw_content=line,
                raw_json=raw_json,
                source_host=f"app-{self.app_name}",
                collection_metadata={
                    "app_name": self.app_name,
                    "line_number": self._line_count,
                }
            )
            
            self._update_stats(success=True)
            return event
            
        except Exception as e:
            self.logger.error(f"Error reading application log: {e}")
            self._update_stats(success=False)
            return None
    
    def collect_batch(self, batch_size: int = 100) -> List[RawEvent]:
        """Collect multiple application events."""
        events = []
        for _ in range(batch_size):
            event = self.collect_one()
            if event:
                events.append(event)
            else:
                break
        
        if events:
            self.logger.debug(f"Collected batch of {len(events)} application events")
        
        return events
    
    def _create_sample_file(self) -> None:
        """Create a sample application log file."""
        os.makedirs(settings.sample_data_dir, exist_ok=True)
        sample_path = os.path.join(settings.sample_data_dir, "application_sample.log")
        
        samples = [
            '{"timestamp":"2026-08-29T10:30:15Z","level":"INFO","app":"webapp","message":"User login successful","user":"john.doe","ip":"192.168.1.10","session_id":"abc123"}',
            '{"timestamp":"2026-08-29T10:30:20Z","level":"WARNING","app":"webapp","message":"Failed login attempt","user":"admin","ip":"192.168.1.50","attempts":3}',
            '{"timestamp":"2026-08-29T10:30:25Z","level":"INFO","app":"webapp","message":"API request processed","endpoint":"/api/users","method":"GET","user":"john.doe"}',
            '{"timestamp":"2026-08-29T10:30:30Z","level":"ERROR","app":"database","message":"Query failed","query":"SELECT * FROM users","user":"app_user","error":"Connection timeout"}',
            '{"timestamp":"2026-08-29T10:30:35Z","level":"SECURITY","app":"webapp","message":"Permission denied","user":"test_user","resource":"/admin","ip":"10.0.0.5"}',
            '{"timestamp":"2026-08-29T10:30:40Z","level":"INFO","app":"webapp","message":"User logout","user":"john.doe","ip":"192.168.1.10"}',
        ]
        
        with open(sample_path, 'w', encoding='utf-8') as f:
            for sample in samples:
                f.write(sample + "\n")
        
        self.source_path = sample_path
        self.logger.info(f"Created sample application log: {sample_path}")