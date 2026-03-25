# tests/unit/domain/test_task_update.py

from datetime import date, timedelta
import pytest

from tests.factories.task import build_task

from app.domain.enums.task_status import TaskStatus
from app.domain.errors.task import TaskNotEditableError, InvalidTaskStatusTransitionError, InvalidTaskDueDateError


# ----------------------------------------
# update
# ----------------------------------------

def test_update_returns_false_when_final_state_is_unchanged() -> None:
    # Arrange
    task = build_task(
        title="Task title",
        description="task description",
        status=TaskStatus.PENDING,
        due_date=None
    )

    # Act
    changed = task.update(
        title="Task title",
        description="task description",
        status=TaskStatus.PENDING,
        due_date=None,
        is_blocked=False
    )

    # Assert
    assert changed is False
    assert task.title == "Task title"
    assert task.description == "task description"
    assert task.status == TaskStatus.PENDING
    assert task.due_date is None
    assert task.is_blocked is False


def test_update_replaces_final_state_when_target_state_is_valid() -> None:
    # Arrange
    task = build_task(
        title="Old title",
        description="old description",
        status=TaskStatus.PENDING,
        due_date=None
    )

    # Act
    changed = task.update(
        title="New title",
        description="new description",
        status=TaskStatus.IN_PROGRESS,
        due_date=date(2026, 3, 25),
        is_blocked=True
    )

    # Assert
    assert changed is True
    assert task.title == "New title"
    assert task.description == "new description"
    assert task.status == TaskStatus.IN_PROGRESS
    assert task.due_date == date(2026, 3, 25)
    assert task.is_blocked is True


def test_update_allows_keeping_same_status_and_changing_other_fields() -> None:
    # Arrange
    task = build_task(
        title="Old title",
        description="old description",
        status=TaskStatus.PENDING,
        due_date=None
    )

    # Act
    changed = task.update(
        title="Updated title",
        description="updated description",
        status=TaskStatus.PENDING,
        due_date=date(2026, 3, 25),
        is_blocked=True
    )

    # Assert
    assert changed is True
    assert task.title == "Updated title"
    assert task.description == "updated description"
    assert task.status == TaskStatus.PENDING
    assert task.due_date == date(2026, 3, 25)
    assert task.is_blocked is True


def test_update_allows_pending_to_in_progress_when_final_state_is_valid() -> None:
    # Arrange
    task = build_task(
        status=TaskStatus.PENDING,
        due_date=None
    )

    # Act
    changed = task.update(
        title=task.title,
        description=task.description,
        status=TaskStatus.IN_PROGRESS,
        due_date=date(2026, 3, 25),
        is_blocked=False
    )

    # Assert
    assert changed is True
    assert task.status == TaskStatus.IN_PROGRESS
    assert task.due_date == date(2026, 3, 25)
    assert task.is_blocked is False


def test_update_allows_in_progress_to_completed() -> None:
    # Arrange
    task = build_task(status=TaskStatus.IN_PROGRESS,due_date=date(2026, 3, 25))

    # Act
    changed = task.update(
        title=task.title,
        description=task.description,
        status=TaskStatus.COMPLETED,
        due_date=date(2026, 3, 25),
        is_blocked=False
    )

    # Assert
    assert changed is True
    assert task.status == TaskStatus.COMPLETED


def test_update_allows_in_progress_to_cancelled() -> None:
    # Arrange
    task = build_task(
        status=TaskStatus.IN_PROGRESS,
        due_date=date(2026, 3, 25)
    )

    # Act
    changed = task.update(
        title=task.title,
        description=task.description,
        status=TaskStatus.CANCELLED,
        due_date=date(2026, 3, 25),
        is_blocked=False
    )

    # Assert
    assert changed is True
    assert task.status == TaskStatus.CANCELLED


def test_update_raises_when_pending_to_completed() -> None:
    # Arrange
    task = build_task(status=TaskStatus.PENDING)

    # Act / Assert
    with pytest.raises(InvalidTaskStatusTransitionError, match="Invalid task status transition"):
        task.update(
            title=task.title,
            description=task.description,
            status=TaskStatus.COMPLETED,
            due_date=None,
            is_blocked=False
        )


def test_update_raises_when_in_progress_to_pending() -> None:
    # Arrange
    task = build_task(status=TaskStatus.IN_PROGRESS, due_date=date(2026, 3, 25))

    # Act / Assert
    with pytest.raises(InvalidTaskStatusTransitionError, match="Invalid task status transition"):
        task.update(
            title=task.title,
            description=task.description,
            status=TaskStatus.PENDING,
            due_date=date(2026, 3, 25),
            is_blocked=False
        )


def test_update_raises_when_task_is_completed() -> None:
    # Arrange
    task = build_task(status=TaskStatus.COMPLETED, due_date=date(2026, 3, 25))

    # Act / Assert
    with pytest.raises(TaskNotEditableError, match="Task is not editable"):
        task.update(
            title="Updated title",
            description="updated description",
            status=TaskStatus.COMPLETED,
            due_date=date(2026, 3, 25),
            is_blocked=False
        )


def test_update_raises_when_task_is_cancelled() -> None:
    # Arrange
    task = build_task(status=TaskStatus.CANCELLED)

    # Act / Assert
    with pytest.raises(TaskNotEditableError, match="Task is not editable"):
        task.update(
            title="Updated title",
            description="updated description",
            status=TaskStatus.CANCELLED,
            due_date=None,
            is_blocked=False
        )


def test_update_raises_when_due_date_is_in_the_past() -> None:
    # Arrange
    task = build_task(status=TaskStatus.PENDING)
    past_due_date = date.today() - timedelta(days=1)

    # Act / Assert
    with pytest.raises(InvalidTaskDueDateError, match="cannot be earlier than the current date"):
        task.update(
            title=task.title,
            description=task.description,
            status=TaskStatus.PENDING,
            due_date=past_due_date,
            is_blocked=False
        )


def test_update_raises_when_in_progress_has_no_due_date() -> None:
    # Arrange
    task = build_task(status=TaskStatus.PENDING)

    # Act / Assert
    with pytest.raises(InvalidTaskDueDateError, match="required for IN_PROGRESS tasks"):
        task.update(
            title=task.title,
            description=task.description,
            status=TaskStatus.IN_PROGRESS,
            due_date=None,
            is_blocked=False
        )


def test_update_raises_when_completed_target_state_is_blocked() -> None:
    # Arrange
    task = build_task(status=TaskStatus.IN_PROGRESS, due_date=date(2026, 3, 25))

    # Act / Assert
    with pytest.raises(TaskNotEditableError, match="Task is not editable in its current state"):
        task.update(
            title=task.title,
            description=task.description,
            status=TaskStatus.COMPLETED,
            due_date=date(2026, 3, 25),
            is_blocked=True
        )


def test_update_raises_when_cancelled_target_state_is_blocked() -> None:
    # Arrange
    task = build_task(status=TaskStatus.IN_PROGRESS, due_date=date(2026, 3, 25))

    # Act / Assert
    with pytest.raises(TaskNotEditableError, match="Task is not editable in its current state"):
        task.update(
            title=task.title,
            description=task.description,
            status=TaskStatus.CANCELLED,
            due_date=date(2026, 3, 25),
            is_blocked=True
        )


def test_update_allows_in_progress_to_keep_same_status_and_change_other_fields() -> None:
    # Arrange
    task = build_task(
        status=TaskStatus.IN_PROGRESS,
        due_date=date(2026, 3, 25),
        description="old description"
    )

    # Act
    changed = task.update(
        title=task.title,
        description="new description",
        status=TaskStatus.IN_PROGRESS,
        due_date=date(2026, 3, 30),
        is_blocked=True
    )

    # Assert
    assert changed is True
    assert task.status == TaskStatus.IN_PROGRESS
    assert task.description == "new description"
    assert task.due_date == date(2026, 3, 30)
    assert task.is_blocked is True


def test_update_allows_pending_target_state_to_be_blocked() -> None:
    # Arrange
    task = build_task(status=TaskStatus.PENDING)

    # Act
    changed = task.update(
        title=task.title,
        description=task.description,
        status=TaskStatus.PENDING,
        due_date=None,
        is_blocked=True
    )

    # Assert
    assert changed is True
    assert task.status == TaskStatus.PENDING
    assert task.is_blocked is True


def test_update_does_not_clear_blocked_when_target_state_is_valid() -> None:
    # Arrange
    task = build_task(status=TaskStatus.PENDING)

    # Act
    changed = task.update(
        title=task.title,
        description=task.description,
        status=TaskStatus.IN_PROGRESS,
        due_date=date(2026, 3, 25),
        is_blocked=True
    )

    # Assert
    assert changed is True
    assert task.status == TaskStatus.IN_PROGRESS
    assert task.is_blocked is True


def test_update_allows_pending_to_cancelled() -> None:
    # Arrange
    task = build_task(status=TaskStatus.PENDING)

    # Act
    changed = task.update(
        title=task.title,
        description=task.description,
        status=TaskStatus.CANCELLED,
        due_date=None,
        is_blocked=False
    )

    # Assert
    assert changed is True
    assert task.status == TaskStatus.CANCELLED