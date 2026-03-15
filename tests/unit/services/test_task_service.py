# tests/unit/services/test_task_service.py

import pytest
from datetime import date, datetime
from unittest.mock import Mock

from app.repositories.task_repository import Task, TaskRepository
from app.schemas.task import TaskCreate, TaskPatch, TaskStatus, TaskUpdate
from app.services.task_service import TaskNotFoundError, TaskService


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

def build_task(
    task_id: int = 1,
    title: str = "Test task",
    description: str | None = "testing",
    status: TaskStatus = TaskStatus.PENDING,
    due_date: date | None = None,
    created_at: datetime | None = None,
    updated_at: datetime | None = None
) -> Task:
    """
    Build a Task object for service tests.
    """
    return Task(
        id=task_id,
        title=title,
        description=description,
        status=status,
        due_date=due_date,
        created_at=created_at or datetime(2026, 3, 14, 12, 0, 0),
        updated_at=updated_at
    )


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
    task_input = TaskCreate(title="My first task", description="testing", due_date=None)
    repository.next_id.return_value = 1

    repository.save_task.side_effect = save_task_side_effect

    # Act
    result = task_service.create_task(task_input)

    # Assert
    assert result.id == 1
    assert result.title == "My first task"
    assert result.description == "testing"
    assert result.status == TaskStatus.PENDING
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
    assert saved_task.due_date is None
    assert saved_task.created_at is not None
    assert saved_task.updated_at is None

def test_create_task_accepts_due_date_when_provided(task_service: TaskService, repository: Mock):
    """
    create_task should include due_date in the created Task when provided.
    """
    # Arrange
    task_input = TaskCreate(title="Task with due date", description="testing", due_date=date(2026, 3, 20))
    repository.next_id.return_value = 1

    repository.save_task.side_effect = save_task_side_effect

    # Act
    result = task_service.create_task(task_input)

    # Assert
    assert result.id == 1
    assert result.title == "Task with due date"
    assert result.description == "testing"
    assert result.status == TaskStatus.PENDING
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
    assert saved_task.due_date == date(2026, 3, 20)
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

    task_update = TaskUpdate(title="Updated title", description="updated", status=TaskStatus.IN_PROGRESS, due_date=date(2026, 3, 20))

    repository.save_task.side_effect = save_task_side_effect

    # Act
    result = task_service.update_task(1, task_update)

    # Assert
    assert result.id == 1
    assert result.title == "Updated title"
    assert result.description == "updated"
    assert result.status == TaskStatus.IN_PROGRESS
    assert result.due_date == date(2026, 3, 20)
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
    task_update = TaskUpdate(title="Updated title", description="updated", status=TaskStatus.IN_PROGRESS, due_date=None)

    # Act / Assert
    with pytest.raises(TaskNotFoundError, match="Task not found"):
        task_service.update_task(999, task_update)

    repository.get_task.assert_called_once_with(999)
    repository.save_task.assert_not_called()

def test_update_task_allows_description_and_due_date_to_be_none(task_service: TaskService, repository: Mock):
    """
    update_task should allow description and due_date to be set to None.
    """
    # Arrange
    existing_task = build_task(task_id=1, title="Original title", description="original")
    repository.get_task.return_value = existing_task

    task_update = TaskUpdate(title="Updated title", description=None, status=TaskStatus.IN_PROGRESS, due_date=None)

    repository.save_task.side_effect = lambda task: task

    # Act
    result = task_service.update_task(1, task_update)

    # Assert
    assert result.id == 1
    assert result.title == "Updated title"
    assert result.description is None
    assert result.status == TaskStatus.IN_PROGRESS
    assert result.due_date is None
    assert result.updated_at is not None

    repository.get_task.assert_called_once_with(1)
    repository.save_task.assert_called_once_with(existing_task)

# ----------------------------------------
# patch_task
# ----------------------------------------

def test_patch_task_updates_only_title_when_title_is_provided(task_service: TaskService, repository: Mock):
    """
    patch_task should update only the title when title is explicitly provided.
    """
    # Arrange
    existing_task = build_task(task_id=1, title="Original title")
    existing_task.description = "original description"
    existing_task.due_date = None

    repository.get_task.return_value = existing_task

    task_patch = TaskPatch(title="Patched title")

    repository.save_task.side_effect = save_task_side_effect

    # Act
    result = task_service.patch_task(1, task_patch)

    # Assert
    assert result.id == 1
    assert result.title == "Patched title"
    assert result.description == "original description"
    assert result.status == TaskStatus.PENDING
    assert result.due_date is None
    assert result.updated_at is not None

    repository.get_task.assert_called_once_with(1)
    repository.save_task.assert_called_once_with(existing_task)

def test_patch_task_updates_description_to_none_when_explicitly_provided(task_service: TaskService, repository: Mock):
    """
    patch_task should update description to None when it is explicitly provided.
    """
    # Arrange
    existing_task = build_task(task_id=1, title="Original title")
    existing_task.description = "original description"
    existing_task.due_date = None

    repository.get_task.return_value = existing_task

    task_patch = TaskPatch(description=None)

    repository.save_task.side_effect = save_task_side_effect

    # Act
    result = task_service.patch_task(1, task_patch)

    # Assert
    assert result.id == 1
    assert result.title == "Original title"
    assert result.description is None
    assert result.status == TaskStatus.PENDING
    assert result.due_date is None
    assert result.updated_at is not None

    repository.get_task.assert_called_once_with(1)
    repository.save_task.assert_called_once_with(existing_task)

def test_patch_task_updates_status_when_explicitly_provided(task_service: TaskService, repository: Mock):
    """
    patch_task should update status when it is explicitly provided.
    """
    # Arrange
    existing_task = build_task(task_id=1, title="Original title")
    existing_task.description = "original description"
    existing_task.due_date = None

    repository.get_task.return_value = existing_task

    task_patch = TaskPatch(status=TaskStatus.COMPLETED)

    repository.save_task.side_effect = save_task_side_effect

    # Act
    result = task_service.patch_task(1, task_patch)

    # Assert
    assert result.id == 1
    assert result.title == "Original title"
    assert result.description == "original description"
    assert result.status == TaskStatus.COMPLETED
    assert result.due_date is None
    assert result.updated_at is not None

    repository.get_task.assert_called_once_with(1)
    repository.save_task.assert_called_once_with(existing_task)

def test_patch_task_updates_due_date_when_explicitly_provided(task_service: TaskService, repository: Mock):
    """
    patch_task should update due_date when it is explicitly provided.
    """
    # Arrange
    existing_task = build_task(task_id=1, title="Original title")
    existing_task.description = "original description"
    existing_task.due_date = None

    repository.get_task.return_value = existing_task

    task_patch = TaskPatch(due_date=date(2026, 3, 20))

    repository.save_task.side_effect = save_task_side_effect

    # Act
    result = task_service.patch_task(1, task_patch)

    # Assert
    assert result.id == 1
    assert result.title == "Original title"
    assert result.description == "original description"
    assert result.status == TaskStatus.PENDING
    assert result.due_date == date(2026, 3, 20)
    assert result.updated_at is not None

    repository.get_task.assert_called_once_with(1)
    repository.save_task.assert_called_once_with(existing_task)

def test_patch_task_keeps_existing_fields_when_patch_body_is_empty(task_service: TaskService, repository: Mock):
    """
    patch_task should keep existing fields unchanged when no patch fields are provided.
    """
    # Arrange
    existing_task = build_task(task_id=1, title="Original title", description = "original description", due_date = date(2026, 3, 20))

    repository.get_task.return_value = existing_task

    task_patch = TaskPatch()

    repository.save_task.side_effect = save_task_side_effect

    # Act
    result = task_service.patch_task(1, task_patch)

    # Assert
    assert result.id == 1
    assert result.title == "Original title"
    assert result.description == "original description"
    assert result.status == TaskStatus.PENDING
    assert result.due_date == date(2026, 3, 20)
    assert result.updated_at is not None

    repository.get_task.assert_called_once_with(1)
    repository.save_task.assert_called_once_with(existing_task)

def test_patch_task_raises_when_repository_returns_none(task_service: TaskService, repository: Mock):
    """
    patch_task should raise TaskNotFoundError when the repository does not find the task.
    """
    # Arrange
    repository.get_task.return_value = None
    task_patch = TaskPatch(title="Patched title")

    # Act / Assert
    with pytest.raises(TaskNotFoundError, match="Task not found"):
        task_service.patch_task(999, task_patch)

    repository.get_task.assert_called_once_with(999)
    repository.save_task.assert_not_called()