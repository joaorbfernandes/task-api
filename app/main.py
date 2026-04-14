# app/main.py

from fastapi import FastAPI

from app.modules.tasks.api.task_router import router as tasks_router
from app.api.health_router import router as health_router
from app.modules.tasks.api.exception_handlers import register_exception_handlers

app = FastAPI()

register_exception_handlers(app)

app.include_router(tasks_router)
app.include_router(health_router)