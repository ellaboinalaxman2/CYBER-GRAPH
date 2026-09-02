"""Data source management for ingestion."""

from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime


class DataSourceType(str, Enum):
    """Types of data sources."""
    FILE = "file"
    STREAM = "stream"
    API = "api"
    DATABASE = "database"
    SYSLOG = "syslog"


class DataFormat(str, Enum):
    """Data formats."""
    JSON = "json"
    CSV = "csv"
    LOG = "log"
    SYSLOG = "syslog"
    WINDOWS = "windows"
    LINUX = "linux"
    CUSTOM = "custom"


@dataclass
class DataSource:
    """Data source configuration."""
    
    # Core
    name: str
    type: DataSourceType
    format: DataFormat
    enabled: bool = True
    
    # File configuration
    file_path: Optional[str] = None
    file_pattern: Optional[str] = None
    watch_directory: Optional[str] = None
    
    # Stream configuration
    host: Optional[str] = None
    port: Optional[int] = None
    protocol: Optional[str] = None
    
    # Processing
    batch_size: int = 100
    poll_interval: int = 5  # seconds
    max_retries: int = 3
    
    # Metadata
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_processed: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "type": self.type.value,
            "format": self.format.value,
            "enabled": self.enabled,
            "file_path": self.file_path,
            "file_pattern": self.file_pattern,
            "watch_directory": self.watch_directory,
            "host": self.host,
            "port": self.port,
            "protocol": self.protocol,
            "batch_size": self.batch_size,
            "poll_interval": self.poll_interval,
            "description": self.description,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() + "Z" if self.created_at else None,
            "last_processed": self.last_processed.isoformat() + "Z" if self.last_processed else None,
        }


class DataSourceManager:
    """Manages data sources."""
    
    def __init__(self):
        """Initialize the data source manager."""
        self.sources: Dict[str, DataSource] = {}
        self._load_default_sources()
    
    def _load_default_sources(self) -> None:
        """Load default data sources."""
        default_sources = [
            DataSource(
                name="firewall_logs",
                type=DataSourceType.FILE,
                format=DataFormat.JSON,
                file_path="data/input/batch/firewall_logs.json",
                file_pattern="firewall_*.json",
                watch_directory="data/input/batch",
                description="Firewall logs in JSON format",
                tags=["firewall", "network"],
            ),
            DataSource(
                name="syslog_stream",
                type=DataSourceType.SYSLOG,
                format=DataFormat.SYSLOG,
                host="0.0.0.0",
                port=514,
                protocol="udp",
                description="Syslog stream from network devices",
                tags=["syslog", "network"],
            ),
            DataSource(
                name="windows_events",
                type=DataSourceType.FILE,
                format=DataFormat.WINDOWS,
                file_path="data/input/batch/windows_events.json",
                description="Windows event logs",
                tags=["windows", "security"],
            ),
            DataSource(
                name="linux_logs",
                type=DataSourceType.FILE,
                format=DataFormat.LINUX,
                file_path="data/input/batch/linux_logs.log",
                description="Linux system logs",
                tags=["linux", "system"],
            ),
        ]
        
        for source in default_sources:
            self.sources[source.name] = source
    
    def add_source(self, source: DataSource) -> None:
        """Add a data source."""
        self.sources[source.name] = source
    
    def get_source(self, name: str) -> Optional[DataSource]:
        """Get a data source by name."""
        return self.sources.get(name)
    
    def get_enabled_sources(self) -> List[DataSource]:
        """Get all enabled data sources."""
        return [s for s in self.sources.values() if s.enabled]
    
    def get_sources_by_type(self, source_type: DataSourceType) -> List[DataSource]:
        """Get sources by type."""
        return [s for s in self.sources.values() if s.type == source_type]
    
    def disable_source(self, name: str) -> None:
        """Disable a data source."""
        if name in self.sources:
            self.sources[name].enabled = False
    
    def enable_source(self, name: str) -> None:
        """Enable a data source."""
        if name in self.sources:
            self.sources[name].enabled = True
    
    def update_last_processed(self, name: str) -> None:
        """Update the last processed timestamp for a source."""
        if name in self.sources:
            self.sources[name].last_processed = datetime.utcnow()