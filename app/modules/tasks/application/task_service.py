# app/application/services/task_service.py

from datetime import UTC, datetime

from app.modules.tasks.application.task_dtos import CreateTaskInput, UpdateTaskInput, PatchTaskInput
from app.modules.tasks.application.task_repository import TaskCreateData, TaskRepository
from app.modules.tasks.domain.task import Task
from app.modules.tasks.domain.task_status import TaskStatus


class TaskNotFoundError(Exception):
    """Raised when a task does not exist."""


class TaskService:
    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    def _current_timestamp(self) -> datetime:
        """Return the current UTC timestamp without microseconds."""
        return datetime.now(UTC).replace(microsecond=0)

    def _apply_update(self, task: Task, task_update: UpdateTaskInput) -> Task:
        """Apply a full update to an existing task and persist it if changed."""
        changed = task.update(
            title=task_update.title,
            description=task_update.description,
            status=task_update.status,
            due_date=task_update.due_date,
            is_blocked=task_update.is_blocked,
        )

        if changed:
            task.mark_updated(self._current_timestamp())
            return self._repository.save_task(task)

        return task

    def list_tasks(self) -> list[Task]:
        """Return all tasks currently stored."""
        return self._repository.list_tasks()

    def create_task(self, task_input: CreateTaskInput) -> Task:
        """Create a new task through the repository contract."""
        create_data = TaskCreateData(
            title=task_input.title,
            description=task_input.description,
            status=TaskStatus.PENDING,
            due_date=task_input.due_date,
            created_at=self._current_timestamp(),
            is_blocked=task_input.is_blocked,
        )

        return self._repository.create_task(create_data)

    def get_task(self, task_id: int) -> Task:
        """Return a task by id or raise TaskNotFoundError if it does not exist."""
        task = self._repository.get_task(task_id)

        if task is None:
            raise TaskNotFoundError("Task not found")

        return task

    def update_task(self, task_id: int, task_update: UpdateTaskInput) -> Task:
        """Fully replace task data using the provided application input."""
        task = self.get_task(task_id)

        return self._apply_update(task, task_update)

    def patch_task(self, task_id: int, task_patch: PatchTaskInput) -> Task:
        """Partially update task data using the provided application input."""
        current_task = self.get_task(task_id)

        task_update = UpdateTaskInput(
            title=task_patch.title if task_patch.title_provided else current_task.title,
            description=task_patch.description if task_patch.description_provided else current_task.description,
            status=task_patch.status if task_patch.status_provided else current_task.status,
            due_date=task_patch.due_date if task_patch.due_date_provided else current_task.due_date,
            is_blocked=task_patch.is_blocked if task_patch.is_blocked_provided else current_task.is_blocked,
        )

        return self._apply_update(current_task, task_update)

    def delete_task(self, task_id: int) -> None:
        """Delete a task by id or raise TaskNotFoundError if it does not exist."""
        self.get_task(task_id)
        self._repository.delete_task(task_id)