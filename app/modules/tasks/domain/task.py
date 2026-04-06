# app/domain/entities/task.py

from datetime import date, datetime

from app.modules.tasks.domain.task_status import TaskStatus
from app.modules.tasks.domain.task_errors import InvalidTaskDueDateError, InvalidTaskStatusTransitionError, TaskNotEditableError


STATUS_TRANSITIONS = {
    TaskStatus.PENDING: {TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED},
    TaskStatus.IN_PROGRESS: {TaskStatus.PENDING, TaskStatus.COMPLETED, TaskStatus.CANCELLED},
    TaskStatus.COMPLETED: set(),
    TaskStatus.CANCELLED: set()
}

BLOCKED_STATUS_EXCEPTIONS = {
    TaskStatus.PENDING: {TaskStatus.CANCELLED},
    TaskStatus.IN_PROGRESS: {TaskStatus.PENDING, TaskStatus.CANCELLED}
}

class Task:
    def __init__(
        self,
        *,
        id: int | None,
        title: str,
        description: str | None,
        status: TaskStatus,
        due_date: date | None,
        created_at: datetime,
        updated_at: datetime | None = None,
        is_blocked: bool = False
    ) -> None:
        self._validate_state(status=status, due_date=due_date, is_blocked=is_blocked)

        self._id = id
        self._title = title
        self._description = description
        self._status = status
        self._due_date = due_date
        self._created_at = created_at
        self._updated_at = updated_at
        self._is_blocked = is_blocked

    @property
    def id(self) -> int | None:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @property
    def description(self) -> str | None:
        return self._description

    @property
    def status(self) -> TaskStatus:
        return self._status

    @property
    def due_date(self) -> date | None:
        return self._due_date

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime | None:
        return self._updated_at

    @property
    def is_blocked(self) -> bool:
        return self._is_blocked

    def _check_editable(self) -> None:
        if self._status in (TaskStatus.COMPLETED, TaskStatus.CANCELLED):
            raise TaskNotEditableError("Task is not editable in its current state")

    @staticmethod
    def _validate_state(*, status: TaskStatus, due_date: date | None, is_blocked: bool) -> None:
        if due_date is not None and due_date < date.today():
            raise InvalidTaskDueDateError("Due date cannot be earlier than the current date")

        if status in (TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED) and due_date is None:
            raise InvalidTaskDueDateError(f"Due date is required for {status.display_name} tasks")

        if status == TaskStatus.COMPLETED and is_blocked:
            raise InvalidTaskStatusTransitionError("Task cannot be blocked in the COMPLETED state")
        
    def _validate_target_status_change(self, new_status: TaskStatus) -> None:
        if self._status == new_status:
            return

        rules = STATUS_TRANSITIONS
        if self._is_blocked:
            rules = BLOCKED_STATUS_EXCEPTIONS

        allowed_statuses = rules.get(self._status, set())

        if new_status in allowed_statuses:
            return

        message = (f"Cannot change task status from {self._status.display_name} to {new_status.d}")

        if self._is_blocked:
            message += " because the task is blocked"

        raise InvalidTaskStatusTransitionError(message)

    def rename(self, new_title: str) -> bool:
        self._check_editable()
        if self._title == new_title:
            return False

        self._title = new_title
        return True

    def change_description(self, new_description: str | None) -> bool:
        self._check_editable()
        if self._description == new_description:
            return False
        
        self._description = new_description
        return True

    def change_due_date(self, new_due_date: date | None) -> bool:
        self._check_editable()
        if self._due_date == new_due_date:
            return False

        self._validate_state(status=self._status, due_date=new_due_date, is_blocked=self._is_blocked)

        self._due_date = new_due_date
        return True

    def block(self) -> bool:
        self._check_editable()
        if self._is_blocked:
            return False
        
        if self._status not in (TaskStatus.PENDING, TaskStatus.IN_PROGRESS):
            raise InvalidTaskStatusTransitionError("Task cannot be blocked in its current state")

        self._is_blocked = True
        return True

    def unblock(self) -> bool:
        self._check_editable()
        if not self._is_blocked:
            return False

        self._is_blocked = False
        return True

    def change_status(self, new_status: TaskStatus) -> bool:
        self._check_editable()
        if self._status == new_status:
            return False

        self._validate_target_status_change(new_status)

        self._validate_state(status=new_status, due_date=self._due_date, is_blocked=self._is_blocked)

        self._status = new_status
        return True

    def update(self, *, title: str, description: str | None, status: TaskStatus, due_date: date | None, is_blocked: bool) -> bool:
        self._check_editable()
        changed = (
            self._title != title
            or self._description != description
            or self._status != status
            or self._due_date != due_date
            or self._is_blocked != is_blocked
        )

        if not changed:
            return False


        if self._status != status:
            rules = STATUS_TRANSITIONS
            if is_blocked:
                rules = BLOCKED_STATUS_EXCEPTIONS

            allowed_statuses = rules.get(self._status, set())

            if status not in allowed_statuses:
                message = f"Cannot change task status from {self._status.display_name} to {status.display_name}"
                if is_blocked:
                    message += " because the task is blocked"

                raise InvalidTaskStatusTransitionError(message)

        self._validate_state(status=status, due_date=due_date, is_blocked=is_blocked)

        self._title = title
        self._description = description
        self._status = status
        self._due_date = due_date
        self._is_blocked = is_blocked

        return True

    def mark_updated(self, timestamp: datetime) -> None:
        self._updated_at = timestamp
    
    def assign_id(self, new_id: int) -> None:
        if self._id is not None:
            raise ValueError("Task id is already assigned")

        self._id = new_id