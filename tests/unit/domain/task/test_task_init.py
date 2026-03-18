# tests/unit/domain/test_task_init.py

from datetime import date, timedelta
import pytest

from tests.unit.domain.task.helpers import build_task

from app.domain.enums.task_status import TaskStatus
from app.domain.errors import InvalidTaskStatusTransitionError, InvalidTaskDueDateError


# ----------------------------------------
# __init__ / initial invariants
# ----------------------------------------

def test_init_raises_when_in_progress_has_no_due_date() -> None:
    # Arrange / Act / Assert
    with pytest.raises(InvalidTaskDueDateError, match="required for IN_PROGRESS tasks"):
        build_task(status=TaskStatus.IN_PROGRESS, due_date=None)


def test_init_raises_when_completed_task_is_blocked() -> None:
    # Arrange / Act / Assert
    with pytest.raises(InvalidTaskStatusTransitionError, match="cannot be blocked in the target state"):
        build_task(status=TaskStatus.COMPLETED, due_date=date(2026, 3, 25), is_blocked=True)


def test_init_raises_when_cancelled_task_is_blocked() -> None:
    # Arrange / Act / Assert
    with pytest.raises(InvalidTaskStatusTransitionError, match="cannot be blocked in the target state"):
        build_task(status=TaskStatus.CANCELLED, due_date=date(2026, 3, 25), is_blocked=True)


def test_init_raises_when_due_date_is_in_the_past() -> None:
    # Arrange
    past_due_date = date.today() - timedelta(days=1)

    # Act / Assert
    with pytest.raises(InvalidTaskDueDateError, match="cannot be earlier than the current date"):
        build_task(status=TaskStatus.PENDING, due_date=past_due_date)


def test_init_allows_pending_task_to_start_blocked() -> None:
    # Arrange / Act
    task = build_task(status=TaskStatus.PENDING, is_blocked=True)

    # Assert
    assert task.status == TaskStatus.PENDING
    assert task.is_blocked is True


def test_init_allows_in_progress_task_with_due_date() -> None:
    # Arrange / Act
    task = build_task(status=TaskStatus.IN_PROGRESS, due_date=date(2026, 3, 25))

    # Assert
    assert task.status == TaskStatus.IN_PROGRESS
    assert task.due_date == date(2026, 3, 25)
    assert task.is_blocked is False


def test_init_allows_completed_task_when_not_blocked() -> None:
    # Arrange / Act
    task = build_task(status=TaskStatus.COMPLETED, due_date=date(2026, 3, 25))

    # Assert
    assert task.status == TaskStatus.COMPLETED
    assert task.is_blocked is False


def test_init_allows_cancelled_task_when_not_blocked() -> None:
    # Arrange / Act
    task = build_task(status=TaskStatus.CANCELLED, due_date=date(2026, 3, 25))

    # Assert
    assert task.status == TaskStatus.CANCELLED
    assert task.is_blocked is False


def test_init_allows_pending_task_without_due_date_and_not_blocked() -> None:
    # Arrange / Act
    task = build_task(status=TaskStatus.PENDING, due_date=None)

    # Assert
    assert task.status == TaskStatus.PENDING
    assert task.due_date is None
    assert task.is_blocked is False