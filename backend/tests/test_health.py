"""Tests for health check endpoint."""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check_returns_200() -> None:
    """Test that health check endpoint returns 200 status."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_check_returns_correct_structure() -> None:
    """Test that health check returns expected response structure."""
    response = client.get("/health")
    data = response.json()

    assert "status" in data
    assert "timestamp" in data
    assert data["status"] == "healthy"


def test_health_check_timestamp_is_valid() -> None:
    """Test that health check timestamp is a valid ISO 8601 format."""
    response = client.get("/health")
    data = response.json()

    # Verify timestamp can be parsed
    timestamp = data["timestamp"]
    parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    assert isinstance(parsed, datetime)


def test_health_check_has_correct_content_type() -> None:
    """Test that health check returns JSON content type."""
    response = client.get("/health")
    assert response.headers["content-type"] == "application/json"
