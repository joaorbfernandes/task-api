from datetime import date, datetime

from app.schemas.task import TaskStatus


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
    ) -> None:
        self._id = id
        self._title = title
        self._description = description
        self._status = status
        self._due_date = due_date
        self._created_at = created_at
        self._updated_at = updated_at

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

    def rename(self, new_title: str) -> bool:
        if self._title == new_title:
            return False

        self._title = new_title
        return True

    def change_description(self, new_description: str | None) -> bool:
        if self._description == new_description:
            return False

        self._description = new_description
        return True

    def change_status(self, new_status: TaskStatus) -> bool:
        if self._status == new_status:
            return False

        self._status = new_status
        return True

    def change_due_date(self, new_due_date: date | None) -> bool:
        if self._due_date == new_due_date:
            return False

        self._due_date = new_due_date
        return True

    def update(
        self,
        *,
        title: str,
        description: str | None,
        status: TaskStatus,
        due_date: date | None,
    ) -> bool:
        changed = False

        changed = self.rename(title) or changed
        changed = self.change_description(description) or changed
        changed = self.change_status(status) or changed
        changed = self.change_due_date(due_date) or changed

        return changed

    def mark_updated(self, timestamp: datetime) -> None:
        self._updated_at = timestamp