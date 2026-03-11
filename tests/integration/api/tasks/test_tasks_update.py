# tests/tasks/test_tasks_update.py

from app.schemas.task import TaskStatus

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

    updated_status = TaskStatus.in_progress

    created_task = create_task(title=original_title,description=original_description).json()

    task_id = created_task["id"]

    payload = {"title": updated_title, "description": updated_description, "due_date": None, "status": updated_status.value}
    
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

def test_update_task_returns_404_when_task_does_not_exist(client):
    """
    PUT /tasks/{id} should return 404 if the task does not exist.
    """

    # Arrange
    non_existing_id = 999
    payload = {"title": "Updated title","description": "updated", "status": TaskStatus.pending.value, "due_date": None}

    # Act
    response = client.put(f"/tasks/{non_existing_id}", json=payload)

    # Assert
    assert response.status_code == 404

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

    created_task = create_task(title=original_title,description=original_description).json()

    task_id = created_task["id"]

    payload = {"title": patched_title}

    # Act
    response = client.patch(f"/tasks/{task_id}",json=payload)

    # Assert
    assert response.status_code == 200

    data = response.json()

    # validate API contract
    task = parse_response(data)

    assert task.title == patched_title
    assert task.description == original_description
    assert task.updated_at is not None

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

def test_patch_task_with_empty_body_does_not_change_fields(client, create_task, parse_response):
    """
    PATCH /tasks/{id} with an empty body should not modify existing fields.
    """

    # Arrange
    original_title = "Task"
    original_description = "desc"

    created_task = create_task(title=original_title,description=original_description).json()

    task_id = created_task["id"]

    payload = {}

    # Act
    response = client.patch(f"/tasks/{task_id}", json=payload)

    # Assert
    assert response.status_code == 200

    data = response.json()

    # validate API contract
    task = parse_response(data)

    assert task.title == original_title
    assert task.description == original_description