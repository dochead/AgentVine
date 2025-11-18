"""Tests for about endpoint."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_about_returns_200() -> None:
    """Test that about endpoint returns 200 status."""
    response = client.get("/about")
    assert response.status_code == 200


def test_about_returns_correct_structure() -> None:
    """Test that about endpoint returns expected response structure."""
    response = client.get("/about")
    data = response.json()

    assert "name" in data
    assert "version" in data
    assert "description" in data


def test_about_returns_correct_values() -> None:
    """Test that about endpoint returns correct application information."""
    response = client.get("/about")
    data = response.json()

    assert data["name"] == "AgentVine"
    assert data["version"] == "0.01"
    assert data["description"] == "Event-driven autonomous development system"


def test_about_has_correct_content_type() -> None:
    """Test that about endpoint returns JSON content type."""
    response = client.get("/about")
    assert response.headers["content-type"] == "application/json"
