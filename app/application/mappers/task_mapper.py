# app/application/mappers/task_mapper.py

from app.application.dtos.task_dto import CreateTaskInput, UpdateTaskInput
from app.domain.entities.task import Task
from app.api.schemas.task import TaskCreate, TaskPatch, TaskUpdate


def map_task_create_to_input(task_create: TaskCreate) -> CreateTaskInput:
    return CreateTaskInput(
        title=task_create.title,
        description=task_create.description,
        due_date=task_create.due_date,
        is_blocked=task_create.is_blocked,
    )


def map_task_update_to_input(task_update: TaskUpdate) -> UpdateTaskInput:
    return UpdateTaskInput(
        title=task_update.title,
        description=task_update.description,
        status=task_update.status,
        due_date=task_update.due_date,
        is_blocked=task_update.is_blocked,
    )


def merge_task_patch_into_update_input(task: Task, task_patch: TaskPatch) -> UpdateTaskInput:
    return UpdateTaskInput(
        title=task_patch.title if "title" in task_patch.model_fields_set else task.title,
        description=task_patch.description if "description" in task_patch.model_fields_set else task.description,
        status=task_patch.status if "status" in task_patch.model_fields_set else task.status,
        due_date=task_patch.due_date if "due_date" in task_patch.model_fields_set else task.due_date,
        is_blocked=task_patch.is_blocked if "is_blocked" in task_patch.model_fields_set else task.is_blocked,
    )