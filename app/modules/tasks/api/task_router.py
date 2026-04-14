from fastapi import APIRouter, Depends

from app.modules.tasks.api.task_schemas import TaskInput, TaskPatch, TaskResponse
from app.modules.tasks.application.task_service import TaskService
from app.modules.tasks.application.task_mappers import map_task_input, map_task_patch_to_input
from app.modules.tasks.api.dependencies import get_task_service

router = APIRouter()


@router.get("/tasks", response_model=list[TaskResponse], status_code=200)
def list_tasks(task_service: TaskService = Depends(get_task_service)):
    """Return all tasks."""
    return task_service.list_tasks()


@router.get("/tasks/{task_id}", response_model=TaskResponse, status_code=200)
def get_task(task_id: int, task_service: TaskService = Depends(get_task_service)):
    """Return a task by id."""
    return task_service.get_task(task_id=task_id)


@router.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(payload: TaskInput, task_service: TaskService = Depends(get_task_service)):
    """Create a new task."""
    task_input = map_task_input(payload)
    return task_service.create_task(task=task_input)


@router.put("/tasks/{task_id}", response_model=TaskResponse, status_code=200)
def update_task(task_id: int, payload: TaskInput, task_service: TaskService = Depends(get_task_service)):
    """Fully replace task data."""
    task_input = map_task_input(payload)
    return task_service.update_task(task_id=task_id, task_input=task_input)


@router.patch("/tasks/{task_id}", response_model=TaskResponse, status_code=200)
def patch_task(task_id: int, payload: TaskPatch, task_service: TaskService = Depends(get_task_service)):
    """Partially update task fields."""
    task_input = map_task_patch_to_input(payload)
    return task_service.patch_task(task_id=task_id, task_input=task_input)


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, task_service: TaskService = Depends(get_task_service)):
    """Delete a task by id."""
    task_service.delete_task(task_id=task_id)