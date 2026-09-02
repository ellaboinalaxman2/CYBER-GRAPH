"""Network traffic collector implementation."""

from typing import Optional, List, Dict, Any
import json
import os
from datetime import datetime

from src.collectors.base import BaseCollector
from src.models.raw_event import RawEvent
from src.core.exceptions import CollectorError
from src.core.config import settings


class NetworkCollector(BaseCollector):
    """
    Collects network traffic data.
    
    This is a placeholder collector that:
    - Reads sample PCAP-like data for development
    - Simulates network traffic collection
    - Can be extended to use Scapy or other packet capture libraries
    """
    
    def __init__(
        self,
        interface: str = "eth0",
        source_path: Optional[str] = None,
        source_name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize network collector.
        
        Args:
            interface: Network interface to monitor
            source_path: Path to sample data file
            source_name: Name for logging
            config: Additional configuration
        """
        super().__init__(
            source_type="network",
            source_name=source_name or "network-collector",
            config=config,
        )
        self.interface = interface
        self.source_path = source_path
        self._file_handle = None
        self._line_count = 0
        
    def connect(self) -> bool:
        """Connect to network source."""
        try:
            # File-based collection for development
            if not self.source_path:
                sample_file = os.path.join(
                    settings.sample_data_dir,
                    "network_sample.log"
                )
                if os.path.exists(sample_file):
                    self.source_path = sample_file
                else:
                    self._create_sample_file()
            
            self._file_handle = open(self.source_path, 'r', encoding='utf-8')
            self._is_connected = True
            self._stats["connection_attempts"] += 1
            
            self.logger.info(
                f"Network collector connected to: {self.source_path}",
                extra={"interface": self.interface}
            )
            return True
            
        except Exception as e:
            self._is_connected = False
            self._stats["connection_attempts"] += 1
            error_msg = f"Failed to connect network collector: {e}"
            self.logger.error(error_msg)
            raise CollectorError(error_msg)
    
    def disconnect(self) -> None:
        """Close the file handle."""
        if self._file_handle:
            try:
                self._file_handle.close()
            except Exception as e:
                self.logger.warning(f"Error closing network log: {e}")
            finally:
                self._file_handle = None
        self._is_connected = False
        self.logger.info("Network collector disconnected")
    
    def collect_one(self) -> Optional[RawEvent]:
        """Read one network event."""
        if not self._is_connected:
            raise CollectorError("Network collector not connected")
        
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
                source_host=f"interface-{self.interface}",
                collection_metadata={
                    "interface": self.interface,
                    "line_number": self._line_count,
                }
            )
            
            self._update_stats(success=True)
            return event
            
        except Exception as e:
            self.logger.error(f"Error reading network data: {e}")
            self._update_stats(success=False)
            return None
    
    def collect_batch(self, batch_size: int = 100) -> List[RawEvent]:
        """Collect multiple network events."""
        events = []
        for _ in range(batch_size):
            event = self.collect_one()
            if event:
                events.append(event)
            else:
                break
        
        if events:
            self.logger.debug(f"Collected batch of {len(events)} network events")
        
        return events
    
    def _create_sample_file(self) -> None:
        """Create a sample network traffic file."""
        os.makedirs(settings.sample_data_dir, exist_ok=True)
        sample_path = os.path.join(settings.sample_data_dir, "network_sample.log")
        
        samples = [
            '{"timestamp":"2026-08-29T10:30:15Z","src_ip":"192.168.1.10","src_port":45122,"dst_ip":"192.168.1.20","dst_port":22,"protocol":"TCP","bytes":64,"packets":1,"flags":"SYN"}',
            '{"timestamp":"2026-08-29T10:30:15Z","src_ip":"192.168.1.20","src_port":22,"dst_ip":"192.168.1.10","dst_port":45122,"protocol":"TCP","bytes":40,"packets":1,"flags":"SYN-ACK"}',
            '{"timestamp":"2026-08-29T10:30:15Z","src_ip":"192.168.1.10","src_port":45122,"dst_ip":"192.168.1.20","dst_port":22,"protocol":"TCP","bytes":40,"packets":1,"flags":"ACK"}',
            '{"timestamp":"2026-08-29T10:30:20Z","src_ip":"192.168.1.10","src_port":54321,"dst_ip":"192.168.1.20","dst_port":443,"protocol":"TCP","bytes":1500,"packets":1,"flags":"PSH-ACK"}',
            '{"timestamp":"2026-08-29T10:30:25Z","src_ip":"192.168.1.50","src_port":12345,"dst_ip":"192.168.1.20","dst_port":22,"protocol":"TCP","bytes":64,"packets":1,"flags":"SYN"}',
            '{"timestamp":"2026-08-29T10:30:25Z","src_ip":"192.168.1.20","src_port":22,"dst_ip":"192.168.1.50","dst_port":12345,"protocol":"TCP","bytes":40,"packets":1,"flags":"RST-ACK"}',
        ]
        
        with open(sample_path, 'w', encoding='utf-8') as f:
            for sample in samples:
                f.write(sample + "\n")
        
        self.source_path = sample_path
        self.logger.info(f"Created sample network log: {sample_path}")