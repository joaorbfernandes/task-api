from fastapi import Depends
from sqlalchemy.orm import Session

from app.infrastructure.db.session_factory import get_db_session
from app.modules.tasks.application.task_repository import TaskRepository
from app.modules.tasks.application.task_service import TaskService
from app.application.unit_of_work import UnitOfWork
from app.modules.tasks.infrastructure.sqlalchemy_task_repository import SqlAlchemyTaskRepository
from app.infrastructure.db.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork


def get_task_repository(session: Session = Depends(get_db_session)) -> TaskRepository:
    return SqlAlchemyTaskRepository(session=session)


def get_unit_of_work(session: Session = Depends(get_db_session)) -> UnitOfWork:
    return SqlAlchemyUnitOfWork(session=session)


def get_task_service(
    repository: TaskRepository = Depends(get_task_repository),
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> TaskService:
    return TaskService(repository=repository, uow=uow)