# app/main.py

from fastapi import FastAPI

from app.modules.tasks.api.task_router import router as tasks_router
from app.api.health_router import router as health_router

app = FastAPI()

app.include_router(tasks_router)
app.include_router(health_router)