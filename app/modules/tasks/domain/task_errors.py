class TaskDomainError(Exception):
    """Base error for task domain rule violations."""


class InvalidTaskStatusTransitionError(TaskDomainError):
    """Raised when a task tries to move to an invalid status."""


class TaskNotEditableError(TaskDomainError):
    """Raised when a task cannot be edited in its current state."""


class InvalidTaskDueDateError(TaskDomainError):
    """Raised when a task due date violates domain rules."""