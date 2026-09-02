"""Custom exceptions for Member 4 - Database Engine."""

from typing import Optional, Dict, Any


class DatabaseError(Exception):
    """Base exception for database errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class MongoDBError(DatabaseError):
    """Raised when MongoDB operations fail."""
    pass


class DocumentNotFoundError(MongoDBError):
    """Raised when a document is not found."""
    pass


class Neo4jError(DatabaseError):
    """Raised when Neo4j operations fail."""
    pass


class NodeNotFoundError(Neo4jError):
    """Raised when a node is not found."""
    pass


class RelationshipNotFoundError(Neo4jError):
    """Raised when a relationship is not found."""
    pass


class ValidationError(DatabaseError):
    """Raised when data validation fails."""
    pass