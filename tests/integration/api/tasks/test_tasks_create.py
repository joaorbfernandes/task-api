# tests/tasks/test_tasks_create.py

# ----------------------------------------
# POST /tasks
# ----------------------------------------

def test_create_task_creates_new_task(create_task, parse_response):
    """
    POST /tasks should create a new task.

    The API should:
    - return HTTP 201
    - assign an id
    - set status to 'pending'
    - return the created task
    """

    # Arrange
    expected_title = "My first task"

    # Act
    response = create_task(title=expected_title)

    # Assert
    assert response.status_code == 201

    data = response.json()

    # validate API contract
    task = parse_response(data)

    assert task.id == 1
    assert task.title == "My first task"
    assert task.status == "pending"
    assert task.created_at is not None
    assert task.updated_at is None