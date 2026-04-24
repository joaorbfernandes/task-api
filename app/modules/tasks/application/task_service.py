from datetime import UTC, datetime

from app.modules.tasks.application.task_dtos import TaskInput as TaskInputDTO, PatchTaskInput as PatchTaskInputDTO
from app.modules.tasks.application.task_repository import TaskRepository
from app.application.unit_of_work import UnitOfWork
from app.modules.tasks.domain.task import Task


class TaskNotFoundError(Exception):
    """Raised when a task does not exist."""


class TaskService:
    def __init__(self, repository: TaskRepository, uow: UnitOfWork) -> None:
        self._repository = repository
        self._uow = uow

    def _current_timestamp(self) -> datetime:
        """Return the current UTC timestamp without microseconds."""
        return datetime.now(UTC).replace(microsecond=0)

    def _apply_update(self, task: Task, task_input: TaskInputDTO) -> tuple[Task, bool]:
        """Apply a full update to an existing task and persist it if changed."""
        changed = task.update(
            title=task_input.title,
            description=task_input.description,
            status=task_input.status,
            due_date=task_input.due_date,
            is_blocked=task_input.is_blocked,
        )


        if not changed:
            return task, False

        task.mark_updated(self._current_timestamp())
        persisted_task = self._repository.save_task(task)
        return persisted_task, True

    def list_tasks(self) -> list[Task]:
        """Return all tasks currently stored."""
        return self._repository.list_tasks()


    def create_task(self, task_input: TaskInputDTO) -> Task:
        """Create a new task through the repository contract."""
        try:
            new_task = Task.create(
                title=task_input.title,
                description=task_input.description,
                status=task_input.status,
                due_date=task_input.due_date,
                is_blocked=task_input.is_blocked,
                created_at=self._current_timestamp()
            )

            created_task = self._repository.create_task(new_task)
            self._uow.commit()
            return created_task

        except Exception:
            self._uow.rollback()
            raise

    def get_task(self, task_id: int) -> Task:
        """Return a task by id or raise TaskNotFoundError if it does not exist."""
        current_task = self._repository.get_task(task_id)

        if current_task is None:
            raise TaskNotFoundError("Task not found")

        return current_task

    def update_task(self, task_id: int, task_input: TaskInputDTO) -> Task:
        """Fully replace task data using the provided application input."""
        try:
            current_task = self.get_task(task_id)
            updated_task, changed = self._apply_update(current_task, task_input)

            if changed:
                self._uow.commit()

            return updated_task

        except Exception:
            self._uow.rollback()
            raise

    def patch_task(self, task_id: int, task_input: PatchTaskInputDTO) -> Task:
        """Partially update task data using the provided application input."""
        try:
            current_task = self.get_task(task_id)

            full_input = TaskInputDTO(
                title=task_input.title if task_input.title_provided else current_task.title,
                description=task_input.description if task_input.description_provided else current_task.description,
                status=task_input.status if task_input.status_provided else current_task.status,
                due_date=task_input.due_date if task_input.due_date_provided else current_task.due_date,
                is_blocked=task_input.is_blocked if task_input.is_blocked_provided else current_task.is_blocked,
            )

            updated_task, changed = self._apply_update(current_task, full_input)

            if changed:
                self._uow.commit()

            return updated_task

        except Exception:
            self._uow.rollback()
            raise


    def delete_task(self, task_id: int) -> None:
        """Delete a task by id or raise TaskNotFoundError if it does not exist."""
        try:
            self.get_task(task_id)
            self._repository.delete_task(task_id)
            self._uow.commit()

        except Exception:
            self._uow.rollback()
            raise