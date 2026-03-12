# tests/tasks/test_tasks_delete.py

# ----------------------------------------
# DELETE /tasks/{id}
# ----------------------------------------

def test_delete_task_removes_task(client, create_task):
    """
    DELETE /tasks/{id} should remove the task.
    """

    # Arrange
    title = "Task to delete"

    created_task = create_task(title=title).json()
    task_id = created_task["id"]

    # Act
    delete_response = client.delete(f"/tasks/{task_id}")

    # Assert
    assert delete_response.status_code == 204
    assert delete_response.content == b""

    # confirm resource no longer exists
    get_response = client.get(f"/tasks/{task_id}")

    assert get_response.status_code == 404

def test_delete_task_returns_404_when_task_does_not_exist(client):
    """
    DELETE /tasks/{id} should return 404 if the task does not exist.
    """

    # Arrange
    non_existing_task_id = 999

    # Act
    response = client.delete(f"/tasks/{non_existing_task_id}")

    # Assert
    assert response.status_code == 404