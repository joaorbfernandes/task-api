# tests/conftest.py

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.tasks.infrastructure.in_memory_task_repository import InMemoryTaskRepository
from app.modules.tasks.application.task_service import TaskService
from app.modules.tasks.api.task_schemas import TaskResponse
from app.modules.tasks.api.dependencies import get_task_service

class FakeUnitOfWork:
    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        pass

# ----------------------------------------
# Test client
# ----------------------------------------
@pytest.fixture
def client():
    """
    Provide a TestClient with a fresh in-memory repository and service for each test.

    This keeps API integration tests isolated and aligned with the current
    router -> service -> repository architecture.
    """
    test_repository = InMemoryTaskRepository()
    test_uow = FakeUnitOfWork()
    test_service = TaskService(repository=test_repository, uow=test_uow)

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
def create_task(client: TestClient):
    """
    Provide a helper to create tasks through the HTTP API.
    """
    def _create_task(**overrides):
        payload = {
            "title": "Test task",
            "description": "testing",
            "due_date": None,
            "status": "pending",
            "is_blocked": False,
        }

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