from datetime import date

from app.modules.tasks.domain.task_errors import (
    InvalidTaskDueDateError,
    InvalidTaskStatusTransitionError,
    TaskNotEditableError,
)
from app.modules.tasks.domain.task_status import TaskStatus


class TaskPolicy:
    EDITABLE_STATUSES = {TaskStatus.PENDING, TaskStatus.IN_PROGRESS}
    DUE_DATE_REQUIRED_STATUSES = {TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED}

    STATUS_TRANSITIONS = {
        TaskStatus.PENDING: {TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED},
        TaskStatus.IN_PROGRESS: {
            TaskStatus.PENDING,
            TaskStatus.COMPLETED,
            TaskStatus.CANCELLED,
        },
        TaskStatus.COMPLETED: set(),
        TaskStatus.CANCELLED: set(),
    }

    @classmethod
    def ensure_editable(cls, status: TaskStatus) -> None:
        if status not in cls.EDITABLE_STATUSES:
            raise TaskNotEditableError(
                f"Task is not editable in its current status - [{status.display_name}]"
            )

    @classmethod
    def validate_final_state(
        cls,
        *,
        status: TaskStatus,
        due_date: date | None,
        is_blocked: bool,
    ) -> None:
        cls._validate_due_date(status=status, due_date=due_date)
        cls._validate_blocked_state(status=status, is_blocked=is_blocked)

    @classmethod
    def validate_transition(
        cls,
        *,
        current_status: TaskStatus,
        target_status: TaskStatus,
        target_is_blocked: bool,
    ) -> None:
        if current_status == target_status:
            return

        allowed_statuses = cls.STATUS_TRANSITIONS.get(current_status, set())

        if target_status not in allowed_statuses:
            raise InvalidTaskStatusTransitionError(
                f"Can't change task status from "
                f"{current_status.display_name} to {target_status.display_name}"
            )

        cls._validate_blocked_transition(
            current_status=current_status,
            target_status=target_status,
            target_is_blocked=target_is_blocked,
        )

    @classmethod
    def _validate_due_date(
        cls,
        *,
        status: TaskStatus,
        due_date: date | None,
    ) -> None:
        if due_date is not None and due_date < date.today():
            raise InvalidTaskDueDateError(
                "Due date can't be earlier than the current date"
            )

        if status in cls.DUE_DATE_REQUIRED_STATUSES and due_date is None:
            raise InvalidTaskDueDateError(
                f"Due date is required for {status.display_name} tasks"
            )

    @staticmethod
    def _validate_blocked_state(
        *,
        status: TaskStatus,
        is_blocked: bool,
    ) -> None:
        if not is_blocked:
            return

        if status == TaskStatus.COMPLETED:
            raise InvalidTaskStatusTransitionError(
                "Task can't be blocked in the COMPLETED state"
            )

    @staticmethod
    def _validate_blocked_transition(
        *,
        current_status: TaskStatus,
        target_status: TaskStatus,
        target_is_blocked: bool,
    ) -> None:
        if current_status == TaskStatus.PENDING:
            if target_status == TaskStatus.IN_PROGRESS and target_is_blocked:
                raise InvalidTaskStatusTransitionError(
                    "Can't change task status from PENDING to IN PROGRESS because the task is BLOCKED"
                )
            return

        if current_status == TaskStatus.IN_PROGRESS:
            if target_status == TaskStatus.COMPLETED and target_is_blocked:
                raise InvalidTaskStatusTransitionError(
                    "Can't change task status from IN PROGRESS to COMPLETED because the task is BLOCKED"
                )
