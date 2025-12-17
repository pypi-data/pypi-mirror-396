"""API routes package."""

from fastapi import APIRouter

from gemini_agent.server.routes.health import router as health_router
from gemini_agent.server.routes.mcp import router as mcp_router
from gemini_agent.server.routes.sessions import router as sessions_router
from gemini_agent.server.routes.tasks import router as tasks_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(tasks_router)
api_router.include_router(mcp_router)
api_router.include_router(sessions_router)
