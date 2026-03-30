# tests/integration/api/tasks/test_tasks_create.py

from app.modules.tasks.domain.task_status import TaskStatus
from tests.factories.task import future_date


valid_due_date = future_date()

# ----------------------------------------
# POST /tasks
# ----------------------------------------

def test_create_task_creates_new_task(create_task, parse_response):
    """
    POST /tasks should create a new task.

    The API should:
    - return HTTP 201
    - assign an id
    - set status to TaskStatus.PENDING
    - return the created task
    """

    # Arrange
    expected_title = "My first task"
    expected_description = "testing"

    # Act
    response = create_task(title=expected_title, description=expected_description)

    # Assert
    assert response.status_code == 201

    data = response.json()

    # validate API contract
    task = parse_response(data)

    assert task.id == 1
    assert task.title == expected_title
    assert task.status == TaskStatus.PENDING
    assert task.created_at is not None
    assert task.updated_at is None
    assert task.description == expected_description
    assert task.due_date is None

def test_create_task_allows_null_description(create_task, parse_response):
    """
    POST /tasks should allow description to be null.
    """

    # Arrange
    payload = {
        "title": "Task with null description",
        "description": None,
        "due_date": None,
    }

    # Act
    response = create_task(**payload)

    # Assert
    assert response.status_code == 201

    data = response.json()

    # validate API contract    
    task = parse_response(data)

    assert task.title == payload["title"]
    assert task.description is None
    assert task.status == TaskStatus.PENDING
    assert task.due_date is None

def test_create_task_allows_null_due_date(create_task, parse_response):
    """
    POST /tasks should allow due_date to be null.
    """

    # Arrange
    payload = {
        "title": "Task with null due date",
        "description": "testing",
        "due_date": None,
    }

    # Act
    response = create_task(**payload)

    # Assert
    assert response.status_code == 201

    data = response.json()

    # validate API contract
    task = parse_response(data)

    assert task.title == payload["title"]
    assert task.due_date is None
    assert task.status == TaskStatus.PENDING
    assert task.description == payload["description"]

def test_create_task_trims_title_whitespace(create_task, parse_response):
    """
    POST /tasks should trim surrounding whitespace from title.
    """

    # Arrange
    payload = {
        "title": "   My trimmed title   ",
        "description": "testing",
        "due_date": None,
    }

    # Act
    response = create_task(**payload)

    # Assert
    assert response.status_code == 201

    data = response.json()

    # validate API contract
    task = parse_response(data)

    assert task.title == "My trimmed title"
    assert task.description == payload["description"]
    assert task.due_date is None
    assert task.status == TaskStatus.PENDING

def test_create_task_accepts_full_valid_payload(create_task, parse_response):
    """
    POST /tasks should create a task with all supported create fields.
    """

    # Arrange
    payload = {
        "title": "Full task",
        "description": "Full description",
        "due_date": valid_due_date.isoformat(),
    }

    # Act
    response = create_task(**payload)

    # Assert
    assert response.status_code == 201

    data = response.json()

    # validate API contract
    task = parse_response(data)

    assert task.title == payload["title"]
    assert task.description == payload["description"]
    assert str(task.due_date) == payload["due_date"]
    assert task.status == TaskStatus.PENDING
    assert task.created_at is not None
    assert task.updated_at is None