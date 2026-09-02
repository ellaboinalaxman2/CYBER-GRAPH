"""Common field definitions and types for all events."""

from typing import Literal, Optional, List
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import re

# ============================================================================
# Type Definitions (Enums using Literal)
# ============================================================================

EventType = Literal[
    "NETWORK_CONNECTION",
    "NETWORK_DISCONNECTION",
    "LOGIN_SUCCESS",
    "LOGIN_FAILURE",
    "LOGIN_LOCKOUT",
    "LOGOUT",
    "PROCESS_START",
    "PROCESS_END",
    "FILE_ACCESS",
    "FILE_MODIFIED",
    "FILE_DELETED",
    "FILE_CREATED",
    "FILE_PERMISSION_CHANGE",
    "USER_CREATED",
    "USER_DELETED",
    "USER_MODIFIED",
    "GROUP_CHANGE",
    "PERMISSION_CHANGE",
    "FIREWALL_ALLOW",
    "FIREWALL_DENY",
    "FIREWALL_DROP",
    "ALERT",
    "SYSTEM_EVENT",
    "AUDIT_EVENT",
    "UNKNOWN",
]

Protocol = Literal[
    "TCP",
    "UDP",
    "ICMP",
    "HTTP",
    "HTTPS",
    "SSH",
    "FTP",
    "SFTP",
    "DNS",
    "SMTP",
    "IMAP",
    "POP3",
    "RDP",
    "SMB",
    "NFS",
    "LDAP",
    "NTP",
    "DHCP",
    "SNMP",
    "UNKNOWN",
]

Action = Literal[
    "ALLOW",
    "DENY",
    "BLOCK",
    "DROP",
    "LOG",
    "ALERT",
    "IGNORE",
    "UNKNOWN",
]

Severity = Literal[
    "INFO",
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
]

# ============================================================================
# Models
# ============================================================================

class Source(BaseModel):
    """
    Source device/entity information.
    
    Represents where the event originated from.
    """
    
    ip: Optional[str] = Field(
        None,
        description="Source IP address (IPv4 or IPv6)",
        examples=["192.168.1.100", "10.0.0.1"],
    )
    hostname: Optional[str] = Field(
        None,
        description="Source hostname or FQDN",
        examples=["PC-01", "webserver.example.com"],
    )
    port: Optional[int] = Field(
        None,
        ge=0,
        le=65535,
        description="Source port number (1-65535)",
        examples=[45122, 54321],
    )
    user: Optional[str] = Field(
        None,
        description="Source username",
        examples=["admin", "john.doe"],
    )
    mac: Optional[str] = Field(
        None,
        description="Source MAC address (format: aa:bb:cc:dd:ee:ff)",
        examples=["00:11:22:33:44:55"],
    )
    device_type: Optional[str] = Field(
        None,
        description="Type of source device",
        examples=["workstation", "server", "firewall", "router"],
    )
    
    @field_validator("ip")
    @classmethod
    def validate_ip(cls, v: Optional[str]) -> Optional[str]:
        """Validate IPv4 address format."""
        if v is None:
            return v
        
        # IPv4 pattern
        pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
        if not re.match(pattern, v):
            raise ValueError(f"Invalid IPv4 address: {v}")
        
        # Check each octet is 0-255
        parts = v.split(".")
        if not all(0 <= int(p) <= 255 for p in parts):
            raise ValueError(f"Invalid IP address (octet out of range): {v}")
        
        return v
    
    @field_validator("mac")
    @classmethod
    def validate_mac(cls, v: Optional[str]) -> Optional[str]:
        """Validate MAC address format."""
        if v is None:
            return v
        
        # Simple MAC validation (aa:bb:cc:dd:ee:ff)
        pattern = r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$"
        if not re.match(pattern, v):
            raise ValueError(f"Invalid MAC address format: {v}")
        
        return v


class Destination(BaseModel):
    """
    Destination device/entity information.
    
    Represents where the event is directed to.
    """
    
    ip: Optional[str] = Field(
        None,
        description="Destination IP address (IPv4 or IPv6)",
        examples=["192.168.1.200", "10.0.0.10"],
    )
    hostname: Optional[str] = Field(
        None,
        description="Destination hostname or FQDN",
        examples=["SERVER-01", "database.example.com"],
    )
    port: Optional[int] = Field(
        None,
        ge=0,
        le=65535,
        description="Destination port number (1-65535)",
        examples=[22, 443, 3389],
    )
    user: Optional[str] = Field(
        None,
        description="Destination username",
        examples=["root", "service_account"],
    )
    device_type: Optional[str] = Field(
        None,
        description="Type of destination device",
        examples=["server", "database", "firewall"],
    )
    
    @field_validator("ip")
    @classmethod
    def validate_ip(cls, v: Optional[str]) -> Optional[str]:
        """Validate IPv4 address format."""
        if v is None:
            return v
        
        pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
        if not re.match(pattern, v):
            raise ValueError(f"Invalid IPv4 address: {v}")
        
        parts = v.split(".")
        if not all(0 <= int(p) <= 255 for p in parts):
            raise ValueError(f"Invalid IP address (octet out of range): {v}")
        
        return v


class Metadata(BaseModel):
    """
    Common metadata for all events.
    """
    
    event_id: str = Field(
        ...,
        description="Unique event identifier (generated by the system)",
        examples=["EVT-12345678"],
        min_length=4,
        max_length=64,
    )
    timestamp: datetime = Field(
        ...,
        description="Event timestamp in UTC",
        examples=["2026-08-29T10:30:15.000Z"],
    )
    event_type: EventType = Field(
        ...,
        description="Type/category of the security event",
    )
    raw_source: str = Field(
        ...,
        description="Original source type (syslog, windows, linux, firewall, etc.)",
        examples=["syslog", "firewall", "windows"],
    )
    source: Source = Field(
        ...,
        description="Source information",
    )
    destination: Destination = Field(
        ...,
        description="Destination information",
    )
    protocol: Optional[Protocol] = Field(
        None,
        description="Network protocol used",
    )
    action: Optional[Action] = Field(
        None,
        description="Action taken (allow, deny, block, etc.)",
    )
    severity: Optional[Severity] = Field(
        None,
        description="Event severity level",
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "EVT-12345678",
                "timestamp": "2026-08-29T10:30:15.000Z",
                "event_type": "NETWORK_CONNECTION",
                "raw_source": "firewall",
                "source": {
                    "ip": "192.168.1.10",
                    "hostname": "PC-01",
                    "port": 45122,
                },
                "destination": {
                    "ip": "192.168.1.20",
                    "hostname": "SERVER-01",
                    "port": 22,
                },
                "protocol": "TCP",
                "action": "ALLOW",
                "severity": "INFO",
            }
        }