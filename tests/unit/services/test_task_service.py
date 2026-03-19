# tests/unit/services/test_task_service.py

from datetime import date
from unittest.mock import Mock

import pytest

from app.domain.entities.task import Task
from app.domain.enums.task_status import TaskStatus
from app.domain.errors.task import InvalidTaskDueDateError
from app.infrastructure.repositories.task_repository import TaskRepository
from app.application.services.task_service import TaskNotFoundError, TaskService
from tests.factories.task import build_task
from app.application.dtos.task_dto import CreateTaskInput, UpdateTaskInput

@pytest.fixture
def repository() -> Mock:
    """
    Return a mock TaskRepository for each test.
    """
    return Mock(spec=TaskRepository)


@pytest.fixture
def task_service(repository: Mock) -> TaskService:
    """
    Return a TaskService instance with a mocked repository.
    """
    return TaskService(repository=repository)


def save_task_side_effect(task: Task) -> Task:
    return task


# ----------------------------------------
# get_task
# ----------------------------------------

def test_get_task_returns_task_when_repository_finds_it(task_service: TaskService, repository: Mock):
    """
    get_task should return the task when the repository finds it.
    """
    # Arrange
    existing_task = build_task(task_id=1, title="Task 1")
    repository.get_task.return_value = existing_task

    # Act
    result = task_service.get_task(1)

    # Assert
    assert result == existing_task
    repository.get_task.assert_called_once_with(1)

def test_get_task_raises_when_repository_returns_none(task_service: TaskService, repository: Mock):
    """
    get_task should raise TaskNotFoundError when the repository returns None.
    """
    # Arrange
    repository.get_task.return_value = None

    # Act / Assert
    with pytest.raises(TaskNotFoundError, match="Task not found"):
        task_service.get_task(999)

    repository.get_task.assert_called_once_with(999)

# ----------------------------------------
# delete_task
# ----------------------------------------

def test_delete_task_calls_repository_delete_when_task_exists(task_service: TaskService, repository: Mock):
    """
    delete_task should call repository.delete_task when the task exists.
    """
    # Arrange
    existing_task = build_task(task_id=1, title="Task to delete")
    repository.get_task.return_value = existing_task

    # Act
    task_service.delete_task(1)

    # Assert
    repository.get_task.assert_called_once_with(1)
    repository.delete_task.assert_called_once_with(1)

def test_delete_task_raises_when_repository_returns_none(task_service: TaskService, repository: Mock):
    """
    delete_task should raise TaskNotFoundError when the repository does not find the task.
    """
    # Arrange
    repository.get_task.return_value = None

    # Act / Assert
    with pytest.raises(TaskNotFoundError, match="Task not found"):
        task_service.delete_task(999)

    repository.get_task.assert_called_once_with(999)
    repository.delete_task.assert_not_called()

# ----------------------------------------
# list_tasks
# ----------------------------------------

def test_list_tasks_returns_tasks_from_repository(task_service: TaskService, repository: Mock):
    """
    list_tasks should return the tasks provided by the repository.
    """
    # Arrange
    stored_tasks = [build_task(task_id=1, title="Task 1"), build_task(task_id=2, title="Task 2")]
    repository.list_tasks.return_value = stored_tasks

    # Act
    result = task_service.list_tasks()

    # Assert
    assert result == stored_tasks
    repository.list_tasks.assert_called_once_with()

# ----------------------------------------
# create_task
# ----------------------------------------

def test_create_task_builds_task_with_default_status_and_saves_it(task_service: TaskService, repository: Mock):
    """
    create_task should build a Task with default status and save it through the repository.
    """
    # Arrange
    task_input = CreateTaskInput(title="My first task", description="testing", due_date=None)
    repository.next_id.return_value = 1

    repository.save_task.side_effect = save_task_side_effect

    # Act
    result = task_service.create_task(task_input)

    # Assert
    assert result.id == 1
    assert result.title == "My first task"
    assert result.description == "testing"
    assert result.status == TaskStatus.PENDING
    assert result.is_blocked is False
    assert result.due_date is None
    assert result.created_at is not None
    assert result.updated_at is None

    repository.next_id.assert_called_once_with()
    repository.save_task.assert_called_once()

    saved_task = repository.save_task.call_args.args[0]
    assert isinstance(saved_task, Task)
    assert saved_task.id == 1
    assert saved_task.title == "My first task"
    assert saved_task.description == "testing"
    assert saved_task.status == TaskStatus.PENDING
    assert saved_task.is_blocked is False
    assert saved_task.due_date is None
    assert saved_task.created_at is not None
    assert saved_task.updated_at is None

def test_create_task_accepts_due_date_when_provided(task_service: TaskService, repository: Mock):
    """
    create_task should include due_date in the created Task when provided.
    """
    # Arrange
    task_input = CreateTaskInput(title="Task with due date", description="testing", due_date=date(2026, 3, 20))
    repository.next_id.return_value = 1

    repository.save_task.side_effect = save_task_side_effect

    # Act
    result = task_service.create_task(task_input)

    # Assert
    assert result.id == 1
    assert result.title == "Task with due date"
    assert result.description == "testing"
    assert result.status == TaskStatus.PENDING
    assert result.is_blocked is False
    assert result.due_date == date(2026, 3, 20)
    assert result.created_at is not None
    assert result.updated_at is None

    repository.next_id.assert_called_once_with()
    repository.save_task.assert_called_once()

    saved_task = repository.save_task.call_args.args[0]
    assert isinstance(saved_task, Task)
    assert saved_task.id == 1
    assert saved_task.title == "Task with due date"
    assert saved_task.description == "testing"
    assert saved_task.status == TaskStatus.PENDING
    assert saved_task.is_blocked is False
    assert saved_task.due_date == date(2026, 3, 20)
    assert saved_task.created_at is not None
    assert saved_task.updated_at is None

def test_create_task_accepts_is_blocked_when_provided(task_service: TaskService, repository: Mock):
    """
    create_task should include is_blocked in the created Task when provided.
    """
    # Arrange
    task_input = CreateTaskInput(
        title="Blocked task",
        description="testing",
        due_date=None,
        is_blocked=True,
    )
    repository.next_id.return_value = 1
    repository.save_task.side_effect = save_task_side_effect

    # Act
    result = task_service.create_task(task_input)

    # Assert
    assert result.id == 1
    assert result.title == "Blocked task"
    assert result.description == "testing"
    assert result.status == TaskStatus.PENDING
    assert result.due_date is None
    assert result.is_blocked is True
    assert result.created_at is not None
    assert result.updated_at is None

    repository.next_id.assert_called_once_with()
    repository.save_task.assert_called_once()

    saved_task = repository.save_task.call_args.args[0]
    assert isinstance(saved_task, Task)
    assert saved_task.id == 1
    assert saved_task.title == "Blocked task"
    assert saved_task.description == "testing"
    assert saved_task.status == TaskStatus.PENDING
    assert saved_task.due_date is None
    assert saved_task.is_blocked is True
    assert saved_task.created_at is not None
    assert saved_task.updated_at is None

# ----------------------------------------
# update_task
# ----------------------------------------

def test_update_task_replaces_task_data_and_saves_it(task_service: TaskService, repository: Mock):
    """
    update_task should fully replace task fields and save the updated task.
    """
    # Arrange
    existing_task = build_task(task_id=1, title="Original title", description="original", due_date=None)

    repository.get_task.return_value = existing_task

    task_update = UpdateTaskInput(
        title="Updated title",
        description="updated",
        status=TaskStatus.IN_PROGRESS,
        due_date=date(2026, 3, 20),
        is_blocked=True,
    )

    repository.save_task.side_effect = save_task_side_effect

    # Act
    result = task_service.update_task(1, task_update)

    # Assert
    assert result.id == 1
    assert result.title == "Updated title"
    assert result.description == "updated"
    assert result.status == TaskStatus.IN_PROGRESS
    assert result.due_date == date(2026, 3, 20)
    assert result.is_blocked is True
    assert result.created_at == existing_task.created_at
    assert result.updated_at is not None

    repository.get_task.assert_called_once_with(1)
    repository.save_task.assert_called_once_with(existing_task)

def test_update_task_raises_when_repository_returns_none(task_service: TaskService, repository: Mock):
    """
    update_task should raise TaskNotFoundError when the repository does not find the task.
    """
    # Arrange
    repository.get_task.return_value = None
    task_update = UpdateTaskInput(title="Updated title", description="updated", status=TaskStatus.IN_PROGRESS, due_date=date(2026, 3, 20), is_blocked=False)

    # Act / Assert
    with pytest.raises(TaskNotFoundError, match="Task not found"):
        task_service.update_task(999, task_update)

    repository.get_task.assert_called_once_with(999)
    repository.save_task.assert_not_called()

def test_update_task_saves_pending_state_with_nullable_fields(task_service: TaskService, repository: Mock):
    """
    update_task should allow description and due_date to be set to None.
    """
    # Arrange
    existing_task = build_task(task_id=1, title="Original title", description="original")
    repository.get_task.return_value = existing_task
    repository.save_task.side_effect = save_task_side_effect

    task_update = UpdateTaskInput(
        title="Updated title",
        description=None,
        status=TaskStatus.PENDING,
        due_date=None,
        is_blocked=False
    )

    # Act
    result = task_service.update_task(1, task_update)

    # Assert
    assert result.id == 1
    assert result.title == "Updated title"
    assert result.description is None
    assert result.status == TaskStatus.PENDING
    assert result.due_date is None
    assert result.is_blocked is False
    assert result.updated_at is not None

    repository.get_task.assert_called_once_with(1)
    repository.save_task.assert_called_once_with(existing_task)

def test_update_task_does_not_save_when_no_real_changes(task_service: TaskService, repository: Mock):
    """
    update_task should not save the task when the payload does not change any field.
    """
    # Arrange
    existing_task = build_task(
        task_id=1,
        title="Original title",
        description="original",
        status=TaskStatus.IN_PROGRESS,
        due_date=date(2026, 3, 20)
    )
    repository.get_task.return_value = existing_task

    task_update = UpdateTaskInput(
        title="Original title",
        description="original",
        status=TaskStatus.IN_PROGRESS,
        due_date=date(2026, 3, 20),
        is_blocked=False
    )

    # Act
    result = task_service.update_task(1, task_update)

    # Assert
    assert result is existing_task
    assert result.updated_at is None

    repository.get_task.assert_called_once_with(1)
    repository.save_task.assert_not_called()

def test_update_task_updates_is_blocked_when_provided(task_service: TaskService, repository: Mock):
    """
    update_task should replace is_blocked when provided in the PUT payload.
    """
    # Arrange
    existing_task = build_task(task_id=1, status=TaskStatus.PENDING, due_date=None)
    repository.get_task.return_value = existing_task
    repository.save_task.side_effect = save_task_side_effect

    task_update = UpdateTaskInput(
        title=existing_task.title,
        description=existing_task.description,
        status=TaskStatus.PENDING,
        due_date=None,
        is_blocked=True
    )

    # Act
    result = task_service.update_task(1, task_update)

    # Assert
    assert result.is_blocked is True
    assert result.updated_at is not None
    repository.get_task.assert_called_once_with(1)
    repository.save_task.assert_called_once_with(existing_task)

def test_update_task_propagates_domain_error_and_does_not_save_when_final_state_is_invalid(task_service: TaskService, repository: Mock) -> None:
    existing_task = build_task(task_id=1, status=TaskStatus.PENDING, due_date=None)
    repository.get_task.return_value = existing_task

    task_update = UpdateTaskInput(
        title=existing_task.title,
        description=existing_task.description,
        status=TaskStatus.IN_PROGRESS,
        due_date=None,
        is_blocked=False
    )

    with pytest.raises(InvalidTaskDueDateError, match="required for IN_PROGRESS tasks"):
        task_service.update_task(1, task_update)

    repository.get_task.assert_called_once_with(1)
    repository.save_task.assert_not_called()