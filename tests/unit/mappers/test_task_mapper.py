from datetime import date

from app.application.dtos.task_dto import CreateTaskInput, UpdateTaskInput
from app.application.mappers.task_mapper import map_task_create_to_input, map_task_update_to_input #, merge_task_patch_into_update_input
from app.domain.enums.task_status import TaskStatus
from app.api.schemas.task import TaskCreate, TaskPatch, TaskUpdate
from tests.factories.task import build_task


# ----------------------------------------
# map_task_create_to_input
# ----------------------------------------

def test_map_task_create_to_input_maps_all_fields() -> None:
    # Arrange
    task_create = TaskCreate(
        title="My task",
        description="testing",
        due_date=date(2026, 3, 20),
        is_blocked=True,
    )

    # Act
    result = map_task_create_to_input(task_create)

    # Assert
    assert isinstance(result, CreateTaskInput)
    assert result.title == "My task"
    assert result.description == "testing"
    assert result.due_date == date(2026, 3, 20)
    assert result.is_blocked is True


# ----------------------------------------
# map_task_update_to_input
# ----------------------------------------

def test_map_task_update_to_input_maps_all_fields() -> None:
    # Arrange
    task_update = TaskUpdate(
        title="Updated title",
        description=None,
        status=TaskStatus.PENDING,
        due_date=None,
        is_blocked=False,
    )

    # Act
    result = map_task_update_to_input(task_update)

    # Assert
    assert isinstance(result, UpdateTaskInput)
    assert result.title == "Updated title"
    assert result.description is None
    assert result.status == TaskStatus.PENDING
    assert result.due_date is None
    assert result.is_blocked is False


'''
# ----------------------------------------
# merge_task_patch_into_update_input
# ----------------------------------------

def test_merge_task_patch_into_update_input_keeps_current_values_when_fields_are_not_provided() -> None:
    # Arrange
    task = build_task(
        title="Original title",
        description="testing",
        status=TaskStatus.PENDING,
        due_date=None,
        is_blocked=True,
    )
    task_patch = TaskPatch(title="New title")

    # Act
    result = merge_task_patch_into_update_input(task, task_patch)

    # Assert
    assert isinstance(result, UpdateTaskInput)
    assert result.title == "New title"
    assert result.description == "testing"
    assert result.status == TaskStatus.PENDING
    assert result.due_date is None
    assert result.is_blocked is True


def test_merge_task_patch_into_update_input_sets_description_to_none_when_explicitly_provided() -> None:
    # Arrange
    task = build_task(
        title="Original title",
        description="testing",
        status=TaskStatus.PENDING,
        due_date=None,
        is_blocked=False,
    )
    task_patch = TaskPatch(description=None)

    # Act
    result = merge_task_patch_into_update_input(task, task_patch)

    # Assert
    assert result.title == "Original title"
    assert result.description is None
    assert result.status == TaskStatus.PENDING
    assert result.due_date is None
    assert result.is_blocked is False


def test_merge_task_patch_into_update_input_replaces_due_date_when_provided() -> None:
    # Arrange
    task = build_task(
        title="Original title",
        description="testing",
        status=TaskStatus.PENDING,
        due_date=None,
        is_blocked=False,
    )
    task_patch = TaskPatch(due_date=date(2026, 3, 20))

    # Act
    result = merge_task_patch_into_update_input(task, task_patch)

    # Assert
    assert result.due_date == date(2026, 3, 20)
    assert result.title == "Original title"
    assert result.description == "testing"
    assert result.status == TaskStatus.PENDING
    assert result.is_blocked is False


def test_merge_task_patch_into_update_input_replaces_is_blocked_when_provided() -> None:
    # Arrange
    task = build_task(
        title="Original title",
        description="testing",
        status=TaskStatus.PENDING,
        due_date=None,
        is_blocked=False,
    )
    task_patch = TaskPatch(is_blocked=True)

    # Act
    result = merge_task_patch_into_update_input(task, task_patch)

    # Assert
    assert result.is_blocked is True
    assert result.title == "Original title"
    assert result.description == "testing"
    assert result.status == TaskStatus.PENDING
    assert result.due_date is None


def test_merge_task_patch_into_update_input_merges_status_and_due_date_into_final_state() -> None:
    # Arrange
    task = build_task(
        title="Original title",
        description="testing",
        status=TaskStatus.PENDING,
        due_date=None,
        is_blocked=False,
    )
    task_patch = TaskPatch(
        status=TaskStatus.IN_PROGRESS,
        due_date=date(2026, 3, 20),
    )

    # Act
    result = merge_task_patch_into_update_input(task, task_patch)

    # Assert
    assert result.title == "Original title"
    assert result.description == "testing"
    assert result.status == TaskStatus.IN_PROGRESS
    assert result.due_date == date(2026, 3, 20)
    assert result.is_blocked is False

'''