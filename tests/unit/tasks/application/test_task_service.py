from datetime import date, datetime
from unittest.mock import Mock

import pytest

from app.application.unit_of_work import UnitOfWork
from app.modules.tasks.domain.task import Task
from app.modules.tasks.domain.task_status import TaskStatus
from app.modules.tasks.domain.task_errors import InvalidTaskDueDateError
from app.modules.tasks.application.task_repository import TaskRepository
from app.modules.tasks.application.task_service import TaskNotFoundError, TaskService
from tests.factories.task import build_new_task, build_task, future_date
from app.modules.tasks.application.task_dtos import TaskInput, PatchTaskInput

valid_due_date = future_date()

@pytest.fixture
def repository() -> Mock:
    return Mock(spec=TaskRepository)


@pytest.fixture
def uow() -> Mock:
    return Mock(spec=UnitOfWork)


@pytest.fixture
def task_service(repository: Mock, uow: Mock) -> TaskService:
    return TaskService(repository=repository, uow=uow)


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
    existing_task = build_new_task( title="Task 1")
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
# list_tasks
# ----------------------------------------

def test_list_tasks_returns_tasks_from_repository(task_service: TaskService, repository: Mock):
    """
    list_tasks should return the tasks provided by the repository.
    """
    # Arrange
    stored_tasks = [build_task( title="Task 1"), build_task(title="Task 2")]
    repository.list_tasks.return_value = stored_tasks

    # Act
    result = task_service.list_tasks()

    # Assert
    assert result == stored_tasks
    repository.list_tasks.assert_called_once_with()

# ----------------------------------------
# create_task
# ----------------------------------------

def test_create_task_delegates_creation_to_repository_with_default_status_and_commits(
    task_service: TaskService,
    repository: Mock,
    uow: Mock,
) -> None:
    """
    create_task should build a domain Task, delegate creation to the repository,
    and commit the transaction on success.
    """
    # Arrange
    task_input = TaskInput(
        title="My first task",
        description="testing",
        due_date=None,
        is_blocked=False,
        status=TaskStatus.PENDING,
    )
    created_task = build_new_task(
        title="My first task",
        description="testing",
        due_date=None,
        is_blocked=False,
    )
    repository.create_task.return_value = created_task

    # Act
    result = task_service.create_task(task_input)

    # Assert
    assert result == created_task
    repository.create_task.assert_called_once()
    uow.commit.assert_called_once()
    uow.rollback.assert_not_called()

    create_data = repository.create_task.call_args.args[0]
    assert isinstance(create_data, Task)
    assert create_data.title == "My first task"
    assert create_data.description == "testing"
    assert create_data.status == TaskStatus.PENDING
    assert create_data.due_date is None
    assert create_data.is_blocked is False
    assert isinstance(create_data.created_at, datetime)


def test_create_task_passes_due_date_to_repository_and_commits(
    task_service: TaskService,
    repository: Mock,
    uow: Mock,
) -> None:
    """
    create_task should pass due_date to the repository and commit on success.
    """
    # Arrange
    task_input = TaskInput(
        title="Task with due date",
        description="testing",
        due_date=valid_due_date,
        is_blocked=False,
        status=TaskStatus.PENDING,
    )
    created_task = build_new_task(
        title="Task with due date",
        description="testing",
        due_date=valid_due_date,
        is_blocked=False,
    )
    repository.create_task.return_value = created_task

    # Act
    result = task_service.create_task(task_input)

    # Assert
    assert result == created_task
    repository.create_task.assert_called_once()
    uow.commit.assert_called_once()
    uow.rollback.assert_not_called()

    create_data = repository.create_task.call_args.args[0]
    assert isinstance(create_data, Task)
    assert create_data.title == "Task with due date"
    assert create_data.description == "testing"
    assert create_data.status == TaskStatus.PENDING
    assert create_data.due_date == valid_due_date
    assert create_data.is_blocked is False
    assert isinstance(create_data.created_at, datetime)


def test_create_task_passes_is_blocked_to_repository_and_commits(
    task_service: TaskService,
    repository: Mock,
    uow: Mock,
) -> None:
    """
    create_task should pass is_blocked to the repository and commit on success.
    """
    # Arrange
    task_input = TaskInput(
        title="Blocked task",
        description="testing",
        due_date=None,
        is_blocked=True,
        status=TaskStatus.PENDING,
    )
    created_task = build_new_task(
        title="Blocked task",
        description="testing",
        due_date=None,
        is_blocked=True,
    )
    repository.create_task.return_value = created_task

    # Act
    result = task_service.create_task(task_input)

    # Assert
    assert result == created_task
    repository.create_task.assert_called_once()
    uow.commit.assert_called_once()
    uow.rollback.assert_not_called()

    create_data = repository.create_task.call_args.args[0]
    assert isinstance(create_data, Task)
    assert create_data.title == "Blocked task"
    assert create_data.description == "testing"
    assert create_data.status == TaskStatus.PENDING
    assert create_data.due_date is None
    assert create_data.is_blocked is True
    assert isinstance(create_data.created_at, datetime)


def test_create_task_rolls_back_when_repository_create_fails(
    task_service: TaskService,
    repository: Mock,
    uow: Mock,
) -> None:
    """
    create_task should roll back and re-raise when repository.create_task fails.
    """
    # Arrange
    task_input = TaskInput(
        title="My first task",
        description="testing",
        due_date=None,
        is_blocked=False,
        status=TaskStatus.PENDING,
    )
    repository.create_task.side_effect = RuntimeError("DB error")

    # Act / Assert
    with pytest.raises(RuntimeError, match="DB error"):
        task_service.create_task(task_input)

    repository.create_task.assert_called_once()
    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()

# ----------------------------------------
# update_task
# ----------------------------------------

def test_update_task_replaces_task_data_saves_it_and_commits(
    task_service: TaskService,
    repository: Mock,
    uow: Mock,
) -> None:
    """
    update_task should fully replace task fields, save the updated task,
    and commit the transaction when a real change happens.
    """
    # Arrange
    existing_task = build_task(title="Original title", description="original", due_date=None)
    repository.get_task.return_value = existing_task

    task_update = TaskInput(
        title="Updated title",
        description="updated",
        status=TaskStatus.IN_PROGRESS,
        due_date=valid_due_date,
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
    assert result.due_date == valid_due_date
    assert result.is_blocked is True
    assert result.created_at == existing_task.created_at
    assert result.updated_at is not None

    repository.get_task.assert_called_once_with(1)
    repository.save_task.assert_called_once_with(existing_task)
    uow.commit.assert_called_once()
    uow.rollback.assert_not_called()


def test_update_task_raises_and_rolls_back_when_repository_returns_none(
    task_service: TaskService,
    repository: Mock,
    uow: Mock,
) -> None:
    """
    update_task should raise TaskNotFoundError and roll back when the repository does not find the task.
    """
    # Arrange
    repository.get_task.return_value = None
    task_update = TaskInput(
        title="Updated title",
        description="updated",
        status=TaskStatus.IN_PROGRESS,
        due_date=date(2026, 3, 20),
        is_blocked=False,
    )

    # Act / Assert
    with pytest.raises(TaskNotFoundError, match="Task not found"):
        task_service.update_task(999, task_update)

    repository.get_task.assert_called_once_with(999)
    repository.save_task.assert_not_called()
    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


def test_update_task_saves_pending_state_with_nullable_fields_and_commits(
    task_service: TaskService,
    repository: Mock,
    uow: Mock,
) -> None:
    """
    update_task should allow description and due_date to be set to None
    and commit when a real change happens.
    """
    # Arrange
    existing_task = build_task(title="Original title", description="original")
    repository.get_task.return_value = existing_task
    repository.save_task.side_effect = save_task_side_effect

    task_update = TaskInput(
        title="Updated title",
        description=None,
        status=TaskStatus.PENDING,
        due_date=None,
        is_blocked=False,
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
    uow.commit.assert_called_once()
    uow.rollback.assert_not_called()


def test_update_task_does_not_save_or_commit_when_no_real_changes(
    task_service: TaskService,
    repository: Mock,
    uow: Mock,
) -> None:
    """
    update_task should not save or commit when the payload does not change any field.
    """
    # Arrange
    existing_task = build_new_task(
        title="Original title",
        description="original",
        status=TaskStatus.IN_PROGRESS,
        due_date=valid_due_date,
    )
    repository.get_task.return_value = existing_task

    task_update = TaskInput(
        title="Original title",
        description="original",
        status=TaskStatus.IN_PROGRESS,
        due_date=valid_due_date,
        is_blocked=False,
    )

    # Act
    result = task_service.update_task(1, task_update)

    # Assert
    assert result is existing_task
    assert result.updated_at is None

    repository.get_task.assert_called_once_with(1)
    repository.save_task.assert_not_called()
    uow.commit.assert_not_called()
    uow.rollback.assert_not_called()


def test_update_task_updates_is_blocked_when_provided_and_commits(
    task_service: TaskService,
    repository: Mock,
    uow: Mock,
) -> None:
    """
    update_task should replace is_blocked when provided in the PUT payload
    and commit when a real change happens.
    """
    # Arrange
    existing_task = build_new_task(status=TaskStatus.PENDING, due_date=None)
    repository.get_task.return_value = existing_task
    repository.save_task.side_effect = save_task_side_effect

    task_update = TaskInput(
        title=existing_task.title,
        description=existing_task.description,
        status=TaskStatus.PENDING,
        due_date=None,
        is_blocked=True,
    )

    # Act
    result = task_service.update_task(1, task_update)

    # Assert
    assert result.is_blocked is True
    assert result.updated_at is not None

    repository.get_task.assert_called_once_with(1)
    repository.save_task.assert_called_once_with(existing_task)
    uow.commit.assert_called_once()
    uow.rollback.assert_not_called()


def test_update_task_propagates_domain_error_rolls_back_and_does_not_save_when_final_state_is_invalid(
    task_service: TaskService,
    repository: Mock,
    uow: Mock,
) -> None:
    """
    update_task should propagate domain validation errors, avoid saving,
    and roll back the transaction.
    """
    # Arrange
    existing_task = build_new_task(status=TaskStatus.PENDING, due_date=None)
    repository.get_task.return_value = existing_task

    task_update = TaskInput(
        title=existing_task.title,
        description=existing_task.description,
        status=TaskStatus.IN_PROGRESS,
        due_date=None,
        is_blocked=False,
    )

    # Act / Assert
    with pytest.raises(InvalidTaskDueDateError, match="Due date is required for IN PROGRESS tasks"):
        task_service.update_task(1, task_update)

    repository.get_task.assert_called_once_with(1)
    repository.save_task.assert_not_called()
    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()

# ----------------------------------------
# patch_task
# ----------------------------------------

def test_patch_task_updates_only_provided_fields_saves_and_commits(
    task_service: TaskService,
    repository: Mock,
    uow: Mock,
) -> None:
    """
    patch_task should update only the provided fields, save the task,
    and commit when a real change happens.
    """
    # Arrange
    existing_task = build_new_task(
        title="Original title",
        description="original",
        status=TaskStatus.PENDING,
        due_date=valid_due_date,
        is_blocked=False,
    )
    repository.get_task.return_value = existing_task
    repository.save_task.side_effect = save_task_side_effect

    task_patch = PatchTaskInput(
        description="updated description",
        description_provided=True,
    )

    # Act
    result = task_service.patch_task(1, task_patch)

    # Assert
    assert result.title == "Original title"
    assert result.description == "updated description"
    assert result.status == TaskStatus.PENDING
    assert result.due_date == valid_due_date
    assert result.is_blocked is False
    assert result.updated_at is not None

    repository.get_task.assert_called_once_with(1)
    repository.save_task.assert_called_once_with(existing_task)
    uow.commit.assert_called_once()
    uow.rollback.assert_not_called()


def test_patch_task_allows_description_to_be_cleared_saves_and_commits(
    task_service: TaskService,
    repository: Mock,
    uow: Mock,
) -> None:
    """
    patch_task should allow clearing description, save the task,
    and commit when a real change happens.
    """
    # Arrange
    existing_task = build_new_task(
        description="original",
        due_date=valid_due_date,
    )
    repository.get_task.return_value = existing_task
    repository.save_task.side_effect = save_task_side_effect

    task_patch = PatchTaskInput(
        description=None,
        description_provided=True,
    )

    # Act
    result = task_service.patch_task(1, task_patch)

    # Assert
    assert result.description is None
    assert result.updated_at is not None

    repository.get_task.assert_called_once_with(1)
    repository.save_task.assert_called_once_with(existing_task)
    uow.commit.assert_called_once()
    uow.rollback.assert_not_called()


def test_patch_task_does_not_save_or_commit_when_patch_does_not_change_state(
    task_service: TaskService,
    repository: Mock,
    uow: Mock,
) -> None:
    """
    patch_task should not save or commit when the final state is unchanged.
    """
    # Arrange
    existing_task = build_new_task(
        title="Original title",
        description="original",
        status=TaskStatus.PENDING,
        due_date=valid_due_date,
        is_blocked=False,
    )
    repository.get_task.return_value = existing_task

    task_patch = PatchTaskInput(
        title="Original title",
        title_provided=True,
    )

    # Act
    result = task_service.patch_task(1, task_patch)

    # Assert
    assert result is existing_task
    assert result.updated_at is None

    repository.get_task.assert_called_once_with(1)
    repository.save_task.assert_not_called()
    uow.commit.assert_not_called()
    uow.rollback.assert_not_called()


def test_patch_task_raises_and_rolls_back_when_repository_returns_none(
    task_service: TaskService,
    repository: Mock,
    uow: Mock,
) -> None:
    """
    patch_task should raise TaskNotFoundError and roll back when the task does not exist.
    """
    # Arrange
    repository.get_task.return_value = None

    task_patch = PatchTaskInput(
        description="updated",
        description_provided=True,
    )

    # Act / Assert
    with pytest.raises(TaskNotFoundError, match="Task not found"):
        task_service.patch_task(999, task_patch)

    repository.get_task.assert_called_once_with(999)
    repository.save_task.assert_not_called()
    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


def test_patch_task_propagates_domain_error_rolls_back_and_does_not_save_when_final_state_is_invalid(
    task_service: TaskService,
    repository: Mock,
    uow: Mock,
) -> None:
    """
    patch_task should propagate domain validation errors, avoid saving,
    and roll back the transaction.
    """
    # Arrange
    existing_task = build_new_task(
        status=TaskStatus.PENDING,
        due_date=None,
        is_blocked=False,
    )
    repository.get_task.return_value = existing_task

    task_patch = PatchTaskInput(
        status=TaskStatus.IN_PROGRESS,
        status_provided=True,
    )

    # Act / Assert
    with pytest.raises(InvalidTaskDueDateError, match="Due date is required for IN PROGRESS tasks"):
        task_service.patch_task(1, task_patch)

    repository.get_task.assert_called_once_with(1)
    repository.save_task.assert_not_called()
    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()

# ----------------------------------------
# delete_task
# ----------------------------------------

def test_delete_task_calls_repository_delete_and_commits_when_task_exists(
    task_service: TaskService,
    repository: Mock,
    uow: Mock,
) -> None:
    """
    delete_task should call repository.delete_task and commit when the task exists.
    """
    # Arrange
    existing_task = build_new_task(title="Task to delete")
    repository.get_task.return_value = existing_task

    # Act
    task_service.delete_task(1)

    # Assert
    repository.get_task.assert_called_once_with(1)
    repository.delete_task.assert_called_once_with(1)
    uow.commit.assert_called_once()
    uow.rollback.assert_not_called()


def test_delete_task_raises_and_rolls_back_when_repository_returns_none(
    task_service: TaskService,
    repository: Mock,
    uow: Mock,
) -> None:
    """
    delete_task should raise TaskNotFoundError and roll back when the task does not exist.
    """
    # Arrange
    repository.get_task.return_value = None

    # Act / Assert
    with pytest.raises(TaskNotFoundError, match="Task not found"):
        task_service.delete_task(999)

    repository.get_task.assert_called_once_with(999)
    repository.delete_task.assert_not_called()
    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()