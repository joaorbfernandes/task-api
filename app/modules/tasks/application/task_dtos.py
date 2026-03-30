# app/application/dtos/task_dto.py

from dataclasses import dataclass
from datetime import date

from app.modules.tasks.domain.task_status import TaskStatus


@dataclass(frozen=True, slots=True)
class CreateTaskInput:
    title: str
    description: str | None = None
    due_date: date | None = None
    is_blocked: bool = False


@dataclass(frozen=True, slots=True)
class UpdateTaskInput:
    title: str
    description: str | None
    status: TaskStatus
    due_date: date | None
    is_blocked: bool


@dataclass(frozen=True, slots=True)
class PatchTaskInput:
    title: str | None = None
    title_provided: bool = False

    description: str | None = None
    description_provided: bool = False

    status: TaskStatus | None = None
    status_provided: bool = False

    due_date: date | None = None
    due_date_provided: bool = False

    is_blocked: bool | None = None
    is_blocked_provided: bool = False