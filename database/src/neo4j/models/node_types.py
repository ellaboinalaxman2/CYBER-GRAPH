"""Node types for Neo4j graph."""

from enum import Enum
from typing import Dict, Any


class NodeType(str, Enum):
    """Node types in the Cyber Graph."""
    
    DEVICE = "DEVICE"
    SERVER = "SERVER"
    DATABASE = "DATABASE"
    USER = "USER"
    IP = "IP"
    PROCESS = "PROCESS"
    APPLICATION = "APPLICATION"
    FIREWALL = "FIREWALL"
    WORKSTATION = "WORKSTATION"
    UNKNOWN = "UNKNOWN"
    
    @classmethod
    def get_all_types(cls) -> list:
        """Get all node types as a list."""
        return [t.value for t in cls]
    
    @classmethod
    def get_type_metadata(cls) -> Dict[str, Dict[str, Any]]:
        """Get metadata for each node type."""
        return {
            cls.DEVICE.value: {
                "description": "Generic device",
                "icon": "🖥️",
                "color": "#3498db",
            },
            cls.SERVER.value: {
                "description": "Server machine",
                "icon": "🖥️",
                "color": "#2ecc71",
            },
            cls.DATABASE.value: {
                "description": "Database server",
                "icon": "🗄️",
                "color": "#e74c3c",
            },
            cls.USER.value: {
                "description": "User account",
                "icon": "👤",
                "color": "#f39c12",
            },
            cls.IP.value: {
                "description": "IP address",
                "icon": "🌐",
                "color": "#9b59b6",
            },
            cls.PROCESS.value: {
                "description": "Running process",
                "icon": "⚙️",
                "color": "#1abc9c",
            },
            cls.APPLICATION.value: {
                "description": "Application",
                "icon": "📱",
                "color": "#e67e22",
            },
            cls.FIREWALL.value: {
                "description": "Firewall device",
                "icon": "🔥",
                "color": "#e74c3c",
            },
            cls.WORKSTATION.value: {
                "description": "Workstation",
                "icon": "💻",
                "color": "#3498db",
            },
            cls.UNKNOWN.value: {
                "description": "Unknown type",
                "icon": "❓",
                "color": "#95a5a6",
            },
        }