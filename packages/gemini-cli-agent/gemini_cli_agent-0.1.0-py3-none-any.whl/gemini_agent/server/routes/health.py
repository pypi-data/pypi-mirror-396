"""Health check endpoints."""

import subprocess

from fastapi import APIRouter

from gemini_agent.server.config import get_settings
from gemini_agent.server.models import HealthResponse

router = APIRouter(tags=["Health"])
settings = get_settings()


@router.get("/", response_model=HealthResponse)
@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check with Gemini CLI version and MCP servers."""
    gemini_version = None
    mcp_servers = []

    try:
        result = subprocess.run(["gemini", "--version"], capture_output=True, text=True, timeout=10)
        gemini_version = result.stdout.strip()
    except Exception:
        pass

    try:
        result = subprocess.run(
            ["gemini", "mcp", "list"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    mcp_servers.append(line.strip())
    except Exception:
        pass

    return HealthResponse(
        app_name=settings.app_name,
        app_version=settings.app_version,
        gemini_cli_version=gemini_version,
        mcp_servers=mcp_servers,
    )
