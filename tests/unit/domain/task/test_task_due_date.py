# tests/unit/domain/test_task_due_date.py

from datetime import date, timedelta
import pytest

from tests.unit.domain.task.helpers import build_task

from app.domain.enums.task_status import TaskStatus
from app.domain.errors.errors import TaskNotEditableError, InvalidTaskDueDateError


# ----------------------------------------
# change_due_date
# ----------------------------------------

def test_change_due_date_updates_due_date_when_task_is_pending() -> None:
    # Arrange
    task = build_task(status=TaskStatus.PENDING, due_date=None)
    new_due_date = date(2026, 3, 25)

    # Act
    changed = task.change_due_date(new_due_date)

    # Assert
    assert changed is True
    assert task.due_date == new_due_date


def test_change_due_date_updates_due_date_when_task_is_in_progress() -> None:
    # Arrange
    original_due_date = date(2026, 3, 25)
    new_due_date = date(2026, 3, 30)

    task = build_task(status=TaskStatus.IN_PROGRESS, due_date=original_due_date)

    # Act
    changed = task.change_due_date(new_due_date)

    # Assert
    assert changed is True
    assert task.due_date == new_due_date


def test_change_due_date_returns_false_when_due_date_is_unchanged() -> None:
    # Arrange
    same_due_date = date(2026, 3, 25)
    task = build_task(due_date=same_due_date)

    # Act
    changed = task.change_due_date(same_due_date)

    # Assert
    assert changed is False
    assert task.due_date == same_due_date


def test_change_due_date_raises_when_due_date_is_in_the_past() -> None:
    # Arrange
    task = build_task(status=TaskStatus.PENDING)
    past_due_date = date.today() - timedelta(days=1)

    # Act / Assert
    with pytest.raises(InvalidTaskDueDateError, match="cannot be earlier than the current date"):
        task.change_due_date(past_due_date)


def test_change_due_date_raises_when_in_progress_task_would_have_no_due_date() -> None:
    # Arrange
    task = build_task(status=TaskStatus.IN_PROGRESS, due_date=date(2026, 3, 25))

    # Act / Assert
    with pytest.raises(InvalidTaskDueDateError, match="required for IN_PROGRESS tasks"):
        task.change_due_date(None)


def test_change_due_date_raises_when_task_is_completed() -> None:
    # Arrange
    task = build_task(status=TaskStatus.COMPLETED, due_date=date(2026, 3, 25))

    # Act / Assert
    with pytest.raises(TaskNotEditableError, match="Task is not editable"):
        task.change_due_date(date(2026, 3, 30))


def test_change_due_date_raises_when_task_is_cancelled() -> None:
    # Arrange
    task = build_task(status=TaskStatus.CANCELLED, due_date=date(2026, 3, 25))

    # Act / Assert
    with pytest.raises(TaskNotEditableError, match="Task is not editable"):
        task.change_due_date(date(2026, 3, 30))


def test_change_due_date_does_not_change_task_status() -> None:
    # Arrange
    task = build_task(status=TaskStatus.PENDING, due_date=None)
    new_due_date = date(2026, 3, 25)

    # Act
    task.change_due_date(new_due_date)

    # Assert
    assert task.status == TaskStatus.PENDING
    assert task.due_date == new_due_date


def test_change_due_date_does_not_change_blocked_state() -> None:
    # Arrange
    task = build_task(status=TaskStatus.PENDING, due_date=None, is_blocked=True)
    new_due_date = date(2026, 3, 25)

    # Act
    task.change_due_date(new_due_date)

    # Assert
    assert task.is_blocked is True
    assert task.due_date == new_due_date