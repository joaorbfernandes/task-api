# app/infrastructure/repositories/in_memory_task_repository.py

from app.application.ports.task_repository import TaskCreateData, TaskRepository
from app.domain.entities.task import Task


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

    def create_task(self, task_input: TaskCreateData) -> Task:
        """Create and store a new task in memory, returning the persisted entity."""
        task = Task(
            id=self._next_id,
            title=task_input.title,
            description=task_input.description,
            status=task_input.status,
            due_date=task_input.due_date,
            created_at=task_input.created_at,
            updated_at=None,
            is_blocked=task_input.is_blocked,
        )

        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def save_task(self, task: Task) -> Task:
        """Store or replace a task in memory and return it."""
        self._tasks[task.id] = task
        return task

    def delete_task(self, task_id: int) -> None:
        """Delete a task from memory by id."""
        del self._tasks[task_id]