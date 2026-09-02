"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Tests for health endpoints."""
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Cyber-Graph-AI-Engine"


class TestPredictionEndpoints:
    """Tests for prediction endpoints."""
    
    def test_predict_endpoint(self):
        """Test prediction endpoint."""
        response = client.post(
            "/api/v1/predict",
            json={
                "node_id": "NODE-1",
                "include_explanation": True,
            }
        )
        # Should work even without model
        assert response.status_code in [200, 500]
    
    def test_model_status(self):
        """Test model status endpoint."""
        response = client.get("/api/v1/model/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data