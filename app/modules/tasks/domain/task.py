# app/domain/entities/task.py

from datetime import date, datetime

from app.modules.tasks.domain.task_status import TaskStatus
from app.modules.tasks.domain.task_errors import InvalidTaskDueDateError, InvalidTaskStatusTransitionError, TaskNotEditableError


STATUS_TRANSITIONS = {
    TaskStatus.PENDING: {TaskStatus.PENDING, TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED},
    TaskStatus.IN_PROGRESS: {TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED, TaskStatus.CANCELLED},
    TaskStatus.COMPLETED: set(),
    TaskStatus.CANCELLED: set(),
}

BLOCKED_STATUS_EXCEPTIONS = {
    TaskStatus.PENDING: {TaskStatus.IN_PROGRESS},
    TaskStatus.IN_PROGRESS: {TaskStatus.CANCELLED}
}

class Task:
    def __init__(
        self,
        *,
        id: int,
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
    def id(self) -> int:
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
        if status in (TaskStatus.COMPLETED, TaskStatus.CANCELLED) and is_blocked:
            raise InvalidTaskStatusTransitionError("Task cannot be blocked in the target state")

        if due_date is not None and due_date < date.today():
            raise InvalidTaskDueDateError("Due date cannot be earlier than the current date")

        if status == TaskStatus.IN_PROGRESS and due_date is None:
            raise InvalidTaskDueDateError("Due date is required for IN_PROGRESS tasks")

    def _validate_target_status_change(self, new_status: TaskStatus) -> None:
        if self._status == new_status:
            return

        if self._status in (TaskStatus.COMPLETED, TaskStatus.CANCELLED):
            raise InvalidTaskStatusTransitionError(
                "Task cannot change status from its current terminal state"
            )

        if self._is_blocked:
            allowed_targets = BLOCKED_STATUS_EXCEPTIONS.get(self._status, set())
            if new_status not in allowed_targets:
                raise InvalidTaskStatusTransitionError(
                    "Blocked tasks cannot change status in the requested way"
                )
            return

        allowed_targets = STATUS_TRANSITIONS.get(self._status, set())
        if new_status not in allowed_targets:
            raise InvalidTaskStatusTransitionError("Invalid task status transition")

    def rename(self, new_title: str) -> bool:
        if self._title == new_title:
            return False

        self._check_editable()
        self._title = new_title
        return True

    def change_description(self, new_description: str | None) -> bool:
        if self._description == new_description:
            return False

        self._check_editable()
        self._description = new_description
        return True

    def change_due_date(self, new_due_date: date | None) -> bool:
        if self._due_date == new_due_date:
            return False

        self._check_editable()
        self._validate_state(status=self._status, due_date=new_due_date, is_blocked=self._is_blocked)

        self._due_date = new_due_date
        return True

    def block(self) -> bool:
        if self._is_blocked:
            return False
        
        self._check_editable()

        if self._status not in (TaskStatus.PENDING, TaskStatus.IN_PROGRESS):
            raise InvalidTaskStatusTransitionError(
                "Task cannot be blocked in its current state"
            )

        self._is_blocked = True
        return True

    def unblock(self) -> bool:
        if not self._is_blocked:
            return False

        self._check_editable()

        self._is_blocked = False
        return True

    def change_status(self, new_status: TaskStatus) -> bool:
        if self._status == new_status:
            return False

        self._check_editable()

        self._validate_target_status_change(new_status)

        target_is_blocked = self._is_blocked
        if self._is_blocked and new_status in BLOCKED_STATUS_EXCEPTIONS.get(self._status, set()):
            target_is_blocked = False

        self._validate_state(status=new_status, due_date=self._due_date, is_blocked=target_is_blocked)

        self._status = new_status
        self._is_blocked = target_is_blocked
        return True

    def update(self, *, title: str, description: str | None, status: TaskStatus, due_date: date | None, is_blocked: bool) -> bool:

        changed = False

        changed = self.rename(title) or changed
        changed = self.change_description(description) or changed
        changed = self.change_due_date(due_date) or changed
        changed = self.change_status(status) or changed

        if is_blocked:
            changed = self.block() or changed
        else:
            changed = self.unblock() or changed

        return changed

    def mark_updated(self, timestamp: datetime) -> None:
        self._updated_at = timestamp