# tests/unit/domain/test_task_properties.py

from datetime import date, datetime

from tests.factories.task import build_task

from app.domain.enums.task_status import TaskStatus


# ----------------------------------------
# properties / mark_updated
# ----------------------------------------

def test_task_exposes_all_properties() -> None:
    # Arrange
    created_at = datetime(2026, 3, 18, 12, 0, 0)
    updated_at = datetime(2026, 3, 19, 9, 30, 0)

    task = build_task(
        task_id=10,
        title="My task",
        description="task description",
        status=TaskStatus.IN_PROGRESS,
        due_date=date(2026, 3, 25),
        created_at=created_at,
        updated_at=updated_at,
        is_blocked=True
    )

    # Assert
    assert task.id == 10
    assert task.title == "My task"
    assert task.description == "task description"
    assert task.status == TaskStatus.IN_PROGRESS
    assert task.due_date == date(2026, 3, 25)
    assert task.created_at == created_at
    assert task.updated_at == updated_at
    assert task.is_blocked is True


def test_task_is_unblocked_by_default() -> None:
    # Arrange
    task = build_task()

    # Assert
    assert task.is_blocked is False


def test_mark_updated_sets_updated_at() -> None:
    # Arrange
    task = build_task(updated_at=None)
    timestamp = datetime(2026, 3, 20, 15, 45, 0)

    # Act
    task.mark_updated(timestamp)

    # Assert
    assert task.updated_at == timestamp


def test_mark_updated_does_not_change_domain_fields() -> None:
    # Arrange
    task = build_task(
        title="Task",
        description="desc",
        status=TaskStatus.PENDING,
        due_date=None
    )
    
    timestamp = datetime(2026, 3, 20, 15, 45, 0)

    # Act
    task.mark_updated(timestamp)

    # Assert
    assert task.title == "Task"
    assert task.description == "desc"
    assert task.status == TaskStatus.PENDING
    assert task.due_date is None
    assert task.is_blocked is False
    assert task.updated_at == timestamp