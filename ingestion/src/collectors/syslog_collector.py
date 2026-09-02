"""Syslog collector implementation (UDP)."""

import socket
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.collectors.base import BaseCollector
from src.models.raw_event import RawEvent
from src.core.exceptions import CollectorError
from src.core.config import settings


class SyslogCollector(BaseCollector):
    """
    Collects syslog messages via UDP.
    
    Listens on a UDP port for syslog messages from network devices.
    Handles RFC 3164 (BSD syslog) and RFC 5424 (modern syslog) formats.
    """
    
    def __init__(
        self,
        host: str = "0.0.0.0",
        port: Optional[int] = None,
        buffer_size: int = 4096,
        timeout: float = 5.0,
        source_name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize syslog collector.
        
        Args:
            host: Interface to bind to (0.0.0.0 for all)
            port: UDP port to listen on (default from settings)
            buffer_size: UDP receive buffer size
            timeout: Socket timeout in seconds
            source_name: Name for logging
            config: Additional configuration
        """
        super().__init__(
            source_type="syslog",
            source_name=source_name or "syslog-udp",
            config=config,
        )
        self.host = host
        self.port = port or settings.syslog_port
        self.buffer_size = buffer_size
        self.timeout = timeout
        self._socket: Optional[socket.socket] = None
        
    def connect(self) -> bool:
        """Set up UDP socket for syslog reception."""
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._socket.bind((self.host, self.port))
            self._socket.settimeout(self.timeout)
            self._is_connected = True
            self._stats["connection_attempts"] += 1
            
            self.logger.info(
                f"Syslog collector listening on {self.host}:{self.port}",
                extra={"host": self.host, "port": self.port}
            )
            return True
            
        except socket.error as e:
            self._is_connected = False
            self._stats["connection_attempts"] += 1
            error_msg = f"Failed to bind syslog socket: {e}"
            self.logger.error(error_msg)
            raise CollectorError(error_msg)
        except Exception as e:
            self._is_connected = False
            self._stats["connection_attempts"] += 1
            error_msg = f"Unexpected error starting syslog collector: {e}"
            self.logger.error(error_msg)
            raise CollectorError(error_msg)
    
    def disconnect(self) -> None:
        """Close the UDP socket."""
        if self._socket:
            try:
                self._socket.close()
            except Exception as e:
                self.logger.warning(f"Error closing syslog socket: {e}")
            finally:
                self._socket = None
        self._is_connected = False
        self.logger.info("Syslog collector disconnected")
    
    def collect_one(self) -> Optional[RawEvent]:
        """
        Receive one syslog message.
        
        Returns:
            RawEvent: If a message was received.
            None: If timeout or no data.
            
        Raises:
            CollectorError: If connection is not established.
        """
        if not self._is_connected:
            raise CollectorError("Syslog collector not connected")
        
        try:
            data, addr = self._socket.recvfrom(self.buffer_size)
            
            raw_content = data.decode('utf-8', errors='ignore').strip()
            
            if not raw_content:
                return None
            
            # Parse RFC 3164 header if present (simplified)
            original_timestamp = None
            if len(raw_content) > 15 and raw_content[0:3].isalpha():
                # Try to extract timestamp from first 15 chars
                # Format: "MMM DD HH:MM:SS" or "MMM DD HH:MM:SS"
                parts = raw_content.split(' ', 3)
                if len(parts) >= 4:
                    # First three parts are timestamp components
                    original_timestamp = ' '.join(parts[0:3])
            
            event = self._create_raw_event(
                raw_content=raw_content,
                source_host=f"{addr[0]}:{addr[1]}",
                original_timestamp=original_timestamp,
                collection_metadata={
                    "source_ip": addr[0],
                    "source_port": addr[1],
                    "protocol": "UDP",
                }
            )
            
            self._update_stats(success=True)
            self.logger.debug(f"Collected syslog from {addr[0]}:{addr[1]}")
            return event
            
        except socket.timeout:
            return None
        except UnicodeDecodeError as e:
            self.logger.warning(f"Failed to decode syslog message: {e}")
            self._update_stats(success=False)
            return None
        except Exception as e:
            self.logger.error(f"Error receiving syslog: {e}")
            self._update_stats(success=False)
            return None
    
    def collect_batch(self, batch_size: int = 100) -> List[RawEvent]:
        """
        Collect multiple syslog messages.
        
        Args:
            batch_size: Maximum number to collect.
            
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
            self.logger.debug(f"Collected batch of {len(events)} syslog events")
        
        return events