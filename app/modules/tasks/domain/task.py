from datetime import date, datetime
from typing import Self

from app.modules.tasks.domain.task_policy import TaskPolicy
from app.modules.tasks.domain.task_status import TaskStatus
from app.modules.tasks.domain.task_title import TaskTitle


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
        validated_title = TaskTitle(title)

        TaskPolicy.validate_final_state(
            status=status,
            due_date=due_date,
            is_blocked=is_blocked,
        )

        self._id = id
        self._title = validated_title
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
        return self._title.value

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
        created_at: datetime,
    ) -> Self:
        return cls(
            id=None,
            title=title,
            description=description,
            status=status,
            due_date=due_date,
            is_blocked=is_blocked,
            created_at=created_at,
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
        TaskPolicy.ensure_editable(self.status)

        validated_title = TaskTitle(title)

        changed = (
            self.title != validated_title.value
            or self.description != description
            or self.status != status
            or self.due_date != due_date
            or self.is_blocked != is_blocked
        )

        if not changed:
            return False

        TaskPolicy.validate_transition(
            current_status=self.status,
            target_status=status,
            target_is_blocked=is_blocked,
        )

        TaskPolicy.validate_final_state(
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
