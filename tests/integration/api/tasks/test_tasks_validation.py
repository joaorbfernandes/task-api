# tests/tasks/test_tasks_validation.py

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


def test_create_task_fails_when_title_too_short(client):
    """
    Title must have at least 3 characters.
    """

    # Arrange
    payload = {"title": "ab", "description": "testing", "due_date": None}

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

# ----------------------------------------
# PUT /tasks validation
# ----------------------------------------

def test_update_task_fails_when_title_missing(client, create_task):
    """
    PUT /tasks/{id} should return 422 when required fields are missing.
    """

    # Arrange
    task_id = create_task().json()["id"]

    payload = {"description": "updated", "due_date": None}

    # Act
    response = client.put(f"/tasks/{task_id}", json=payload)

    # Assert
    assert response.status_code == 422

# ----------------------------------------
# PATCH /tasks validation
# ----------------------------------------

def test_patch_task_fails_when_invalid_type(client, create_task):
    """
    PATCH /tasks/{id} should return 422 when a field has an invalid type.
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