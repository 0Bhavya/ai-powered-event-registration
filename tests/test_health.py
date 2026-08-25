"""Phase 1 health check tests."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["status"] == "healthy"


def test_landing_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "Powered by Intelligence" in response.text


def test_stats_api():
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "total_registrations" in data["data"]
