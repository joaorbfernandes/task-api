# app/application/ports/task_repository.py

from abc import ABC, abstractmethod

from app.modules.tasks.domain.task import Task

class TaskRepository(ABC):
    @abstractmethod
    def list_tasks(self) -> list[Task]:
        """Return all stored tasks."""

    @abstractmethod
    def get_task(self, task_id: int) -> Task | None:
        """Return a task by id or None if it does not exist."""

    @abstractmethod
    def create_task(self, task: Task) -> Task:
        """Create and persist a new task, returning the persisted domain entity."""

    @abstractmethod
    def save_task(self, task: Task) -> Task:
        """Store or replace an existing task and return it."""

    @abstractmethod
    def delete_task(self, task_id: int) -> None:
        """Delete a task by id."""