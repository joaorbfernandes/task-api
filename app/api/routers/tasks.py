# /api/routers/task.py

from fastapi import APIRouter, HTTPException
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate, TaskPatch, TaskStatus
from datetime import datetime, UTC

# router
router = APIRouter()


# storage (estado em memória)
tasks: dict[int, dict] = {}
next_id: int = 1

# timestamp
current_time = datetime.now(UTC).replace(microsecond=0)

# -----------------------
# lógica interna
# -----------------------

def _create_task_logic(task: TaskCreate):
    global next_id
    new_task = {
        "id": next_id,
        "title": task.title,
        "status": TaskStatus.pending,
        "description": task.description,
        "due_date": task.due_date,
        "created_at": current_time,
        "updated_at": None
    }
    tasks[next_id] = new_task
    next_id += 1
    return new_task

def _get_task_logic(task_id: int):
    task = tasks.get(task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task

def _update_task_logic(task_id: int, task_update: TaskUpdate):
    task = tasks.get(task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    task["title"] = task_update.title
    task["description"] = task_update.description
    task["due_date"] = task_update.due_date
    task["status"] = task_update.status
    task["updated_at"] = current_time

    return task

def _patch_task_logic(task_id: int, task_patch: TaskPatch):

    task = tasks.get(task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    updates = task_patch.model_dump(exclude_unset=True)

    for field, value in updates.items():
        task[field] = value

    task["updated_at"] = current_time

    return task

def _delete_task_logic(task_id: int):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    del tasks[task_id]

# -----------------------
# endpoints
# -----------------------

@router.get("/tasks", response_model=list[TaskResponse], status_code=200)
def list_tasks():
    return list(tasks.values())

@router.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(task: TaskCreate):
    return _create_task_logic(task)

@router.get("/tasks/{task_id}", response_model=TaskResponse, status_code=200)
def get_task(task_id: int):
    return _get_task_logic(task_id)

@router.put("/tasks/{task_id}", response_model=TaskResponse, status_code=200)
def update_task(task_id: int, task_update: TaskUpdate):
    return _update_task_logic(task_id, task_update)

@router.patch("/tasks/{task_id}", response_model=TaskResponse)
def patch_task(task_id: int, task_patch: TaskPatch):
    return _patch_task_logic(task_id, task_patch)

@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    _delete_task_logic(task_id)