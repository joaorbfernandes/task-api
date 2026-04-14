from app.modules.tasks.application.task_dtos import PatchTaskInput, TaskInput as TaskInputDTO
from app.modules.tasks.api.task_schemas import TaskPatch, TaskInput as TaskInputSchema


def map_task_input(task_input: TaskInputSchema) -> TaskInputDTO:
    return TaskInputDTO(
        title=task_input.title,
        description=task_input.description,
        status=task_input.status,
        due_date=task_input.due_date,
        is_blocked=task_input.is_blocked
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