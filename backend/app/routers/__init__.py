"""API routers for AgentVine backend."""

from app.routers.about import router as about_router
from app.routers.chat import router as chat_router
from app.routers.health import router as health_router
from app.routers.tasks import router as tasks_router
from app.routers.workers import router as workers_router
from app.routers.sessions import router as sessions_router
from app.routers.queue import router as queue_router

__all__ = [
    "about_router",
    "chat_router",
    "health_router",
    "tasks_router",
    "workers_router",
    "sessions_router",
    "queue_router",
]
