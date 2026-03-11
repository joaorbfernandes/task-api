# tests/tasks/test_tasks_read.py

# ----------------------------------------
# GET /tasks
# ----------------------------------------

def test_list_tasks_returns_empty_list_when_no_tasks_exist(client):
    """
    When the API starts and no tasks were created,
    GET /tasks should return an empty list.
    """

    # Arrange
    # storage is empty

    # Act
    response = client.get("/tasks")

    # Assert
    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    assert data == []

def test_list_tasks_returns_created_tasks(client, create_task, parse_response):

    # Arrange
    expected_title = "task 1"
    create_task(title=expected_title)

    # Act
    response = client.get("/tasks")

    # Assert
    assert response.status_code == 200

    data = response.json()

    # validate API contract
    tasks = parse_response(data)

    assert tasks[0].id == 1
    assert tasks[0].title == expected_title

def test_list_tasks_returns_multiple_tasks(client, create_task, parse_response):
    """
    GET /tasks should return all created tasks.
    """

    # Arrange
    title_1 = "task 1"
    title_2 = "task 2"

    create_task(title=title_1)
    create_task(title=title_2)

    # Act
    response = client.get("/tasks")

    # Assert
    assert response.status_code == 200

    data = response.json()

    # validate API contract
    tasks = parse_response(data)

    assert len(tasks) == 2

    titles = [task.title for task in tasks]

    assert title_1 in titles
    assert title_2 in titles

# ----------------------------------------
# GET /tasks/{id}
# ----------------------------------------

def test_get_task_returns_task_by_id(client, create_task, parse_response):
    """
    GET /tasks/{id} should return the task when it exists.

    Flow:
    1. Create a task
    2. Request the task by id
    3. Validate the returned data
    """

    # Arrange
    expected_title = "Task for retrieval"
    task = create_task(title=expected_title).json()
    task_id = task["id"]

    # Act
    response = client.get(f"/tasks/{task_id}")

    # Assert
    assert response.status_code == 200

    # validate API contract
    data = response.json()

    # validate API contract
    task = parse_response(data)

    assert task.id == task_id
    assert task.title == expected_title
    assert task.status == "pending"

def test_get_task_returns_404_when_task_does_not_exist(client):
    """
    GET /tasks/{id} should return 404 if the task does not exist.
    """

    # Arrange
    non_existing_id = 999

    # Act
    response = client.get(f"/tasks/{non_existing_id}")

    # Assert
    assert response.status_code == 404