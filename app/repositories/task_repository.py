# app/repositories/task_repository.py

from abc import ABC, abstractmethod

from app.domain.entities.task import Task

class TaskRepository(ABC):
    @abstractmethod
    def list_tasks(self) -> list[Task]:
        """Return all stored tasks."""

    @abstractmethod
    def get_task(self, task_id: int) -> Task | None:
        """Return a task by id or None if it does not exist."""

    @abstractmethod
    def save_task(self, task: Task) -> Task:
        """Store or replace a task and return it."""

    @abstractmethod
    def delete_task(self, task_id: int) -> None:
        """Delete a task by id."""

    @abstractmethod
    def next_id(self) -> int:
        """Return the next available task id."""


class InMemoryTaskRepository(TaskRepository):
    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def list_tasks(self) -> list[Task]:
        """Return all tasks currently stored in memory."""
        return list(self._tasks.values())

    def get_task(self, task_id: int) -> Task | None:
        """Return a task by id or None if it does not exist."""
        return self._tasks.get(task_id)

    def save_task(self, task: Task) -> Task:
        """Store or replace a task in memory and return it."""
        self._tasks[task.id] = task
        return task

    def delete_task(self, task_id: int) -> None:
        """Delete a task from memory by id."""
        del self._tasks[task_id]

    def next_id(self) -> int:
        """Return the next available in-memory task id."""
        task_id = self._next_id
        self._next_id += 1
        return task_id


_task_repository = InMemoryTaskRepository()


def get_task_repository() -> TaskRepository:
    """Return the shared task repository instance used by the application."""
    return _task_repository