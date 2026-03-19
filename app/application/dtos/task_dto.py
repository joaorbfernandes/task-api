# app/application/dtos/task_dto.py

from dataclasses import dataclass
from datetime import date

from app.domain.enums.task_status import TaskStatus


@dataclass(slots=True)
class CreateTaskInput:
    title: str
    description: str | None = None
    due_date: date | None = None
    is_blocked: bool = False


@dataclass(slots=True)
class UpdateTaskInput:
    title: str
    description: str | None
    status: TaskStatus
    due_date: date | None
    is_blocked: bool