# app/services/task_service.py

from datetime import UTC, date, datetime
from typing import TypedDict

from app.schemas.task import TaskCreate, TaskPatch, TaskStatus, TaskUpdate


class TaskData(TypedDict):
    id: int
    title: str
    description: str | None
    status: TaskStatus
    due_date: date | None
    created_at: datetime
    updated_at: datetime | None


class TaskNotFoundError(Exception):
    """Raised when a task does not exist."""


class TaskService:
    def __init__(self) -> None:
        self._tasks: dict[int, TaskData] = {}
        self._next_id: int = 1

    def _current_timestamp(self) -> datetime:
        """Return the current UTC timestamp without microseconds."""
        return datetime.now(UTC).replace(microsecond=0)

    def _build_task_data(self, task_id: int, task: TaskCreate) -> TaskData:
        """Build the internal task data structure for a new task."""
        return {
            "id": task_id,
            "title": task.title,
            "description": task.description,
            "status": TaskStatus.PENDING,
            "due_date": task.due_date,
            "created_at": self._current_timestamp(),
            "updated_at": None,
        }

    def list_tasks(self) -> list[TaskData]:
        """Return all tasks currently stored in memory."""
        return list(self._tasks.values())

    def create_task(self, task: TaskCreate) -> TaskData:
        """Create a new task and store it in temporary in-memory state."""
        task_id = self._next_id
        new_task = self._build_task_data(task_id, task)
        self._tasks[task_id] = new_task
        self._next_id += 1

        return new_task

    def get_task(self, task_id: int) -> TaskData:
        """Return a task by id or raise TaskNotFoundError if it does not exist."""
        task = self._tasks.get(task_id)

        if task is None:
            raise TaskNotFoundError("Task not found")

        return task

    def update_task(self, task_id: int, task_update: TaskUpdate) -> TaskData:
        """Fully replace task data using the validated PUT payload."""
        task = self.get_task(task_id)

        task["title"] = task_update.title
        task["description"] = task_update.description
        task["status"] = task_update.status
        task["due_date"] = task_update.due_date
        task["updated_at"] = self._current_timestamp()

        return task

    def patch_task(self, task_id: int, task_patch: TaskPatch) -> TaskData:
        """Partially update task fields that were explicitly provided."""
        task = self.get_task(task_id)

        if "title" in task_patch.model_fields_set:
            task["title"] = task_patch.title

        if "description" in task_patch.model_fields_set:
            task["description"] = task_patch.description

        if "status" in task_patch.model_fields_set:
            task["status"] = task_patch.status

        if "due_date" in task_patch.model_fields_set:
            task["due_date"] = task_patch.due_date

        task["updated_at"] = self._current_timestamp()

        return task

    def delete_task(self, task_id: int) -> None:
        """Delete a task by id or raise TaskNotFoundError if it does not exist."""
        self.get_task(task_id)
        del self._tasks[task_id]


_task_service = TaskService()


def get_task_service() -> TaskService:
    """Return the shared task service instance used by the API layer."""
    return _task_service