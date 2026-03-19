# tests/unit/domain/test_task_editing.py

import pytest

from tests.factories.task import build_task

from app.domain.enums.task_status import TaskStatus
from app.domain.errors.task import TaskNotEditableError


# ----------------------------------------
# rename
# ----------------------------------------

def test_rename_updates_title_when_task_is_editable() -> None:
    # Arrange
    task = build_task(title="Original title")

    # Act
    changed = task.rename("Updated title")

    # Assert
    assert changed is True
    assert task.title == "Updated title"


def test_rename_returns_false_when_title_is_unchanged() -> None:
    # Arrange
    task = build_task(title="Same title")

    # Act
    changed = task.rename("Same title")

    # Assert
    assert changed is False
    assert task.title == "Same title"


def test_rename_raises_when_task_is_completed() -> None:
    # Arrange
    task = build_task(status=TaskStatus.COMPLETED)

    # Act / Assert
    with pytest.raises(TaskNotEditableError, match="Task is not editable"):
        task.rename("Updated title")


def test_rename_raises_when_task_is_cancelled() -> None:
    # Arrange
    task = build_task(status=TaskStatus.CANCELLED)

    # Act / Assert
    with pytest.raises(TaskNotEditableError, match="Task is not editable"):
        task.rename("Updated title")


def test_rename_does_not_change_title_when_task_is_completed() -> None:
    # Arrange
    task = build_task(status=TaskStatus.COMPLETED, title="Original title")

    # Act / Assert
    with pytest.raises(TaskNotEditableError):
        task.rename("Updated title")

    assert task.title == "Original title"


def test_rename_does_not_change_title_when_task_is_cancelled() -> None:
    task = build_task(status=TaskStatus.CANCELLED, title="Original title")

    with pytest.raises(TaskNotEditableError):
        task.rename("Updated title")

    assert task.title == "Original title"

# ----------------------------------------
# change_description
# ----------------------------------------

def test_change_description_updates_description_when_task_is_editable() -> None:
    # Arrange
    task = build_task(description="original description")

    # Act
    changed = task.change_description("updated description")

    # Assert
    assert changed is True
    assert task.description == "updated description"


def test_change_description_returns_false_when_description_is_unchanged() -> None:
    # Arrange
    task = build_task(description="same description")

    # Act
    changed = task.change_description("same description")

    # Assert
    assert changed is False
    assert task.description == "same description"


def test_change_description_allows_setting_description_to_none() -> None:
    # Arrange
    task = build_task(description="description to clear")

    # Act
    changed = task.change_description(None)

    # Assert
    assert changed is True
    assert task.description is None


def test_change_description_raises_when_task_is_completed() -> None:
    # Arrange
    task = build_task(status=TaskStatus.COMPLETED, description="original")

    # Act / Assert
    with pytest.raises(TaskNotEditableError, match="Task is not editable"):
        task.change_description("updated")


def test_change_description_raises_when_task_is_cancelled() -> None:
    # Arrange
    task = build_task(status=TaskStatus.CANCELLED, description="original")

    # Act / Assert
    with pytest.raises(TaskNotEditableError, match="Task is not editable"):
        task.change_description("updated")


def test_change_description_does_not_change_description_when_task_is_completed() -> None:
    # Arrange
    task = build_task(status=TaskStatus.COMPLETED, description="original")

    # Act / Assert
    with pytest.raises(TaskNotEditableError):
        task.change_description("updated")

    assert task.description == "original"