# tests/unit/domain/test_task_status.py

from datetime import date
import pytest

from tests.factories.task import build_task

from app.domain.enums.task_status import TaskStatus
from app.domain.errors.task import InvalidTaskStatusTransitionError, InvalidTaskDueDateError, TaskNotEditableError


# ----------------------------------------
# change_status
# ----------------------------------------

def test_change_status_returns_false_when_status_is_unchanged() -> None:
    # Arrange
    task = build_task(status=TaskStatus.PENDING)

    # Act
    changed = task.change_status(TaskStatus.PENDING)

    # Assert
    assert changed is False
    assert task.status == TaskStatus.PENDING


def test_change_status_allows_pending_to_in_progress_when_due_date_exists() -> None:
    # Arrange
    task = build_task(status=TaskStatus.PENDING, due_date=date(2026, 3, 25))

    # Act
    changed = task.change_status(TaskStatus.IN_PROGRESS)

    # Assert
    assert changed is True
    assert task.status == TaskStatus.IN_PROGRESS
    assert task.is_blocked is False


def test_change_status_allows_pending_to_cancelled() -> None:
    # Arrange
    task = build_task(status=TaskStatus.PENDING)

    # Act
    changed = task.change_status(TaskStatus.CANCELLED)

    # Assert
    assert changed is True
    assert task.status == TaskStatus.CANCELLED


def test_change_status_raises_when_pending_to_completed() -> None:
    # Arrange
    task = build_task(status=TaskStatus.PENDING)

    # Act / Assert
    with pytest.raises(InvalidTaskStatusTransitionError, match="Invalid task status transition"):
        task.change_status(TaskStatus.COMPLETED)


def test_change_status_allows_in_progress_to_completed() -> None:
    # Arrange
    task = build_task(status=TaskStatus.IN_PROGRESS, due_date=date(2026, 3, 25))

    # Act
    changed = task.change_status(TaskStatus.COMPLETED)

    # Assert
    assert changed is True
    assert task.status == TaskStatus.COMPLETED


def test_change_status_allows_in_progress_to_cancelled() -> None:
    # Arrange
    task = build_task(status=TaskStatus.IN_PROGRESS, due_date=date(2026, 3, 25))

    # Act
    changed = task.change_status(TaskStatus.CANCELLED)

    # Assert
    assert changed is True
    assert task.status == TaskStatus.CANCELLED


def test_change_status_raises_when_in_progress_to_pending() -> None:
    # Arrange
    task = build_task(status=TaskStatus.IN_PROGRESS, due_date=date(2026, 3, 25))

    # Act / Assert
    with pytest.raises(InvalidTaskStatusTransitionError, match="Invalid task status transition"):
        task.change_status(TaskStatus.PENDING)


def test_change_status_raises_when_task_is_completed() -> None:
    # Arrange
    task = build_task(status=TaskStatus.COMPLETED, due_date=date(2026, 3, 25))

    # Act / Assert
    with pytest.raises(TaskNotEditableError, match="Task is not editable in its current state"):
        task.change_status(TaskStatus.CANCELLED)


def test_change_status_raises_when_task_is_cancelled() -> None:
    # Arrange
    task = build_task(status=TaskStatus.CANCELLED)

    # Act / Assert
    with pytest.raises(TaskNotEditableError, match="Task is not editable in its current state"):
        task.change_status(TaskStatus.PENDING)


def test_change_status_raises_when_moving_to_in_progress_without_due_date() -> None:
    # Arrange
    task = build_task(status=TaskStatus.PENDING, due_date=None)

    # Act / Assert
    with pytest.raises(InvalidTaskDueDateError, match="required for IN_PROGRESS tasks"):
        task.change_status(TaskStatus.IN_PROGRESS)


def test_change_status_allows_blocked_pending_to_in_progress_and_clears_blocked() -> None:
    # Arrange
    task = build_task(status=TaskStatus.PENDING, due_date=date(2026, 3, 25), is_blocked=True)

    # Act
    changed = task.change_status(TaskStatus.IN_PROGRESS)

    # Assert
    assert changed is True
    assert task.status == TaskStatus.IN_PROGRESS
    assert task.is_blocked is False


def test_change_status_allows_blocked_in_progress_to_cancelled_and_clears_blocked() -> None:
    # Arrange
    task = build_task(status=TaskStatus.IN_PROGRESS, due_date=date(2026, 3, 25), is_blocked=True)

    # Act
    changed = task.change_status(TaskStatus.CANCELLED)

    # Assert
    assert changed is True
    assert task.status == TaskStatus.CANCELLED
    assert task.is_blocked is False


def test_change_status_raises_when_blocked_pending_to_cancelled() -> None:
    # Arrange
    task = build_task(status=TaskStatus.PENDING, is_blocked=True)

    # Act / Assert
    with pytest.raises(InvalidTaskStatusTransitionError, match="Blocked tasks cannot change status"):
        task.change_status(TaskStatus.CANCELLED)


def test_change_status_raises_when_blocked_pending_to_completed() -> None:
    # Arrange
    task = build_task(status=TaskStatus.PENDING, is_blocked=True)

    # Act / Assert
    with pytest.raises(InvalidTaskStatusTransitionError, match="Blocked tasks cannot change status"):
        task.change_status(TaskStatus.COMPLETED)


def test_change_status_raises_when_blocked_in_progress_to_completed() -> None:
    # Arrange
    task = build_task(status=TaskStatus.IN_PROGRESS, due_date=date(2026, 3, 25), is_blocked=True)

    # Act / Assert
    with pytest.raises(InvalidTaskStatusTransitionError, match="Blocked tasks cannot change status"):
        task.change_status(TaskStatus.COMPLETED)


def test_change_status_raises_when_blocked_in_progress_to_pending() -> None:
    # Arrange
    task = build_task(status=TaskStatus.IN_PROGRESS, due_date=date(2026, 3, 25), is_blocked=True)

    # Act / Assert
    with pytest.raises(InvalidTaskStatusTransitionError, match="Blocked tasks cannot change status"):
        task.change_status(TaskStatus.PENDING)


def test_change_status_does_not_change_due_date() -> None:
    # Arrange
    original_due_date = date(2026, 3, 25)
    task = build_task(status=TaskStatus.PENDING, due_date=original_due_date)

    # Act
    task.change_status(TaskStatus.IN_PROGRESS)

    # Assert
    assert task.status == TaskStatus.IN_PROGRESS
    assert task.due_date == original_due_date
