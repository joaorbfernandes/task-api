# tests/unit/domain/test_task_blocking.py

from datetime import date
import pytest

from tests.factories.task import build_task

from app.domain.enums.task_status import TaskStatus
from app.domain.errors.task import InvalidTaskStatusTransitionError, TaskNotEditableError


# ----------------------------------------
# block / unblock
# ----------------------------------------

def test_block_sets_task_as_blocked_when_status_is_pending() -> None:
    # Arrange
    task = build_task(status=TaskStatus.PENDING, is_blocked=False)

    # Act
    changed = task.block()

    # Assert
    assert changed is True
    assert task.is_blocked is True


def test_block_sets_task_as_blocked_when_status_is_in_progress() -> None:
    # Arrange
    task = build_task(status=TaskStatus.IN_PROGRESS, due_date=date(2026, 3, 25), is_blocked=False)

    # Act
    changed = task.block()

    # Assert
    assert changed is True
    assert task.is_blocked is True


def test_block_returns_false_when_task_is_already_blocked() -> None:
    # Arrange
    task = build_task(is_blocked=True)

    # Act
    changed = task.block()

    # Assert
    assert changed is False
    assert task.is_blocked is True


def test_block_raises_when_task_is_completed() -> None:
    # Arrange
    task = build_task(status=TaskStatus.COMPLETED, is_blocked=False)

    # Act / Assert
    with pytest.raises(TaskNotEditableError, match="Task is not editable in its current state"):
        task.block()


def test_block_raises_when_task_is_cancelled() -> None:
    # Arrange
    task = build_task(status=TaskStatus.CANCELLED, is_blocked=False)

    # Act / Assert
    with pytest.raises(TaskNotEditableError, match="Task is not editable in its current state"):
        task.block()


def test_unblock_sets_task_as_unblocked_when_task_is_blocked() -> None:
    # Arrange
    task = build_task(is_blocked=True)

    # Act
    changed = task.unblock()

    # Assert
    assert changed is True
    assert task.is_blocked is False


def test_unblock_returns_false_when_task_is_already_unblocked() -> None:
    # Arrange
    task = build_task()

    # Act
    changed = task.unblock()

    # Assert
    assert changed is False
    assert task.is_blocked is False


def test_block_does_not_change_task_status() -> None:
    # Arrange
    task = build_task(status=TaskStatus.PENDING, is_blocked=False)

    # Act
    task.block()

    # Assert
    assert task.status == TaskStatus.PENDING
    assert task.is_blocked is True


def test_unblock_does_not_change_task_status() -> None:
    # Arrange
    task = build_task(status=TaskStatus.PENDING, is_blocked=True)

    # Act
    task.unblock()

    # Assert
    assert task.status == TaskStatus.PENDING
    assert task.is_blocked is False