# tests/integration/api/tasks/test_tasks_validation.py

import pytest
from app.modules.tasks.domain.task_status import TaskStatus

# ----------------------------------------
# GET /tasks/{id} validation
# ----------------------------------------

def test_get_task_fails_when_id_is_not_an_integer(client):
    """
    GET /tasks/{id} should return 422 when id is not a valid integer.
    """

    # Act
    response = client.get("/tasks/abc")

    # Assert
    assert response.status_code == 422

# ----------------------------------------
# POST /tasks validation
# ----------------------------------------

def test_create_task_fails_when_title_missing(client):
    """
    POST /tasks should return 422 when title is missing.
    """

    # Arrange
    payload = {"description": "testing", "due_date": None}

    # Act
    response = client.post("/tasks", json=payload)

    # Assert
    assert response.status_code == 422

def test_create_task_fails_when_extra_field_provided(client):
    """
    POST /tasks should return 422 when unexpected fields are provided.
    """

    # Arrange
    payload = {"title": "Valid title", "description": "testing", "due_date": None, "unexpected": "value"}

    # Act
    response = client.post("/tasks", json=payload)

    # Assert
    assert response.status_code == 422

@pytest.mark.parametrize("title, expected_status",
    [
        ("ab", 422),        # below minimum
        ("abc", 201),       # minimum valid
        ("a" * 120, 201),   # maximum valid
        ("a" * 121, 422)   # above maximum
    ],
)
def test_create_task_validates_title_length_boundaries(client, title, expected_status):

    # Arrange
    payload = {"title": title, "description": "valid description", "due_date": None}

    # Act
    response = client.post("/tasks", json=payload)

    # Assert
    assert response.status_code == expected_status

@pytest.mark.parametrize("description, expected_status",
    [
        ("", 422),           # below minimum
        ("a", 201),          # minimum valid
        ("a" * 500, 201),    # maximum valid
        ("a" * 501, 422)    # above maximum
    ],
)
def test_create_task_validates_description_length_boundaries(client, description, expected_status):

    # Arrange
    payload = {"title": "valid title", "description": description, "due_date": None}

    # Act
    response = client.post("/tasks", json=payload)

    # Assert
    assert response.status_code == expected_status

def test_create_task_fails_when_title_is_null(client):
    """
    POST /tasks should return 422 when title is explicitly null.
    """

    # Arrange
    payload = {"title": None, "description": "testing", "due_date": None}

    # Act
    response = client.post("/tasks", json=payload)

    # Assert
    assert response.status_code == 422

def test_create_task_fails_when_status_is_provided(client):
    """
    POST /tasks should return 422 when status is provided by the client.
    """

    # Arrange
    payload = {"title": "Valid title", "description": "testing", "due_date": None, "status": TaskStatus.COMPLETED.value}

    # Act
    response = client.post("/tasks", json=payload)

    # Assert
    assert response.status_code == 422

def test_create_task_fails_when_title_has_invalid_type(client):
    """
    POST /tasks should return 422 when title has an invalid type.
    """

    # Arrange
    payload = {"title": 234, "description": "description", "due_date": None}

    # Act
    response = client.post("/tasks", json=payload)

    # Assert
    assert response.status_code == 422

def test_create_task_fails_when_description_has_invalid_type(client):
    """
    POST /tasks should return 422 when description has an invalid type.
    """

    # Arrange
    payload = {"title": "Valid title", "description": 123, "due_date": None}

    # Act
    response = client.post("/tasks", json=payload)

    # Assert
    assert response.status_code == 422

def test_create_task_fails_when_due_date_has_invalid_format(client):
    """
    POST /tasks should return 422 when due_date is not a valid date.
    """

    # Arrange
    payload = {"title": "Valid title", "description": "testing", "due_date": "not-a-date"}

    # Act
    response = client.post("/tasks", json=payload)

    # Assert
    assert response.status_code == 422

# ----------------------------------------
# PUT /tasks validation
# ----------------------------------------

def test_update_task_fails_when_title_missing(client, create_task):
    """
    PUT /tasks/{id} should return 422 when title is missing.
    """

    # Arrange
    task_id = create_task().json()["id"]

    payload = {"description": "updated", "status": TaskStatus.COMPLETED.value, "due_date": None}

    # Act
    response = client.put(f"/tasks/{task_id}", json=payload)

    # Assert
    assert response.status_code == 422

def test_update_task_rejects_null_title(client, create_task):
    """
    PUT /tasks/{id} should return 422 when title is explicitly null.
    """

    # Arrange
    created_task = create_task(title="Original title", description="original").json()
    task_id = created_task["id"]

    payload = {
        "title": None,
        "description": "updated",
        "status": TaskStatus.IN_PROGRESS.value,
        "due_date": None
    }

    # Act
    response = client.put(f"/tasks/{task_id}", json=payload)

    # Assert
    assert response.status_code == 422

def test_update_task_rejects_null_status(client, create_task):
    """
    PUT /tasks/{id} should return 422 when status is explicitly null.
    """

    # Arrange
    created_task = create_task(title="Original title", description="original").json()
    task_id = created_task["id"]

    payload = {
        "title": "title",
        "description": "description",
        "status": None,
        "due_date": None
    }

    # Act
    response = client.put(f"/tasks/{task_id}", json=payload)

    # Assert
    assert response.status_code == 422

def test_update_task_requires_description_field(client, create_task):
    """
    PUT /tasks/{id} should return 422 when description is missing.
    """

    # Arrange
    created_task = create_task(title="Original title", description="original").json()
    task_id = created_task["id"]

    payload = {
        "title": "Updated title",
        "status": TaskStatus.IN_PROGRESS.value,
        "due_date": None
    }

    # Act
    response = client.put(f"/tasks/{task_id}", json=payload)

    # Assert
    assert response.status_code == 422

def test_update_task_requires_due_date_field(client, create_task):
    """
    PUT /tasks/{id} should return 422 when due_date is missing.
    """

    # Arrange
    created_task = create_task(title="Original title", description="original").json()
    task_id = created_task["id"]

    payload = {
        "title": "Updated title",
        "description": "updated",
        "status": TaskStatus.IN_PROGRESS.value
    }

    # Act
    response = client.put(f"/tasks/{task_id}", json=payload)

    # Assert
    assert response.status_code == 422

def test_update_task_fails_when_extra_field_is_provided(client, create_task):
    """
    PUT /tasks/{id} should return 422 when unexpected fields are provided.
    """

    # Arrange
    created_task = create_task(title="Original title", description="original").json()
    task_id = created_task["id"]

    payload = {
        "title": "Updated title",
        "description": "updated",
        "status": TaskStatus.IN_PROGRESS.value,
        "due_date": None,
        "unexpected": "value"
    }

    # Act
    response = client.put(f"/tasks/{task_id}", json=payload)

    # Assert
    assert response.status_code == 422

def test_update_task_fails_when_invalid_title_type(client, create_task):
    """
    PUT /tasks/{id} should return 422 when title has an invalid type
    """

    # Arrange
    task_id = create_task().json()["id"]

    payload = {
        "title": 123,
        "description": "updated",
        "status": TaskStatus.IN_PROGRESS.value,
        "due_date": None
    }

    # Act
    response = client.put(f"/tasks/{task_id}", json=payload)

    # Assert
    assert response.status_code == 422

def test_update_task_fails_when_due_date_has_invalid_format(client, create_task):
    """
    PUT /tasks/{id} should return 422 when due_date is not a valid date.
    """

    # Arrange
    task_id = create_task().json()["id"]

    payload = {
        "title": "Updated title",
        "description": "updated",
        "status": TaskStatus.IN_PROGRESS.value,
        "due_date": "not-a-date"
    }

    # Act
    response = client.put(f"/tasks/{task_id}", json=payload)

    # Assert
    assert response.status_code == 422

def test_update_task_fails_when_status_has_invalid_value(client, create_task):
    """
    PUT /tasks/{id} should return 422 when status has an invalid value.
    """

    # Arrange
    task_id = create_task().json()["id"]

    payload = {
        "title": "Updated title",
        "description": "updated",
        "status": "invalid-status",
        "due_date": None
    }

    # Act
    response = client.put(f"/tasks/{task_id}", json=payload)

    # Assert
    assert response.status_code == 422

def test_update_task_fails_when_description_has_invalid_type(client, create_task):
    """
    PUT /tasks/{id} should return 422 when description has an invalid type.
    """

    # Arrange
    task_id = create_task().json()["id"]

    payload = {
        "title": "Updated title",
        "description": 2344,
        "status": TaskStatus.IN_PROGRESS.value,
        "due_date": None
    }

    # Act
    response = client.put(f"/tasks/{task_id}", json=payload)

    # Assert
    assert response.status_code == 422

def test_update_task_requires_status_field(client, create_task):
    """
    PUT /tasks/{id} should return 422 when status is missing.
    """
    # Arrange
    task_id = create_task().json()["id"]

    payload = {
        "title": "Updated title",
        "description": "updated",
        "due_date": None
    }

    # Act
    response = client.put(f"/tasks/{task_id}", json=payload)

    # Assert
    assert response.status_code == 422

# ----------------------------------------
# PATCH /tasks validation
# ----------------------------------------

def test_patch_task_fails_when_invalid_title_type(client, create_task):
    """
    PATCH /tasks/{id} should return 422 when a title has an invalid type.
    """

    # Arrange
    task_id = create_task().json()["id"]

    payload = {"title": 123}

    # Act
    response = client.patch(f"/tasks/{task_id}", json=payload)

    # Assert
    assert response.status_code == 422

def test_patch_task_fails_when_extra_field_provided(client, create_task):
    """
    PATCH /tasks/{id} should return 422 when unexpected fields are provided.
    """

    # Arrange
    task_id = create_task().json()["id"]

    payload = {"unexpected": "value"}

    # Act
    response = client.patch(f"/tasks/{task_id}", json=payload)

    # Assert
    assert response.status_code == 422

def test_patch_task_rejects_null_title(client, create_task):
    """
    PATCH /tasks/{id} should return 422 when title is explicitly null.
    """

    # Arrange
    created_task = create_task(title="Original title", description="original").json()
    task_id = created_task["id"]

    payload = {"title": None}

    # Act
    response = client.patch(f"/tasks/{task_id}", json=payload)

    # Assert
    assert response.status_code == 422

def test_patch_task_rejects_null_status(client, create_task):
    """
    PATCH /tasks/{id} should return 422 when status is explicitly null.
    """

    # Arrange
    created_task = create_task(title="Original title", description="original").json()
    task_id = created_task["id"]

    payload = {"status": None}

    # Act
    response = client.patch(f"/tasks/{task_id}", json=payload)

    # Assert
    assert response.status_code == 422

def test_patch_task_fails_when_status_has_invalid_value(client, create_task):
    """
    PATCH /tasks/{id} should return 422 when status has an invalid value.
    """

    # Arrange
    task_id = create_task().json()["id"]

    payload = {"status": "invalid-status"}

    # Act
    response = client.patch(f"/tasks/{task_id}", json=payload)

    # Assert
    assert response.status_code == 422

def test_patch_task_fails_when_due_date_has_invalid_format(client, create_task):
    """
    PATCH /tasks/{id} should return 422 when due_date is not a valid date.
    """

    # Arrange
    task_id = create_task().json()["id"]

    payload = {"due_date": "not-a-date"}

    # Act
    response = client.patch(f"/tasks/{task_id}", json=payload)

    # Assert
    assert response.status_code == 422

def test_patch_task_fails_when_description_has_invalid_type(client, create_task):
    """
    PATCH /tasks/{id} should return 422 when description has an invalid type.
    """

    # Arrange
    task_id = create_task().json()["id"]

    payload = {"description": 123}

    # Act
    response = client.patch(f"/tasks/{task_id}", json=payload)

    # Assert
    assert response.status_code == 422

def test_patch_task_fails_when_body_is_empty(client, create_task):
    """
    PATCH /tasks/{id} should return 422 when the request body is empty.
    """

    # Arrange
    task_id = create_task(title="Task", description="desc").json()["id"]
    payload = {}

    # Act
    response = client.patch(f"/tasks/{task_id}", json=payload)

    # Assert
    assert response.status_code == 422

# ----------------------------------------
# DELETE /tasks/{id} validation
# ----------------------------------------

def test_delete_task_fails_when_id_is_not_an_integer(client):
    """
    DELETE /tasks/{id} should return 422 when id is not a valid integer.
    """

    # Act
    response = client.delete("/tasks/abc")

    # Assert
    assert response.status_code == 422