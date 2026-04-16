# app/infrastructure/repositories/in_memory_task_repository.py

from app.modules.tasks.application.task_repository import TaskRepository
from app.modules.tasks.domain.task import Task


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

    def create_task(self, task: Task) -> Task:
        task.assign_id(self._next_id)
        self._tasks[self._next_id] = task
        self._next_id += 1
        return task

    def save_task(self, task: Task) -> Task:
        """Store or replace a task in memory and return it."""
        if task.id is None:
            raise ValueError("Cannot save a task without an id")
        self._tasks[task.id] = task
        return task

    def delete_task(self, task_id: int) -> None:
        """Delete a task from memory by id."""
        del self._tasks[task_id]