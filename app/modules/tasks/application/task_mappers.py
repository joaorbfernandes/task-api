# app/application/mappers/task_mapper.py

from app.modules.tasks.application.task_dtos import CreateTaskInput, UpdateTaskInput, PatchTaskInput
from app.modules.tasks.api.task_schemas import TaskCreate, TaskPatch, TaskUpdate


def map_task_create_to_input(task_create: TaskCreate) -> CreateTaskInput:
    return CreateTaskInput(
        title=task_create.title,
        description=task_create.description,
        due_date=task_create.due_date,
        is_blocked=task_create.is_blocked
    )


def map_task_update_to_input(task_update: TaskUpdate) -> UpdateTaskInput:
    return UpdateTaskInput(
        title=task_update.title,
        description=task_update.description,
        status=task_update.status,
        due_date=task_update.due_date,
        is_blocked=task_update.is_blocked
    )


def map_task_patch_to_input(task_patch: TaskPatch) -> PatchTaskInput:
    return PatchTaskInput(
        title=task_patch.title,
        title_provided="title" in task_patch.model_fields_set,

        description=task_patch.description,
        description_provided="description" in task_patch.model_fields_set,

        status=task_patch.status,
        status_provided="status" in task_patch.model_fields_set,

        due_date=task_patch.due_date,
        due_date_provided="due_date" in task_patch.model_fields_set,

        is_blocked=task_patch.is_blocked,
        is_blocked_provided="is_blocked" in task_patch.model_fields_set
    )