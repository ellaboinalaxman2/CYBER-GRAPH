from enum import Enum
from typing import Dict, Any, Optional

class NodeType(str, Enum):
    """Node types in the Cyber Graph"""
    
    # Device types
    DEVICE = "DEVICE"
    SERVER = "SERVER"
    WORKSTATION = "WORKSTATION"
    DATABASE = "DATABASE"
    FIREWALL = "FIREWALL"
    ROUTER = "ROUTER"
    SWITCH = "SWITCH"
    APPLICATION_SERVER = "APPLICATION_SERVER"
    WEB_SERVER = "WEB_SERVER"
    FILE_SERVER = "FILE_SERVER"
    EMAIL_SERVER = "EMAIL_SERVER"
    DOMAIN_CONTROLLER = "DOMAIN_CONTROLLER"
    
    # Network types
    IP_ADDRESS = "IP_ADDRESS"
    NETWORK_SEGMENT = "NETWORK_SEGMENT"
    
    # User/Process types
    USER = "USER"
    PROCESS = "PROCESS"
    SERVICE = "SERVICE"
    APPLICATION = "APPLICATION"
    
    # Security types
    ALERT = "ALERT"
    INCIDENT = "INCIDENT"
    ATTACK_PATTERN = "ATTACK_PATTERN"
    MITRE_TECHNIQUE = "MITRE_TECHNIQUE"
    
    # Unknown
    UNKNOWN = "UNKNOWN"

class NodeProperties:
    """Standard node properties"""
    
    @staticmethod
    def get_common_properties() -> Dict[str, Any]:
        """Get common properties for all nodes"""
        return {
            "id": None,              # Unique identifier
            "name": None,            # Display name
            "type": None,            # Node type
            "hostname": None,        # Hostname
            "ip_address": None,      # IP address
            "os": None,              # Operating system
            "os_version": None,      # OS version
            "status": None,          # Node status
            "criticality": None,     # Criticality level (1-5)
            "description": None,     # Description
            "created_at": None,      # Creation timestamp
            "updated_at": None,      # Last update timestamp
            "metadata": None         # Additional metadata
        }
    
    @staticmethod
    def get_server_properties() -> Dict[str, Any]:
        """Get server-specific properties"""
        return {
            **NodeProperties.get_common_properties(),
            "server_role": None,     # Server role
            "services": None,        # Running services
            "ports": None,           # Open ports
            "cpu_cores": None,       # CPU cores
            "memory_gb": None,       # Memory in GB
            "storage_gb": None       # Storage in GB
        }
    
    @staticmethod
    def get_workstation_properties() -> Dict[str, Any]:
        """Get workstation-specific properties"""
        return {
            **NodeProperties.get_common_properties(),
            "user": None,            # Primary user
            "department": None,      # Department
            "last_login": None,      # Last login time
            "software": None         # Installed software
        }
    
    @staticmethod
    def get_database_properties() -> Dict[str, Any]:
        """Get database-specific properties"""
        return {
            **NodeProperties.get_common_properties(),
            "db_type": None,         # Database type
            "db_version": None,      # Database version
            "tables": None,          # Tables count
            "size_gb": None,         # Size in GB
            "sensitive_data": None   # Contains sensitive data
        }

class NodeFactory:
    """Factory for creating node objects"""
    
    @staticmethod
    def create_node(node_type: NodeType, **kwargs) -> Dict[str, Any]:
        """Create a node with properties based on type"""
        
        base_props = {
            "type": node_type.value,
            "created_at": kwargs.get("created_at", "datetime()"),
            "updated_at": kwargs.get("updated_at", "datetime()")
        }
        
        # Add common properties
        common = {
            "id": kwargs.get("id"),
            "name": kwargs.get("name"),
            "hostname": kwargs.get("hostname"),
            "ip_address": kwargs.get("ip_address"),
            "os": kwargs.get("os"),
            "os_version": kwargs.get("os_version"),
            "status": kwargs.get("status", "active"),
            "criticality": kwargs.get("criticality", 3),
            "description": kwargs.get("description"),
            "metadata": kwargs.get("metadata", {})
        }
        
        # Add type-specific properties
        if node_type in [NodeType.SERVER, NodeType.WEB_SERVER, NodeType.FILE_SERVER, 
                         NodeType.EMAIL_SERVER, NodeType.APPLICATION_SERVER]:
            specific = {
                "server_role": kwargs.get("server_role"),
                "services": kwargs.get("services", []),
                "ports": kwargs.get("ports", []),
                "cpu_cores": kwargs.get("cpu_cores"),
                "memory_gb": kwargs.get("memory_gb"),
                "storage_gb": kwargs.get("storage_gb")
            }
        elif node_type == NodeType.DATABASE:
            specific = {
                "db_type": kwargs.get("db_type"),
                "db_version": kwargs.get("db_version"),
                "tables": kwargs.get("tables"),
                "size_gb": kwargs.get("size_gb"),
                "sensitive_data": kwargs.get("sensitive_data", False)
            }
        elif node_type in [NodeType.WORKSTATION, NodeType.DEVICE]:
            specific = {
                "user": kwargs.get("user"),
                "department": kwargs.get("department"),
                "last_login": kwargs.get("last_login"),
                "software": kwargs.get("software", [])
            }
        else:
            specific = {}
        
        return {**base_props, **common, **specific}