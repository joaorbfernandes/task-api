# app/infrastructure/dependencies.py

from app.application.ports.task_repository import TaskRepository
from app.application.services.task_service import TaskService
from app.infrastructure.repositories.in_memory_task_repository import InMemoryTaskRepository


# Shared in-memory repository so application state survives across requests.
_task_repository = InMemoryTaskRepository()


def get_task_repository() -> TaskRepository:
    """Return the repository instance used by the application."""
    return _task_repository


def get_task_service() -> TaskService:
    """Return the task service instance used by the API layer."""
    repository = get_task_repository()
    return TaskService(repository=repository)