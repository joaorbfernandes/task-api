# tests/tasks/test_tasks_update.py

from app.domain.enums.task_status import TaskStatus
from tests.factories.task import future_date

valid_due_date = future_date()

# ----------------------------------------
# PUT /tasks/{id}
# ----------------------------------------

def test_update_task_replaces_task_data(client, create_task, parse_response):
    """
    PUT /tasks/{id} should replace the task data.
    """

    # Arrange
    original_title = "Original title"
    original_description = "original"

    updated_title = "Updated title"
    updated_description = "updated"
    updated_status = TaskStatus.IN_PROGRESS

    created_task = create_task(title=original_title, description=original_description).json()

    task_id = created_task["id"]

    payload = {"title": updated_title, "description": updated_description, "due_date": valid_due_date.isoformat(), "status": updated_status.value, "is_blocked": False}
    
    # Act
    response = client.put(f"/tasks/{task_id}",json=payload)

    # Assert
    assert response.status_code == 200

    data = response.json()

    # validate API contract
    task = parse_response(data)

    assert task.id == task_id
    assert task.title == updated_title
    assert task.description == updated_description
    assert task.status == updated_status
    assert task.updated_at is not None
    assert task.due_date == valid_due_date
    assert task.created_at is not None

def test_update_task_returns_404_when_task_does_not_exist(client):
    """
    PUT /tasks/{id} should return 404 if the task does not exist.
    """

    # Arrange
    non_existing_id = 999
    payload = {"title": "Updated title","description": "updated", "status": TaskStatus.PENDING.value, "due_date": None, "is_blocked": False}

    # Act
    response = client.put(f"/tasks/{non_existing_id}", json=payload)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

def test_update_task_allows_null_description(client, create_task, parse_response):
    """
    PUT /tasks/{id} should allow description to be explicitly set to null.
    """

    # Arrange
    created_task = create_task(title="Original title", description="original").json()
    task_id = created_task["id"]

    payload = {
        "title": "Updated title",
        "description": None,
        "status": TaskStatus.IN_PROGRESS.value,
        "due_date": valid_due_date.isoformat(),
        "is_blocked": False
    }

    # Act
    response = client.put(f"/tasks/{task_id}", json=payload)

    # Assert
    assert response.status_code == 200

    data = response.json()

    # valid API contract
    task = parse_response(data)

    assert task.title == "Updated title"
    assert task.description is None
    assert task.status == TaskStatus.IN_PROGRESS
    assert task.due_date == valid_due_date
    assert task.updated_at is not None

def test_update_task_allows_null_due_date(client, create_task, parse_response):
    """
    PUT /tasks/{id} should allow due_date to be explicitly set to null.
    """

    # Arrange
    created_task = create_task(
        title="Original title",
        description="original",
        due_date="2026-03-20",
    ).json()
    task_id = created_task["id"]


    payload = {
        "title": "Updated title",
        "description": "updated",
        "status": TaskStatus.PENDING.value,
        "due_date": valid_due_date.isoformat(),
        "is_blocked": False
    }

    # Act
    response = client.put(f"/tasks/{task_id}", json=payload)

    # Assert
    assert response.status_code == 200

    data = response.json()

    # validate API contract
    task = parse_response(data)

    assert task.title == "Updated title"
    assert task.description == "updated"
    assert task.status == TaskStatus.PENDING
    assert task.due_date == valid_due_date
    assert task.updated_at is not None

# ----------------------------------------
# PATCH /tasks/{id}
# ----------------------------------------

def test_patch_task_updates_only_provided_fields(client, create_task, parse_response):
    """
    PATCH /tasks/{id} should update only the fields provided.
    """

    # Arrange
    original_title = "Original title"
    original_description = "original description"
    patched_title = "Patched title"

    created_task = create_task(title=original_title, description=original_description).json()

    task_id = created_task["id"]

    payload = {"title": patched_title}

    # Act
    response = client.patch(f"/tasks/{task_id}",json=payload)

    # Assert
    assert response.status_code == 200

    data = response.json()

    # validate API contract
    task = parse_response(data)

    assert task.id == task_id   
    assert task.title == patched_title
    assert task.description == original_description
    assert task.updated_at is not None
    assert task.status == TaskStatus.PENDING

def test_patch_task_returns_404_when_task_does_not_exist(client):
    """
    PATCH /tasks/{id} should return 404 if the task does not exist.
    """

    # Arrange
    non_existing_id = 999
    payload = {"title": "Patched title"}

    # Act
    response = client.patch(f"/tasks/{non_existing_id}", json=payload)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

def test_patch_task_allows_null_description(client, create_task, parse_response):
    """
    PATCH /tasks/{id} should allow description to be explicitly set to null.
    """

    # Arrange
    created_task = create_task(title="Original title", description="original").json()
    task_id = created_task["id"]

    payload = {"description": None}

    # Act
    response = client.patch(f"/tasks/{task_id}", json=payload)

    # Assert
    assert response.status_code == 200

    data = response.json()

    # validate API contract
    task = parse_response(data)

    assert task.title == "Original title"
    assert task.description is None
    assert task.status == TaskStatus.PENDING
    assert task.due_date is None
    assert task.updated_at is not None

def test_patch_task_allows_null_due_date(client, create_task, parse_response):
    """
    PATCH /tasks/{id} should allow due_date to be explicitly set to null.
    """

    # Arrange
    original_title = "Original title"
    original_description = "original"

    created_task = create_task(
        title=original_title,
        description=original_description,
        due_date=valid_due_date.isoformat(),
    ).json()
    task_id = created_task["id"]

    payload = {"due_date": None}

    # Act
    response = client.patch(f"/tasks/{task_id}", json=payload)

    # Assert
    assert response.status_code == 200

    data = response.json()

    # validate API contract
    task = parse_response(data)

    assert task.title == original_title
    assert task.description == original_description
    assert task.status == TaskStatus.PENDING
    assert task.due_date is None
    assert task.updated_at is not None