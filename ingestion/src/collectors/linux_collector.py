"""Linux system log collector implementation."""

from typing import Optional, List, Dict, Any
import os
from datetime import datetime

from src.collectors.base import BaseCollector
from src.models.raw_event import RawEvent
from src.core.exceptions import CollectorError
from src.core.config import settings


class LinuxCollector(BaseCollector):
    """
    Collects Linux system and security logs.
    
    This collector reads from Linux log files like:
    - /var/log/auth.log (authentication)
    - /var/log/syslog (system)
    - /var/log/secure (security)
    
    This is a placeholder for development that reads sample data.
    """
    
    def __init__(
        self,
        log_file: str = "/var/log/auth.log",
        source_path: Optional[str] = None,
        source_name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Linux collector.
        
        Args:
            log_file: Linux log file path
            source_path: Path to sample data file
            source_name: Name for logging
            config: Additional configuration
        """
        super().__init__(
            source_type="linux",
            source_name=source_name or "linux-collector",
            config=config,
        )
        self.log_file = log_file
        self.source_path = source_path
        self._file_handle = None
        self._line_count = 0
        
    def connect(self) -> bool:
        """Connect to Linux log source."""
        try:
            # Try file-based collection for development
            if not self.source_path:
                sample_file = os.path.join(
                    settings.sample_data_dir,
                    "linux_sample.log"
                )
                if os.path.exists(sample_file):
                    self.source_path = sample_file
                else:
                    self._create_sample_file()
            
            self._file_handle = open(self.source_path, 'r', encoding='utf-8')
            self._is_connected = True
            self._stats["connection_attempts"] += 1
            
            self.logger.info(
                f"Linux collector connected to: {self.source_path}",
                extra={"log_file": self.log_file}
            )
            return True
            
        except Exception as e:
            self._is_connected = False
            self._stats["connection_attempts"] += 1
            error_msg = f"Failed to connect Linux collector: {e}"
            self.logger.error(error_msg)
            raise CollectorError(error_msg)
    
    def disconnect(self) -> None:
        """Close the file handle."""
        if self._file_handle:
            try:
                self._file_handle.close()
            except Exception as e:
                self.logger.warning(f"Error closing Linux log: {e}")
            finally:
                self._file_handle = None
        self._is_connected = False
        self.logger.info("Linux collector disconnected")
    
    def collect_one(self) -> Optional[RawEvent]:
        """Read one line from Linux log."""
        if not self._is_connected:
            raise CollectorError("Linux collector not connected")
        
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
            
            # Extract original timestamp if possible
            original_timestamp = None
            parts = line.split(' ', 3)
            if len(parts) >= 3:
                # Linux logs typically start with "MMM DD HH:MM:SS"
                original_timestamp = ' '.join(parts[0:3])
            
            event = self._create_raw_event(
                raw_content=line,
                source_host="linux-host",
                original_timestamp=original_timestamp,
                collection_metadata={
                    "log_file": self.log_file,
                    "line_number": self._line_count,
                }
            )
            
            self._update_stats(success=True)
            return event
            
        except Exception as e:
            self.logger.error(f"Error reading Linux log: {e}")
            self._update_stats(success=False)
            return None
    
    def collect_batch(self, batch_size: int = 100) -> List[RawEvent]:
        """Collect multiple Linux log entries."""
        events = []
        for _ in range(batch_size):
            event = self.collect_one()
            if event:
                events.append(event)
            else:
                break
        
        if events:
            self.logger.debug(f"Collected batch of {len(events)} Linux events")
        
        return events
    
    def _create_sample_file(self) -> None:
        """Create a sample Linux log file."""
        os.makedirs(settings.sample_data_dir, exist_ok=True)
        sample_path = os.path.join(settings.sample_data_dir, "linux_sample.log")
        
        samples = [
            'Aug 29 10:30:15 server01 sshd[1234]: Failed password for invalid user admin from 192.168.1.50 port 45122 ssh2',
            'Aug 29 10:30:20 server01 sshd[2345]: Accepted password for john from 192.168.1.10 port 54321 ssh2',
            'Aug 29 10:30:25 server01 sudo[3456]: john : TTY=pts/1 ; PWD=/home/john ; USER=root ; COMMAND=/bin/systemctl restart nginx',
            'Aug 29 10:30:30 server01 sshd[4567]: Connection closed by 192.168.1.10 port 54321',
            'Aug 29 10:30:35 server01 kernel: [12345.678] Firewall: *TCP_OUT Blocked* IN= OUT=eth0 SRC=192.168.1.20 DST=10.0.0.5 LEN=60 TOS=0x00 PREC=0x00 TTL=64 ID=12345 PROTO=TCP SPT=22 DPT=3389 WINDOW=65535 RES=0x00 SYN URGP=0',
        ]
        
        with open(sample_path, 'w', encoding='utf-8') as f:
            for sample in samples:
                f.write(sample + "\n")
        
        self.source_path = sample_path
        self.logger.info(f"Created sample Linux log: {sample_path}")