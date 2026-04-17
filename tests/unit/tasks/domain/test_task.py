from datetime import datetime
from uuid import uuid4

import pytest

from app.modules.tasks.domain.task_errors import (
    InvalidTaskDueDateError,
    InvalidTaskStatusTransitionError,
    InvalidTaskTitleError,
    TaskNotEditableError,
)
from app.modules.tasks.domain.task_status import TaskStatus
from tests.factories.task import build_new_task, future_date, past_date


# -----------------------------
# Creation / invariants
# -----------------------------

def test_create_pending_task_with_valid_defaults() -> None:
    # Arrange / Act
    task = build_new_task()

    # Assert
    assert task.status == TaskStatus.PENDING
    assert task.due_date is None
    assert task.is_blocked is False

def test_create_task_rejects_past_due_date() -> None:
    # Arrange / Act / Assert
    with pytest.raises(
        InvalidTaskDueDateError,
        match="Due date can't be earlier than the current date",
    ):
        build_new_task(due_date=past_date())


def test_create_in_progress_requires_due_date() -> None:
    # Arrange / Act / Assert
    with pytest.raises(
        InvalidTaskDueDateError,
        match="Due date is required for IN PROGRESS tasks",
    ):
        build_new_task(status=TaskStatus.IN_PROGRESS, due_date=None)


def test_create_completed_requires_due_date() -> None:
    # Arrange / Act / Assert
    with pytest.raises(
        InvalidTaskDueDateError,
        match="Due date is required for COMPLETED tasks",
    ):
        build_new_task(status=TaskStatus.COMPLETED, due_date=None)


def test_create_completed_cannot_be_blocked() -> None:
    # Arrange / Act / Assert
    with pytest.raises(
        InvalidTaskStatusTransitionError,
        match="Task can't be blocked in the COMPLETED state",
    ):
        build_new_task(
            status=TaskStatus.COMPLETED,
            due_date=future_date(),
            is_blocked=True,
        )


def test_create_cancelled_can_remain_blocked() -> None:
    # Arrange / Act
    task = build_new_task(
        status=TaskStatus.CANCELLED,
        due_date=None,
        is_blocked=True,
    )

    # Assert
    assert task.status == TaskStatus.CANCELLED
    assert task.is_blocked is True


def test_create_rejects_blank_title() -> None:
    # Arrange / Act / Assert
    with pytest.raises(
        InvalidTaskTitleError,
        match="Task title cannot be empty",
    ):
        build_new_task(title="   ")


# -----------------------------
# Full update
# -----------------------------

def test_update_returns_false_when_final_state_is_identical() -> None:
    # Arrange
    due = future_date()
    task = build_new_task(
        title="Same",
        description="same",
        status=TaskStatus.PENDING,
        due_date=due,
        is_blocked=False,
    )

    # Act
    changed = task.update(
        title="Same",
        description="same",
        status=TaskStatus.PENDING,
        due_date=due,
        is_blocked=False,
    )

    # Assert
    assert changed is False


def test_update_trims_title_before_saving() -> None:
    # Arrange
    task = build_new_task(title="Old")

    # Act
    changed = task.update(
        title="  New title  ",
        description=task.description,
        status=task.status,
        due_date=task.due_date,
        is_blocked=task.is_blocked,
    )

    # Assert
    assert changed is True
    assert task.title == "New title"


def test_update_allows_explicit_unblock_and_progress_in_same_operation() -> None:
    # Arrange
    task = build_new_task(
        status=TaskStatus.PENDING,
        due_date=future_date(),
        is_blocked=True,
    )

    # Act
    changed = task.update(
        title=task.title,
        description=task.description,
        status=TaskStatus.IN_PROGRESS,
        due_date=task.due_date,
        is_blocked=False,
    )

    # Assert
    assert changed is True
    assert task.status == TaskStatus.IN_PROGRESS
    assert task.is_blocked is False


def test_update_rejects_blocked_pending_to_in_progress_when_target_remains_blocked() -> None:
    # Arrange
    task = build_new_task(
        status=TaskStatus.PENDING,
        due_date=future_date(),
        is_blocked=True,
    )

    # Act / Assert
    with pytest.raises(
        InvalidTaskStatusTransitionError,
        match="Can't change task status from PENDING to IN PROGRESS because the task is BLOCKED",
    ):
        task.update(
            title=task.title,
            description=task.description,
            status=TaskStatus.IN_PROGRESS,
            due_date=task.due_date,
            is_blocked=True,
        )


def test_update_rejects_in_progress_without_due_date() -> None:
    # Arrange
    task = build_new_task(
        status=TaskStatus.PENDING,
        due_date=None,
        is_blocked=False,
    )

    # Act / Assert
    with pytest.raises(
        InvalidTaskDueDateError,
        match="Due date is required for IN PROGRESS tasks",
    ):
        task.update(
            title=task.title,
            description=task.description,
            status=TaskStatus.IN_PROGRESS,
            due_date=None,
            is_blocked=False,
        )


def test_update_rejects_pending_to_completed() -> None:
    # Arrange
    task = build_new_task(
        status=TaskStatus.PENDING,
        due_date=future_date(),
        is_blocked=False,
    )

    # Act / Assert
    with pytest.raises(
        InvalidTaskStatusTransitionError,
        match="Can't change task status from PENDING to COMPLETED",
    ):
        task.update(
            title=task.title,
            description=task.description,
            status=TaskStatus.COMPLETED,
            due_date=task.due_date,
            is_blocked=False,
        )


def test_update_rejects_completed_with_blocked_true() -> None:
    # Arrange
    task = build_new_task(
        status=TaskStatus.IN_PROGRESS,
        due_date=future_date(),
        is_blocked=False,
    )

    # Act / Assert
    with pytest.raises(
        InvalidTaskStatusTransitionError,
        match="Can't change task status from IN PROGRESS to COMPLETED because the task is BLOCKED",
    ):
        task.update(
            title=task.title,
            description=task.description,
            status=TaskStatus.COMPLETED,
            due_date=task.due_date,
            is_blocked=True,
        )


def test_update_rejects_blocked_in_progress_to_completed_when_target_remains_blocked() -> None:
    # Arrange
    task = build_new_task(
        status=TaskStatus.IN_PROGRESS,
        due_date=future_date(),
        is_blocked=True,
    )

    # Act / Assert
    with pytest.raises(
        InvalidTaskStatusTransitionError,
        match="Can't change task status from IN PROGRESS to COMPLETED because the task is BLOCKED",
    ):
        task.update(
            title=task.title,
            description=task.description,
            status=TaskStatus.COMPLETED,
            due_date=task.due_date,
            is_blocked=True,
        )


def test_update_allows_explicit_unblock_and_complete_in_same_operation() -> None:
    # Arrange
    task = build_new_task(
        status=TaskStatus.IN_PROGRESS,
        due_date=future_date(),
        is_blocked=True,
    )

    # Act
    changed = task.update(
        title=task.title,
        description=task.description,
        status=TaskStatus.COMPLETED,
        due_date=task.due_date,
        is_blocked=False,
    )

    # Assert
    assert changed is True
    assert task.status == TaskStatus.COMPLETED
    assert task.is_blocked is False


@pytest.mark.parametrize("status", [TaskStatus.COMPLETED, TaskStatus.CANCELLED])
def test_update_rejects_terminal_task(status: TaskStatus) -> None:
    # Arrange
    due_date = future_date() if status == TaskStatus.COMPLETED else None
    task = build_new_task(status=status, due_date=due_date)

    # Act / Assert
    with pytest.raises(TaskNotEditableError, match="Task is not editable"):
        task.update(
            title=task.title,
            description=task.description,
            status=task.status,
            due_date=task.due_date,
            is_blocked=task.is_blocked,
        )


def test_update_does_not_mutate_task_when_validation_fails() -> None:
    # Arrange
    task = build_new_task(
        title="Original",
        status=TaskStatus.IN_PROGRESS,
        due_date=future_date(),
        is_blocked=False,
    )

    # Act / Assert
    with pytest.raises(
        InvalidTaskStatusTransitionError,
        match="Can't change task status from IN PROGRESS to COMPLETED because the task is BLOCKED",
    ):
        task.update(
            title="Changed",
            description=task.description,
            status=TaskStatus.COMPLETED,
            due_date=task.due_date,
            is_blocked=True,
        )

    # Assert
    assert task.title == "Original"
    assert task.status == TaskStatus.IN_PROGRESS
    assert task.is_blocked is False


# -----------------------------
# update_at
# -----------------------------

def test_mark_updated_sets_updated_at() -> None:
    # Arrange
    task = build_new_task()
    timestamp = datetime.now()

    # Act
    task.mark_updated(timestamp)

    # Assert
    assert task.updated_at == timestamp

def test_update_rejects_transition_from_pending_to_in_progress_when_target_becomes_blocked() -> None:
    """
    update should reject the transition from PENDING to IN_PROGRESS
    when the target state becomes blocked.
    """
    # Arrange
    task = build_new_task(
        status=TaskStatus.PENDING,
        due_date=None,
        is_blocked=False,
    )

    # Act / Assert
    with pytest.raises(
        InvalidTaskStatusTransitionError,
        match="PENDING to IN PROGRESS",
    ):
        task.update(
            title=task.title,
            description=task.description,
            status=TaskStatus.IN_PROGRESS,
            due_date=future_date(),
            is_blocked=True,
        )

def test_update_allows_transition_from_pending_to_in_progress_when_target_is_not_blocked() -> None:
    """
    update should allow the transition from PENDING to IN_PROGRESS
    when the target state is not blocked.
    """
    # Arrange
    task = build_new_task(
        status=TaskStatus.PENDING,
        due_date=None,
        is_blocked=False,
    )

    # Act
    changed = task.update(
        title=task.title,
        description=task.description,
        status=TaskStatus.IN_PROGRESS,
        due_date=future_date(),
        is_blocked=False,
    )

    # Assert
    assert changed is True
    assert task.status == TaskStatus.IN_PROGRESS
    assert task.is_blocked is False

def test_update_rejects_transition_from_pending_blocked_to_in_progress_blocked() -> None:
    """
    update should reject the transition from PENDING to IN_PROGRESS
    when the task remains blocked in the target state.
    """
    # Arrange
    task = build_new_task(
        status=TaskStatus.PENDING,
        due_date=None,
        is_blocked=True,
    )

    # Act / Assert
    with pytest.raises(
        InvalidTaskStatusTransitionError,
        match="PENDING to IN PROGRESS",
    ):
        task.update(
            title=task.title,
            description=task.description,
            status=TaskStatus.IN_PROGRESS,
            due_date=future_date(),
            is_blocked=True,
        )

def test_update_allows_transition_from_pending_blocked_to_in_progress_when_target_is_unblocked() -> None:
    """
    update should allow the transition from PENDING to IN_PROGRESS
    when the target state is unblocked.
    """
    # Arrange
    task = build_new_task(
        status=TaskStatus.PENDING,
        due_date=None,
        is_blocked=True,
    )

    # Act
    changed = task.update(
        title=task.title,
        description=task.description,
        status=TaskStatus.IN_PROGRESS,
        due_date=future_date(),
        is_blocked=False,
    )

    # Assert
    assert changed is True
    assert task.status == TaskStatus.IN_PROGRESS
    assert task.is_blocked is False