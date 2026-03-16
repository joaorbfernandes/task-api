from datetime import UTC, datetime

from app.domain.entities.task import Task
from app.repositories.task_repository import TaskRepository, get_task_repository
from app.schemas.task import TaskCreate, TaskPatch, TaskStatus, TaskUpdate


class TaskNotFoundError(Exception):
    """Raised when a task does not exist."""


class TaskService:
    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    def _current_timestamp(self) -> datetime:
        """Return the current UTC timestamp without microseconds."""
        return datetime.now(UTC).replace(microsecond=0)

    def _build_task(self, task_id: int, task: TaskCreate) -> Task:
        """Build the internal task entity for a new task."""
        return Task(
            id=task_id,
            title=task.title,
            description=task.description,
            status=TaskStatus.PENDING,
            due_date=task.due_date,
            created_at=self._current_timestamp(),
            updated_at=None,
        )

    def list_tasks(self) -> list[Task]:
        """Return all tasks currently stored."""
        return self._repository.list_tasks()

    def create_task(self, task: TaskCreate) -> Task:
        """Create a new task and store it through the repository."""
        task_id = self._repository.next_id()
        new_task = self._build_task(task_id, task)
        return self._repository.save_task(new_task)

    def get_task(self, task_id: int) -> Task:
        """Return a task by id or raise TaskNotFoundError if it does not exist."""
        task = self._repository.get_task(task_id)

        if task is None:
            raise TaskNotFoundError("Task not found")

        return task

    def update_task(self, task_id: int, task_update: TaskUpdate) -> Task:
        """Fully replace task data using the validated PUT payload."""
        task = self.get_task(task_id)

        changed = task.update(
            title=task_update.title,
            description=task_update.description,
            status=task_update.status,
            due_date=task_update.due_date,
        )

        if changed:
            task.mark_updated(self._current_timestamp())
            return self._repository.save_task(task)

        return task

    def patch_task(self, task_id: int, task_patch: TaskPatch) -> Task:
        """Partially update task fields that were explicitly provided."""
        task = self.get_task(task_id)

        changed = False

        if "title" in task_patch.model_fields_set:
            changed = task.rename(task_patch.title) or changed

        if "description" in task_patch.model_fields_set:
            changed = task.change_description(task_patch.description) or changed

        if "status" in task_patch.model_fields_set:
            changed = task.change_status(task_patch.status) or changed

        if "due_date" in task_patch.model_fields_set:
            changed = task.change_due_date(task_patch.due_date) or changed

        if changed:
            task.mark_updated(self._current_timestamp())
            return self._repository.save_task(task)

        return task

    def delete_task(self, task_id: int) -> None:
        """Delete a task by id or raise TaskNotFoundError if it does not exist."""
        self.get_task(task_id)
        self._repository.delete_task(task_id)


def get_task_service() -> TaskService:
    """Return the task service instance used by the API layer."""
    repository = get_task_repository()
    return TaskService(repository=repository)