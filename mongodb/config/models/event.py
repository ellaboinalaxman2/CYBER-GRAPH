from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class EventType(str, Enum):
    NETWORK_CONNECTION = "NETWORK_CONNECTION"
    NETWORK_DISCONNECTION = "NETWORK_DISCONNECTION"
    AUTHENTICATION = "AUTHENTICATION"
    PROCESS_START = "PROCESS_START"
    PROCESS_END = "PROCESS_END"
    FILE_ACCESS = "FILE_ACCESS"
    REGISTRY_CHANGE = "REGISTRY_CHANGE"
    DNS_QUERY = "DNS_QUERY"
    HTTP_REQUEST = "HTTP_REQUEST"
    DATABASE_ACCESS = "DATABASE_ACCESS"
    SYSTEM_SHUTDOWN = "SYSTEM_SHUTDOWN"
    SYSTEM_STARTUP = "SYSTEM_STARTUP"
    UNKNOWN = "UNKNOWN"

class Protocol(str, Enum):
    TCP = "TCP"
    UDP = "UDP"
    ICMP = "ICMP"
    HTTP = "HTTP"
    HTTPS = "HTTPS"
    SSH = "SSH"
    FTP = "FTP"
    DNS = "DNS"
    SMB = "SMB"
    RDP = "RDP"
    MYSQL = "MYSQL"
    POSTGRES = "POSTGRES"

class EventModel:
    """Security event model for MongoDB"""
    
    def __init__(self, data: dict):
        self.data = data
    
    @staticmethod
    def schema() -> dict:
        """Event schema definition"""
        return {
            "event_id": str,           # Unique event identifier
            "timestamp": datetime,      # Event timestamp
            "source": str,             # Source IP/hostname
            "source_port": Optional[int],  # Source port
            "destination": str,        # Destination IP/hostname
            "destination_port": Optional[int],  # Destination port
            "protocol": Protocol,      # Network protocol
            "event_type": EventType,   # Type of event
            "user": Optional[str],     # Associated user
            "process": Optional[str],  # Associated process
            "command_line": Optional[str],  # Full command line
            "message": str,            # Event message
            "severity": Optional[str], # Event severity
            "raw_log": str,            # Original raw log
            "normalized_data": Dict[str, Any],  # Normalized fields
            "tags": list,              # Event tags
            "is_anomaly": bool,        # Anomaly flag
            "anomaly_score": Optional[float],  # Anomaly score
            "source_hostname": Optional[str],  # Source hostname
            "destination_hostname": Optional[str],  # Destination hostname
            "bytes_sent": Optional[int],  # Bytes sent
            "bytes_received": Optional[int],  # Bytes received
            "duration": Optional[float],  # Connection duration
            "country": Optional[str],  # Country for IP
            "metadata": Dict[str, Any],  # Additional metadata
            "processed_at": datetime,  # Processing timestamp
            "ingestion_timestamp": datetime,  # When ingested
            "source_type": str        # Log source type
        }
    
    @classmethod
    def create(cls, event_data: dict) -> dict:
        """Create a new event document"""
        return {
            "event_id": event_data.get("event_id"),
            "timestamp": event_data.get("timestamp", datetime.utcnow()),
            "source": event_data.get("source"),
            "source_port": event_data.get("source_port"),
            "destination": event_data.get("destination"),
            "destination_port": event_data.get("destination_port"),
            "protocol": event_data.get("protocol"),
            "event_type": event_data.get("event_type", EventType.UNKNOWN),
            "user": event_data.get("user"),
            "process": event_data.get("process"),
            "command_line": event_data.get("command_line"),
            "message": event_data.get("message"),
            "severity": event_data.get("severity"),
            "raw_log": event_data.get("raw_log"),
            "normalized_data": event_data.get("normalized_data", {}),
            "tags": event_data.get("tags", []),
            "is_anomaly": event_data.get("is_anomaly", False),
            "anomaly_score": event_data.get("anomaly_score"),
            "source_hostname": event_data.get("source_hostname"),
            "destination_hostname": event_data.get("destination_hostname"),
            "bytes_sent": event_data.get("bytes_sent"),
            "bytes_received": event_data.get("bytes_received"),
            "duration": event_data.get("duration"),
            "country": event_data.get("country"),
            "metadata": event_data.get("metadata", {}),
            "processed_at": datetime.utcnow(),
            "ingestion_timestamp": datetime.utcnow(),
            "source_type": event_data.get("source_type", "NETWORK")
        }