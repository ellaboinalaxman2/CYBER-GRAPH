"""Relationship types for Neo4j graph."""

from enum import Enum
from typing import Dict, Any


class RelationshipType(str, Enum):
    """Relationship types in the Cyber Graph."""
    
    CONNECTS_TO = "CONNECTS_TO"
    ACCESSES = "ACCESSES"
    AUTHENTICATES_TO = "AUTHENTICATES_TO"
    RUNS = "RUNS"
    COMMUNICATES_WITH = "COMMUNICATES_WITH"
    DEPENDS_ON = "DEPENDS_ON"
    TALKS_TO = "TALKS_TO"
    ATTACKS = "ATTACKS"
    COMPROMISES = "COMPROMISES"
    LATERAL_MOVEMENT = "LATERAL_MOVEMENT"
    
    @classmethod
    def get_all_types(cls) -> list:
        """Get all relationship types as a list."""
        return [t.value for t in cls]
    
    @classmethod
    def get_type_metadata(cls) -> Dict[str, Dict[str, Any]]:
        """Get metadata for each relationship type."""
        return {
            cls.CONNECTS_TO.value: {
                "description": "Network connection between devices",
                "color": "#3498db",
                "direction": "directed",
            },
            cls.ACCESSES.value: {
                "description": "Access to a resource",
                "color": "#2ecc71",
                "direction": "directed",
            },
            cls.AUTHENTICATES_TO.value: {
                "description": "Authentication to a system",
                "color": "#f39c12",
                "direction": "directed",
            },
            cls.RUNS.value: {
                "description": "Runs a process",
                "color": "#1abc9c",
                "direction": "directed",
            },
            cls.COMMUNICATES_WITH.value: {
                "description": "Communication between entities",
                "color": "#9b59b6",
                "direction": "undirected",
            },
            cls.DEPENDS_ON.value: {
                "description": "Depends on another entity",
                "color": "#e67e22",
                "direction": "directed",
            },
            cls.TALKS_TO.value: {
                "description": "Talking to another entity",
                "color": "#3498db",
                "direction": "undirected",
            },
            cls.ATTACKS.value: {
                "description": "Attack from one entity to another",
                "color": "#e74c3c",
                "direction": "directed",
            },
            cls.COMPROMISES.value: {
                "description": "Compromises another entity",
                "color": "#c0392b",
                "direction": "directed",
            },
            cls.LATERAL_MOVEMENT.value: {
                "description": "Lateral movement in attack",
                "color": "#e74c3c",
                "direction": "directed",
            },
        }