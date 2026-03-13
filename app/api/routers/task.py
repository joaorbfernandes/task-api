# app/api/routers/task.py

from fastapi import APIRouter, Depends, HTTPException

from app.schemas.task import TaskCreate, TaskPatch, TaskResponse, TaskUpdate
from app.services.task_service import TaskNotFoundError, TaskService, get_task_service

router = APIRouter()


@router.get("/tasks", response_model=list[TaskResponse], status_code=200)
def list_tasks(task_service: TaskService = Depends(get_task_service)):
    """Return all tasks."""
    return task_service.list_tasks()


@router.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(task: TaskCreate, task_service: TaskService = Depends(get_task_service)):
    """Create a new task."""
    return task_service.create_task(task)


@router.get("/tasks/{task_id}", response_model=TaskResponse, status_code=200)
def get_task(task_id: int, task_service: TaskService = Depends(get_task_service)):
    """Return a task by id."""
    try:
        return task_service.get_task(task_id)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/tasks/{task_id}", response_model=TaskResponse, status_code=200)
def update_task(task_id: int, task_update: TaskUpdate, task_service: TaskService = Depends(get_task_service)):
    """Fully replace task data."""
    try:
        return task_service.update_task(task_id, task_update)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.patch("/tasks/{task_id}", response_model=TaskResponse, status_code=200)
def patch_task(task_id: int, task_patch: TaskPatch, task_service: TaskService = Depends(get_task_service)):
    """Partially update task fields."""
    try:
        return task_service.patch_task(task_id, task_patch)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, task_service: TaskService = Depends(get_task_service)):
    """Delete a task by id."""
    try:
        task_service.delete_task(task_id)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc