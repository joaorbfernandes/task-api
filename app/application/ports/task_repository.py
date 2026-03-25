# app/application/ports/task_repository.py

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime

from app.domain.entities.task import Task
from app.domain.enums.task_status import TaskStatus


@dataclass(frozen=True, slots=True)
class TaskCreateData:
    title: str
    description: str | None
    status: TaskStatus
    due_date: date | None
    created_at: datetime
    is_blocked: bool = False


class TaskRepository(ABC):
    @abstractmethod
    def list_tasks(self) -> list[Task]:
        """Return all stored tasks."""

    @abstractmethod
    def get_task(self, task_id: int) -> Task | None:
        """Return a task by id or None if it does not exist."""

    @abstractmethod
    def create_task(self, task_input: TaskCreateData) -> Task:
        """Create and persist a new task, returning the persisted domain entity."""

    @abstractmethod
    def save_task(self, task: Task) -> Task:
        """Store or replace an existing task and return it."""

    @abstractmethod
    def delete_task(self, task_id: int) -> None:
        """Delete a task by id."""