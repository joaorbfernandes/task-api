# app/main.py

from fastapi import FastAPI

from app.api.routers.tasks import router as tasks_router
from app.api.routers.health import router as health_router

app = FastAPI()

app.include_router(tasks_router)
app.include_router(health_router)