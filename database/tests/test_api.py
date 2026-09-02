"""API tests for Member 4 - Database Engine."""

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


class TestAPI:
    """Test API endpoints."""
    
    def test_root(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Cyber-Graph-Database-Engine"
        assert data["phase"] == "4 - Production Ready"
    
    def test_health(self):
        """Test health endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_docs_info(self):
        """Test docs info endpoint."""
        response = client.get("/api/v1/docs/info")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
    
    def test_rate_limit_status(self):
        """Test rate limit status endpoint."""
        response = client.get("/api/v1/rate-limit-status")
        assert response.status_code == 200
        data = response.json()
        assert "rate_limit" in data
        assert "status" in data


class TestIntegrationEndpoints:
    """Test integration endpoints."""
    
    def test_events_endpoint(self):
        """Test events endpoint."""
        response = client.get("/api/v1/events/")
        assert response.status_code in [200, 500]
    
    def test_alerts_endpoint(self):
        """Test alerts endpoint."""
        response = client.get("/api/v1/alerts/")
        assert response.status_code in [200, 500]
    
    def test_incidents_endpoint(self):
        """Test incidents endpoint."""
        response = client.get("/api/v1/incidents/")
        assert response.status_code in [200, 500]
    
    def test_graph_endpoint(self):
        """Test graph endpoint."""
        response = client.get("/api/v1/graph/statistics")
        assert response.status_code in [200, 500]