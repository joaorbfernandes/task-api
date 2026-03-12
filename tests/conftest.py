# tests/conftest.py

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.routers import tasks

from app.schemas.task import TaskResponse


# ----------------------------------------
# Test client
# ----------------------------------------

@pytest.fixture
def client():
    """
    Provides a TestClient instance for API tests.

    Also resets the in-memory task storage before
    and after each test to ensure isolation.
    """

    # reset storage before test
    tasks.tasks.clear()
    tasks.next_id = 1

    with TestClient(app) as client:
        yield client

    # reset storage after test
    tasks.tasks.clear()
    tasks.next_id = 1


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
    def _parse(data):
        if isinstance(data, list):
            return [TaskResponse.model_validate(item) for item in data]
        if isinstance(data, dict):
            return TaskResponse.model_validate(data)

        raise TypeError(f"Unexpected response format: {type(data)}")

    return _parse