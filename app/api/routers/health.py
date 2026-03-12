# api/routers/health.py

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def root():
    return {
        "service": "task-api",
        "status": "running",
        "docs": "/docs"
    }


@router.get("/health")
def health_check():
    return {"status": "ok"}