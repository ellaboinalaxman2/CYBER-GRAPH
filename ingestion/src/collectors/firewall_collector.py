"""Firewall log collector implementation."""

import json
import os
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.collectors.base import BaseCollector
from src.models.raw_event import RawEvent
from src.core.exceptions import CollectorError
from src.core.config import settings


class FirewallCollector(BaseCollector):
    """
    Collects firewall logs.
    
    Supports:
    - File reading (for batch processing and development)
    - JSON formatted logs
    - Plain text logs
    - API mode (placeholder)
    """
    
    def __init__(
        self,
        source_path: Optional[str] = None,
        source_type: str = "file",  # "file" or "api"
        source_name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize firewall collector.
        
        Args:
            source_path: Path to log file (for file mode)
            source_type: "file" or "api"
            source_name: Name for logging
            config: Additional configuration
        """
        super().__init__(
            source_type="firewall",
            source_name=source_name or "firewall-collector",
            config=config,
        )
        self.source_path = source_path
        self.source_type = source_type
        self._file_handle = None
        self._line_count = 0
        
    def connect(self) -> bool:
        """Open connection to firewall data source."""
        if self.source_type == "file":
            return self._connect_file()
        elif self.source_type == "api":
            return self._connect_api()
        else:
            raise CollectorError(f"Unsupported source type: {self.source_type}")
    
    def _connect_file(self) -> bool:
        """Connect to a file source."""
        try:
            # Try sample data if no path provided
            if not self.source_path:
                sample_file = os.path.join(
                    settings.sample_data_dir,
                    "firewall_sample.log"
                )
                if os.path.exists(sample_file):
                    self.source_path = sample_file
                else:
                    self._create_sample_file()
            
            self._file_handle = open(self.source_path, 'r', encoding='utf-8')
            self._is_connected = True
            self._stats["connection_attempts"] += 1
            
            self.logger.info(
                f"Firewall collector connected to: {self.source_path}",
                extra={"path": self.source_path}
            )
            return True
            
        except FileNotFoundError as e:
            self._is_connected = False
            self._stats["connection_attempts"] += 1
            error_msg = f"Firewall log file not found: {self.source_path}"
            self.logger.error(error_msg)
            raise CollectorError(error_msg)
        except Exception as e:
            self._is_connected = False
            self._stats["connection_attempts"] += 1
            error_msg = f"Failed to open firewall log: {e}"
            self.logger.error(error_msg)
            raise CollectorError(error_msg)
    
    def _connect_api(self) -> bool:
        """Connect to an API source (placeholder)."""
        self.logger.warning("Firewall API mode not yet implemented")
        self._is_connected = False
        return False
    
    def disconnect(self) -> None:
        """Close file handle."""
        if self._file_handle:
            try:
                self._file_handle.close()
            except Exception as e:
                self.logger.warning(f"Error closing firewall log: {e}")
            finally:
                self._file_handle = None
        self._is_connected = False
        self.logger.info("Firewall collector disconnected")
    
    def collect_one(self) -> Optional[RawEvent]:
        """
        Read one line from firewall log.
        
        Returns:
            RawEvent: If a line was read.
            None: If end of file or no data.
        """
        if not self._is_connected:
            raise CollectorError("Firewall collector not connected")
        
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
                source_host="firewall-01",
                collection_metadata={
                    "line_number": self._line_count,
                    "file_path": self.source_path,
                    "mode": "file",
                }
            )
            
            self._update_stats(success=True)
            return event
            
        except Exception as e:
            self.logger.error(f"Error reading firewall log: {e}")
            self._update_stats(success=False)
            return None
    
    def collect_batch(self, batch_size: int = 100) -> List[RawEvent]:
        """
        Read multiple lines from firewall log.
        
        Args:
            batch_size: Maximum number to read.
            
        Returns:
            List[RawEvent]: Collected events.
        """
        events = []
        for _ in range(batch_size):
            event = self.collect_one()
            if event:
                events.append(event)
            else:
                break
        
        if events:
            self.logger.debug(f"Collected batch of {len(events)} firewall events")
        
        return events
    
    def _create_sample_file(self) -> None:
        """Create a sample firewall log for development."""
        os.makedirs(settings.sample_data_dir, exist_ok=True)
        sample_path = os.path.join(settings.sample_data_dir, "firewall_sample.log")
        
        samples = [
            '{"timestamp":"2026-08-29T10:30:15Z","src":"192.168.1.10","dst":"192.168.1.20","proto":"TCP","dport":22,"action":"ALLOW","interface":"eth0"}',
            '{"timestamp":"2026-08-29T10:30:20Z","src":"192.168.1.10","dst":"192.168.1.20","proto":"TCP","dport":443,"action":"ALLOW","interface":"eth0"}',
            '{"timestamp":"2026-08-29T10:30:25Z","src":"192.168.1.50","dst":"192.168.1.20","proto":"TCP","dport":22,"action":"DENY","interface":"eth0","reason":"Blocked IP"}',
            '{"timestamp":"2026-08-29T10:30:30Z","src":"10.0.0.5","dst":"192.168.1.20","proto":"TCP","dport":3389,"action":"DENY","interface":"eth0","reason":"External RDP"}',
            '{"timestamp":"2026-08-29T10:30:35Z","src":"192.168.1.10","dst":"10.0.0.10","proto":"TCP","dport":80,"action":"ALLOW","interface":"eth1"}',
            '{"timestamp":"2026-08-29T10:30:40Z","src":"192.168.1.15","dst":"192.168.1.20","proto":"UDP","dport":53,"action":"ALLOW","interface":"eth0"}',
            '{"timestamp":"2026-08-29T10:30:45Z","src":"192.168.1.10","dst":"192.168.1.20","proto":"ICMP","action":"ALLOW","interface":"eth0"}',
            '{"timestamp":"2026-08-29T10:30:50Z","src":"192.168.1.20","dst":"192.168.1.10","proto":"TCP","dport":22,"action":"ALLOW","interface":"eth0"}',
        ]
        
        with open(sample_path, 'w', encoding='utf-8') as f:
            for sample in samples:
                f.write(sample + "\n")
        
        self.source_path = sample_path
        self.logger.info(f"Created sample firewall log with {len(samples)} entries: {sample_path}")