"""Windows event log collector implementation."""

from typing import Optional, List, Dict, Any
import json
import os
from datetime import datetime

from src.collectors.base import BaseCollector
from src.models.raw_event import RawEvent
from src.core.exceptions import CollectorError
from src.core.config import settings


class WindowsCollector(BaseCollector):
    """
    Collects Windows Security Event Logs.
    
    This is a placeholder implementation that:
    - Reads sample data for development
    - Simulates Windows event collection
    - Can be extended to use pywin32 for real Windows integration
    """
    
    def __init__(
        self,
        log_name: str = "Security",
        source_path: Optional[str] = None,
        source_name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Windows collector.
        
        Args:
            log_name: Windows Event Log name (Security, System, Application)
            source_path: Path to sample data file
            source_name: Name for logging
            config: Additional configuration
        """
        super().__init__(
            source_type="windows",
            source_name=source_name or f"windows-{log_name}",
            config=config,
        )
        self.log_name = log_name or settings.windows_event_log
        self.source_path = source_path
        self._file_handle = None
        self._line_count = 0
        
    def connect(self) -> bool:
        """Connect to Windows event source."""
        try:
            # Try file-based collection for development
            if not self.source_path:
                sample_file = os.path.join(
                    settings.sample_data_dir,
                    "windows_sample.log"
                )
                if os.path.exists(sample_file):
                    self.source_path = sample_file
                else:
                    self._create_sample_file()
            
            self._file_handle = open(self.source_path, 'r', encoding='utf-8')
            self._is_connected = True
            self._stats["connection_attempts"] += 1
            
            self.logger.info(
                f"Windows collector connected to: {self.source_path}",
                extra={"log_name": self.log_name}
            )
            return True
            
        except Exception as e:
            self._is_connected = False
            self._stats["connection_attempts"] += 1
            error_msg = f"Failed to connect Windows collector: {e}"
            self.logger.error(error_msg)
            raise CollectorError(error_msg)
    
    def disconnect(self) -> None:
        """Close the file handle."""
        if self._file_handle:
            try:
                self._file_handle.close()
            except Exception as e:
                self.logger.warning(f"Error closing windows log: {e}")
            finally:
                self._file_handle = None
        self._is_connected = False
        self.logger.info("Windows collector disconnected")
    
    def collect_one(self) -> Optional[RawEvent]:
        """Read one event from Windows log."""
        if not self._is_connected:
            raise CollectorError("Windows collector not connected")
        
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
            
            # Try to parse as JSON
            raw_json = None
            try:
                raw_json = json.loads(line)
            except json.JSONDecodeError:
                pass
            
            event = self._create_raw_event(
                raw_content=line,
                raw_json=raw_json,
                source_host="windows-host",
                collection_metadata={
                    "log_name": self.log_name,
                    "line_number": self._line_count,
                }
            )
            
            self._update_stats(success=True)
            return event
            
        except Exception as e:
            self.logger.error(f"Error reading Windows log: {e}")
            self._update_stats(success=False)
            return None
    
    def collect_batch(self, batch_size: int = 100) -> List[RawEvent]:
        """Collect multiple Windows events."""
        events = []
        for _ in range(batch_size):
            event = self.collect_one()
            if event:
                events.append(event)
            else:
                break
        
        if events:
            self.logger.debug(f"Collected batch of {len(events)} Windows events")
        
        return events
    
    def _create_sample_file(self) -> None:
        """Create a sample Windows event log file."""
        os.makedirs(settings.sample_data_dir, exist_ok=True)
        sample_path = os.path.join(settings.sample_data_dir, "windows_sample.log")
        
        samples = [
            '{"timestamp":"2026-08-29T10:30:15Z","event_id":4624,"log_name":"Security","message":"An account was successfully logged on.","account_name":"john.doe","workstation_name":"PC-01","source_ip":"192.168.1.10"}',
            '{"timestamp":"2026-08-29T10:30:20Z","event_id":4625,"log_name":"Security","message":"An account failed to log on.","account_name":"admin","workstation_name":"PC-02","source_ip":"192.168.1.50"}',
            '{"timestamp":"2026-08-29T10:30:25Z","event_id":4672,"log_name":"Security","message":"Special privileges assigned to new logon.","account_name":"administrator","workstation_name":"SERVER-01"}',
            '{"timestamp":"2026-08-29T10:30:30Z","event_id":4740,"log_name":"Security","message":"A user account was locked out.","account_name":"john.doe","workstation_name":"PC-01"}',
            '{"timestamp":"2026-08-29T10:30:35Z","event_id":4720,"log_name":"Security","message":"A user account was created.","account_name":"new_user","workstation_name":"DC-01"}',
        ]
        
        with open(sample_path, 'w', encoding='utf-8') as f:
            for sample in samples:
                f.write(sample + "\n")
        
        self.source_path = sample_path
        self.logger.info(f"Created sample Windows log: {sample_path}")