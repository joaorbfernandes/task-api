from datetime import date

import pytest
from pydantic import ValidationError

from app.domain.enums.task_status import TaskStatus
from app.schemas.task import TaskCreate, TaskPatch


# ----------------------------------------
# TaskCreate
# ----------------------------------------

def test_task_create_sets_is_blocked_to_false_by_default() -> None:
    # Act
    task_create = TaskCreate(
        title="My task",
        description="testing",
        due_date=None,
    )

    # Assert
    assert task_create.title == "My task"
    assert task_create.description == "testing"
    assert task_create.due_date is None
    assert task_create.is_blocked is False


def test_task_create_accepts_is_blocked_when_provided() -> None:
    # Act
    task_create = TaskCreate(
        title="Blocked task",
        description="testing",
        due_date=None,
        is_blocked=True,
    )

    # Assert
    assert task_create.title == "Blocked task"
    assert task_create.description == "testing"
    assert task_create.due_date is None
    assert task_create.is_blocked is True

# ----------------------------------------
# TaskPatch
# ----------------------------------------

def test_task_patch_raises_when_no_fields_are_provided() -> None:
    # Act / Assert
    with pytest.raises(ValidationError, match="at least one field must be provided"):
        TaskPatch()


def test_task_patch_raises_when_title_is_explicitly_null() -> None:
    # Act / Assert
    with pytest.raises(ValidationError, match="title cannot be null"):
        TaskPatch(title=None)


def test_task_patch_raises_when_status_is_explicitly_null() -> None:
    # Act / Assert
    with pytest.raises(ValidationError, match="status cannot be null"):
        TaskPatch(status=None)


def test_task_patch_raises_when_is_blocked_is_explicitly_null() -> None:
    # Act / Assert
    with pytest.raises(ValidationError, match="is_blocked cannot be null"):
        TaskPatch(is_blocked=None)


def test_task_patch_accepts_is_blocked_when_provided() -> None:
    # Act
    task_patch = TaskPatch(is_blocked=True)

    # Assert
    assert task_patch.is_blocked is True
    assert task_patch.model_fields_set == {"is_blocked"}


def test_task_patch_accepts_status_and_due_date_together() -> None:
    # Act
    task_patch = TaskPatch(
        status=TaskStatus.IN_PROGRESS,
        due_date=date(2026, 3, 20),
    )

    # Assert
    assert task_patch.status == TaskStatus.IN_PROGRESS
    assert task_patch.due_date == date(2026, 3, 20)
    assert task_patch.model_fields_set == {"status", "due_date"}