# api/schemas/task.py

from datetime import date, datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints, model_validator


TitleStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=120)]
DescStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskCreate(BaseModel):
    """Schema used to create a new task."""
    model_config = ConfigDict(extra="forbid")

    title: TitleStr
    description: DescStr | None = None
    due_date: date | None = None


class TaskResponse(BaseModel):
    """Schema returned by task endpoints."""
    id: int
    title: TitleStr
    status: TaskStatus
    description: DescStr | None = None
    due_date: date | None = None
    created_at: datetime
    updated_at: datetime | None = None


class TaskUpdate(BaseModel):
    """Schema used for full task replacement."""
    model_config = ConfigDict(extra="forbid")

    title: TitleStr
    description: DescStr | None
    status: TaskStatus
    due_date: date | None


class TaskPatch(BaseModel):
    """Schema used for partial task updates."""
    model_config = ConfigDict(extra="forbid")

    title: TitleStr | None = None
    description: DescStr | None = None
    status: TaskStatus | None = None
    due_date: date | None = None

    @model_validator(mode="after")
    def validate_patch_non_nullable_fields(self):
        if "title" in self.model_fields_set and self.title is None:
            raise ValueError("title cannot be null")

        if "status" in self.model_fields_set and self.status is None:
            raise ValueError("status cannot be null")

        return self