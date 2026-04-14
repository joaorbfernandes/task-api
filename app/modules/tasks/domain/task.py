from datetime import date, datetime
from typing import Self

from app.modules.tasks.domain.task_errors import (
    InvalidTaskDueDateError,
    InvalidTaskStatusTransitionError,
    InvalidTaskTitleError,
    TaskNotEditableError,
)
from app.modules.tasks.domain.task_status import TaskStatus


EDITABLE_STATUSES = {TaskStatus.PENDING, TaskStatus.IN_PROGRESS}
DUE_DATE_REQUIRED_STATUSES = {TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED}

STATUS_TRANSITIONS = {
    TaskStatus.PENDING: {TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED},
    TaskStatus.IN_PROGRESS: {TaskStatus.PENDING, TaskStatus.COMPLETED, TaskStatus.CANCELLED},
    TaskStatus.COMPLETED: set(),
    TaskStatus.CANCELLED: set(),
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
        is_blocked: bool = False,
    ) -> None:
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
    
    @classmethod
    def create(
        cls,
        *,
        title: str,
        description: str | None,
        status: TaskStatus,
        due_date: date | None,
        is_blocked: bool,
        created_at: datetime
    ) -> Self:
        validated_title = cls._validate_title(title)
        cls._validate_final_state(status=status, due_date=due_date, is_blocked=is_blocked)
        return cls(
            id=None,
            title=validated_title,
            description=description,
            status=status,
            due_date=due_date,
            is_blocked=is_blocked,
            created_at=created_at
        )

    def _ensure_editable(self) -> None:
        if self.status not in EDITABLE_STATUSES:
            raise TaskNotEditableError(
                f"Task is not editable in its current status - [{self.status.display_name}]"
            )

    @staticmethod
    def _validate_title(title: str) -> str:
        validated_title = title.strip()

        if not validated_title:
            raise InvalidTaskTitleError("Task title cannot be empty")

        if len(validated_title) < 3:
            raise InvalidTaskTitleError("Task title must be at least 3 characters long")

        if len(validated_title) > 120:
            raise InvalidTaskTitleError("Task title must be at most 120 characters long")

        return validated_title

    @staticmethod
    def _validate_due_date(*, status: TaskStatus, due_date: date | None) -> None:
        if due_date is not None and due_date < date.today():
            raise InvalidTaskDueDateError("Due date can't be earlier than the current date")

        if status in DUE_DATE_REQUIRED_STATUSES and due_date is None:
            raise InvalidTaskDueDateError(
                f"Due date is required for {status.display_name} tasks"
            )

    @staticmethod
    def _validate_blocked_state(*, status: TaskStatus, is_blocked: bool) -> None:
        if not is_blocked:
            return

        if status == TaskStatus.COMPLETED:
            raise InvalidTaskStatusTransitionError("Task can't be blocked in the COMPLETED state")

    def _validate_blocked_transition(
        self,
        *,
        target_status: TaskStatus,
        target_is_blocked: bool,
    ) -> None:
        if not self.is_blocked:
            return

        if self.status == TaskStatus.PENDING:
            if target_status == TaskStatus.IN_PROGRESS and target_is_blocked:
                raise InvalidTaskStatusTransitionError("Can't change task status from PENDING to IN PROGRESS because the task is BLOCKED")
            return

        if self.status == TaskStatus.IN_PROGRESS:
            if target_status == TaskStatus.COMPLETED and target_is_blocked:
                raise InvalidTaskStatusTransitionError("Can't change task status from IN PROGRESS to COMPLETED because the task is BLOCKED")

    @classmethod
    def _validate_final_state(
        cls,
        *,
        status: TaskStatus,
        due_date: date | None,
        is_blocked: bool,
    ) -> None:
        cls._validate_due_date(status=status, due_date=due_date)
        cls._validate_blocked_state(status=status, is_blocked=is_blocked)

    def _validate_status_transition(self, *, target_status: TaskStatus) -> None:
        if self.status == target_status:
            return

        allowed_statuses = STATUS_TRANSITIONS.get(self.status, set())

        if target_status not in allowed_statuses:
            raise InvalidTaskStatusTransitionError(
                f"Can't change task status from "
                f"{self.status.display_name} to {target_status.display_name}"
            )

    def update(
        self,
        *,
        title: str,
        description: str | None,
        status: TaskStatus,
        due_date: date | None,
        is_blocked: bool,
    ) -> bool:
        self._ensure_editable()

        validated_title = self._validate_title(title)

        changed = (
            self.title != validated_title
            or self.description != description
            or self.status != status
            or self.due_date != due_date
            or self.is_blocked != is_blocked
        )

        if not changed:
            return False

        if self.status != status:
            self._validate_status_transition(target_status=status)
            self._validate_blocked_transition(
                target_status=status,
                target_is_blocked=is_blocked,
            )

        self._validate_final_state(
            status=status,
            due_date=due_date,
            is_blocked=is_blocked,
        )

        self._title = validated_title
        self._description = description
        self._status = status
        self._due_date = due_date
        self._is_blocked = is_blocked

        return True

    def mark_updated(self, timestamp: datetime) -> None:
        self._updated_at = timestamp

    def assign_id(self, new_id: int) -> None:
        if self.id is not None:
            raise ValueError("Task id is already assigned")

        self._id = new_id