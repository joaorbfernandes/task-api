from dataclasses import dataclass

from app.modules.tasks.domain.task_errors import InvalidTaskTitleError


@dataclass(frozen=True)
class TaskTitle:
    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise InvalidTaskTitleError("Task title must be a string")

        validated_value = self.value.strip()

        if not validated_value:
            raise InvalidTaskTitleError("Task title cannot be empty")

        if len(validated_value) < 3:
            raise InvalidTaskTitleError("Task title must be at least 3 characters long")

        if len(validated_value) > 120:
            raise InvalidTaskTitleError(
                "Task title must be at most 120 characters long"
            )

        object.__setattr__(self, "value", validated_value)
