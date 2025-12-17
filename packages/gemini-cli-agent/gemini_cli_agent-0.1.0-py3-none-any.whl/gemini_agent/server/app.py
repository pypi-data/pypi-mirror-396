"""FastAPI application for Gemini Agent API."""

import subprocess
from contextlib import asynccontextmanager

from fastapi import FastAPI

from gemini_agent.server.config import get_settings
from gemini_agent.server.routes import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    settings = get_settings()
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    print(f"📡 Redis: {settings.redis_url}")

    try:
        result = subprocess.run(["gemini", "--version"], capture_output=True, text=True, timeout=10)
        print(f"🤖 Gemini CLI: {result.stdout.strip()}")
    except Exception as e:
        print(f"⚠️ Gemini CLI: {e}")

    yield
    print("👋 Shutting down...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="REST API for Gemini CLI agentic capabilities with MCP support",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.include_router(api_router)
    return app


# Default app instance
app = create_app()


def run():
    """CLI entrypoint for running the server."""
    import uvicorn

    uvicorn.run("gemini_agent.server.app:app", host="0.0.0.0", port=8000, reload=True)
