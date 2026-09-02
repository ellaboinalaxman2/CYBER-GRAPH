"""Tests for health check endpoints."""

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_health_check(self):
        """Test the main health endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["service"] == "ingestion-engine"
    
    def test_readiness_check(self):
        """Test the readiness endpoint."""
        response = client.get("/api/v1/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["ready"] is True
        assert "timestamp" in data
    
    def test_liveness_check(self):
        """Test the liveness endpoint."""
        response = client.get("/api/v1/health/live")
        assert response.status_code == 200
        data = response.json()
        assert data["alive"] is True
        assert "timestamp" in data
    
    def test_root_endpoint(self):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Cyber-Graph-Ingestion"
        assert data["status"] == "running"
        assert "version" in data
        assert "environment" in data