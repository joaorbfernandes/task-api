from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.modules.tasks.domain.task_errors import TaskDomainError
from app.modules.tasks.application.task_service import TaskNotFoundError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(TaskDomainError)
    async def handle_task_domain_error(
        request: Request,
        exc: TaskDomainError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"detail": str(exc)},
        )

    @app.exception_handler(TaskNotFoundError)
    async def handle_task_not_found(
        request: Request,
        exc: TaskNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)},
        )