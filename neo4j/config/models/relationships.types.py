from enum import Enum
from typing import Dict, Any

class RelationshipType(str, Enum):
    """Relationship types in the Cyber Graph"""
    
    # Network relationships
    CONNECTS_TO = "CONNECTS_TO"
    COMMUNICATES_WITH = "COMMUNICATES_WITH"
    ACCESSES = "ACCESSES"
    ROUTES_TO = "ROUTES_TO"
    DEPENDS_ON = "DEPENDS_ON"
    
    # Authentication relationships
    AUTHENTICATES_TO = "AUTHENTICATES_TO"
    LOGIN_TO = "LOGIN_TO"
    AUTHORIZED_BY = "AUTHORIZED_BY"
    
    # Process relationships
    RUNS_ON = "RUNS_ON"
    EXECUTES = "EXECUTES"
    SPAWNS = "SPAWNS"
    PARENT_OF = "PARENT_OF"
    CHILD_OF = "CHILD_OF"
    
    # Data relationships
    READS_FROM = "READS_FROM"
    WRITES_TO = "WRITES_TO"
    MODIFIES = "MODIFIES"
    DELETES = "DELETES"
    
    # Security relationships
    TRIGGERED_BY = "TRIGGERED_BY"
    RELATED_TO = "RELATED_TO"
    DETECTED_BY = "DETECTED_BY"
    ASSOCIATED_WITH = "ASSOCIATED_WITH"
    MITRE_TECHNIQUE = "MITRE_TECHNIQUE"
    
    # Attack relationships
    ATTACKED_FROM = "ATTACKED_FROM"
    COMPROMISED = "COMPROMISED"
    AFFECTED = "AFFECTED"
    LATERAL_MOVEMENT = "LATERAL_MOVEMENT"

class RelationshipProperties:
    """Standard relationship properties"""
    
    @staticmethod
    def get_common_properties() -> Dict[str, Any]:
        """Get common properties for all relationships"""
        return {
            "type": None,            # Relationship type
            "timestamp": None,       # Relationship timestamp
            "protocol": None,        # Network protocol
            "port": None,           # Port number
            "direction": None,      # Direction of communication
            "frequency": None,      # Frequency of communication
            "confidence": None,     # Confidence score (0-1)
            "description": None,    # Description
            "metadata": None,       # Additional metadata
            "created_at": None,     # Creation timestamp
            "weight": None          # Weight/importance of relationship
        }
    
    @staticmethod
    def get_network_properties() -> Dict[str, Any]:
        """Get network-specific relationship properties"""
        return {
            **RelationshipProperties.get_common_properties(),
            "bytes_sent": None,      # Bytes sent
            "bytes_received": None,  # Bytes received
            "duration": None,        # Connection duration
            "packets": None,         # Number of packets
            "bandwidth": None        # Bandwidth usage
        }
    
    @staticmethod
    def get_security_properties() -> Dict[str, Any]:
        """Get security-specific relationship properties"""
        return {
            **RelationshipProperties.get_common_properties(),
            "risk_score": None,      # Risk score (0-100)
            "severity": None,        # Severity level
            "detection_method": None, # Detection method
            "confidence_score": None, # Confidence score
            "evidence": None         # Supporting evidence
        }

class RelationshipFactory:
    """Factory for creating relationship objects"""
    
    @staticmethod
    def create_relationship(rel_type: RelationshipType, **kwargs) -> Dict[str, Any]:
        """Create a relationship with properties based on type"""
        
        base_props = {
            "type": rel_type.value,
            "timestamp": kwargs.get("timestamp", "datetime()"),
            "created_at": kwargs.get("created_at", "datetime()")
        }
        
        # Add common properties
        common = {
            "protocol": kwargs.get("protocol"),
            "port": kwargs.get("port"),
            "direction": kwargs.get("direction"),
            "frequency": kwargs.get("frequency"),
            "confidence": kwargs.get("confidence", 0.8),
            "description": kwargs.get("description"),
            "metadata": kwargs.get("metadata", {}),
            "weight": kwargs.get("weight", 1.0)
        }
        
        # Add type-specific properties
        if rel_type in [RelationshipType.CONNECTS_TO, RelationshipType.COMMUNICATES_WITH]:
            specific = {
                "bytes_sent": kwargs.get("bytes_sent"),
                "bytes_received": kwargs.get("bytes_received"),
                "duration": kwargs.get("duration"),
                "packets": kwargs.get("packets"),
                "bandwidth": kwargs.get("bandwidth")
            }
        elif rel_type in [RelationshipType.LATERAL_MOVEMENT, RelationshipType.ATTACKED_FROM]:
            specific = {
                "risk_score": kwargs.get("risk_score", 0.0),
                "severity": kwargs.get("severity"),
                "detection_method": kwargs.get("detection_method"),
                "confidence_score": kwargs.get("confidence_score", 0.0),
                "evidence": kwargs.get("evidence", [])
            }
        else:
            specific = {}
        
        return {**base_props, **common, **specific}