# tests/factories/task.py

from datetime import date, datetime, timedelta

from app.domain.entities.task import Task
from app.domain.enums.task_status import TaskStatus


def build_task(
    *,
    task_id: int = 1,
    title: str = "Test task",
    description: str | None = "testing",
    status: TaskStatus = TaskStatus.PENDING,
    due_date: date | None = None,
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
    is_blocked: bool = False
) -> Task:
    return Task(
        id=task_id,
        title=title,
        description=description,
        status=status,
        due_date=due_date,
        created_at=created_at or datetime(2026, 3, 18, 12, 0, 0),
        updated_at=updated_at,
        is_blocked=is_blocked
    )

def future_date(days: int = 1) -> date:
    return date.today() + timedelta(days=days)
