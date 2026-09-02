"""Tests for Neo4j connection."""

import pytest
from src.neo4j.connection import neo4j
from src.core.exceptions import Neo4jError


class TestNeo4jConnection:
    """Test Neo4j connection."""
    
    def test_connection(self):
        """Test Neo4j connection."""
        assert neo4j.is_connected() is True
    
    def test_health_check(self):
        """Test health check."""
        status = neo4j.health_check()
        assert status["status"] == "healthy"
        assert "node_count" in status
    
    def test_execute_query(self):
        """Test executing a query."""
        result = neo4j.execute_query("RETURN 1 as value")
        assert len(result) > 0
        assert result[0]["value"] == 1