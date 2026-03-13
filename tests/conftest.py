# tests/conftest.py

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.task_service import TaskService, get_task_service

from app.schemas.task import TaskResponse


# ----------------------------------------
# Test client
# ----------------------------------------

@pytest.fixture
def client():
    """
    Provides a TestClient instance for API tests.

    Overrides the task service dependency with a fresh in-memory
    TaskService instance for each test to ensure isolation.
    """
    test_service = TaskService()

    def override_get_task_service() -> TaskService:
        return test_service

    app.dependency_overrides[get_task_service] = override_get_task_service

    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()


# ----------------------------------------
# Task factory
# ----------------------------------------

@pytest.fixture
def create_task(client):
    """
    Factory fixture to easily create tasks in tests.

    Allows overriding default fields when needed.
    """

    def _create_task(**overrides):

        payload = {"title": "Test task", "description": "testing", "due_date": None}

        payload.update(overrides)

        return client.post("/tasks", json=payload)

    return _create_task

@pytest.fixture
def parse_response():
    """
    Validates API responses against the TaskResponse schema.

    Supports both single-object and list responses.
    """
    def _parse(data):
        if isinstance(data, list):
            return [TaskResponse.model_validate(item) for item in data]
        if isinstance(data, dict):
            return TaskResponse.model_validate(data)

        raise TypeError(f"Unexpected response format: {type(data)}")

    return _parse