# tests/unit/repositories/test_task_repository.py

from datetime import datetime

import pytest

from app.repositories.task_repository import InMemoryTaskRepository, Task
from app.schemas.task import TaskStatus


@pytest.fixture
def repository() -> InMemoryTaskRepository:
    """
    Return a fresh in-memory task repository for each test.
    """
    return InMemoryTaskRepository()


def build_task(task_id: int, title: str = "Test task") -> Task:
    """
    Build a task object for repository tests.
    """
    now = datetime(2026, 3, 14, 12, 0, 0)

    return Task(
        id=task_id,
        title=title,
        description="testing",
        status=TaskStatus.PENDING,
        due_date=None,
        created_at=now,
        updated_at=None,
    )


def test_next_id_returns_incremental_ids(repository: InMemoryTaskRepository):
    """
    next_id should return incremental ids.
    """
    # Arrange

    # Act
    first_id = repository.next_id()
    second_id = repository.next_id()

    # Assert
    assert first_id == 1
    assert second_id == 2


def test_list_tasks_returns_empty_list_when_repository_is_empty(repository: InMemoryTaskRepository):
    """
    list_tasks should return an empty list when no tasks were saved.
    """
    # Arrange

    # Act
    tasks = repository.list_tasks()

    # Assert
    assert tasks == []


def test_save_task_stores_task(repository: InMemoryTaskRepository):
    """
    save_task should store a task and return it.
    """
    # Arrange
    task = build_task(task_id=1, title="Task 1")

    # Act
    saved_task = repository.save_task(task)

    # Assert
    assert saved_task == task
    assert repository.get_task(1) == task


def test_get_task_returns_none_when_task_does_not_exist(repository: InMemoryTaskRepository):
    """
    get_task should return None when the task does not exist.
    """
    # Arrange
    non_existing_id = 999

    # Act
    task = repository.get_task(non_existing_id)

    # Assert
    assert task is None


def test_list_tasks_returns_saved_tasks(repository: InMemoryTaskRepository):
    """
    list_tasks should return all saved tasks.
    """
    # Arrange
    task_1 = build_task(task_id=1, title="Task 1")
    task_2 = build_task(task_id=2, title="Task 2")

    repository.save_task(task_1)
    repository.save_task(task_2)

    # Act
    tasks = repository.list_tasks()

    # Assert
    assert len(tasks) == 2
    assert task_1 in tasks
    assert task_2 in tasks


def test_delete_task_removes_existing_task(repository: InMemoryTaskRepository):
    """
    delete_task should remove a stored task.
    """
    # Arrange
    task = build_task(task_id=1)
    repository.save_task(task)

    # Act
    repository.delete_task(1)

    # Assert
    assert repository.get_task(1) is None

def test_save_task_replaces_existing_task_with_same_id(repository: InMemoryTaskRepository):
    """
    save_task should replace an existing task with the same id.
    """
    # Arrange
    original_task = build_task(task_id=1, title="Original")
    updated_task = build_task(task_id=1, title="Updated")

    repository.save_task(original_task)

    # Act
    repository.save_task(updated_task)

    # Assert
    stored_task = repository.get_task(1)
    assert stored_task == updated_task
    assert stored_task.title == "Updated"