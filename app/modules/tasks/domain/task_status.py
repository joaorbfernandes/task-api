# app/domain/enums/task_status.py

from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    @property
    def display_name(self) -> str:
        return self.value.replace("_", " ").upper()