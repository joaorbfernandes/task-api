from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.tasks.application.task_repository import TaskRepository
from app.modules.tasks.domain.task import Task
from app.modules.tasks.domain.task_status import TaskStatus
from app.modules.tasks.infrastructure.task_model import TaskModel


class SqlAlchemyTaskRepository(TaskRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_tasks(self) -> list[Task]:
        stmt = select(TaskModel).order_by(TaskModel.id)
        models = self._session.scalars(stmt).all()
        return [self._to_domain(model) for model in models]

    def get_task(self, task_id: int) -> Task | None:
        model = self._session.get(TaskModel, task_id)

        if model is None:
            return None

        return self._to_domain(model)

    def create_task(self, task: Task) -> Task:
        model = self._to_model(task)

        self._session.add(model)
        self._session.flush()

        return self._to_domain(model)

    def save_task(self, task: Task) -> Task:
        if task.id is None:
            raise ValueError("Cannot save a task without an id")

        model = self._session.get(TaskModel, task.id)
        if model is None:
            raise ValueError(f"Task with id {task.id} was not found")

        self._apply_domain_to_model(task, model)
        self._session.flush()
        
        return self._to_domain(model)

    def delete_task(self, task_id: int) -> None:
        model = self._session.get(TaskModel, task_id)

        if model is not None:
            self._session.delete(model)

    def _to_domain(self, model: TaskModel) -> Task:
        return Task(
            id=model.id,
            title=model.title,
            description=model.description,
            status=TaskStatus(model.status),
            due_date=model.due_date,
            created_at=model.created_at,
            updated_at=model.updated_at,
            is_blocked=model.is_blocked,
        )

    def _to_model(self, task: Task) -> TaskModel:
        return TaskModel(
            title=task.title,
            description=task.description,
            status=task.status.value,
            due_date=task.due_date,
            created_at=task.created_at,
            updated_at=task.updated_at,
            is_blocked=task.is_blocked,
        )

    def _apply_domain_to_model(self, task: Task, model: TaskModel) -> None:
        model.title = task.title
        model.description = task.description
        model.status = task.status.value
        model.due_date = task.due_date
        model.updated_at = task.updated_at
        model.is_blocked = task.is_blocked