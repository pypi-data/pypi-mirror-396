"""MCP server management endpoints."""

import subprocess

from fastapi import APIRouter, HTTPException, status

from gemini_agent.server.models import (
    MCPServerListResponse,
    MCPServerRequest,
    MCPServerResponse,
)

router = APIRouter(prefix="/mcp/servers", tags=["MCP"])


@router.get("", response_model=MCPServerListResponse)
async def list_mcp_servers() -> MCPServerListResponse:
    """List all configured MCP servers."""
    try:
        result = subprocess.run(
            ["gemini", "mcp", "list"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        servers = []
        if result.returncode == 0 and result.stdout.strip():
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    servers.append({"name": line.strip(), "status": "configured"})

        return MCPServerListResponse(servers=servers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list MCP servers: {e}")


@router.post("", response_model=MCPServerResponse, status_code=status.HTTP_201_CREATED)
async def add_mcp_server(request: MCPServerRequest) -> MCPServerResponse:
    """Register an MCP server with Gemini CLI."""
    try:
        command = ["gemini", "mcp", "add", request.name, request.url]
        if request.args:
            command.extend(request.args)

        result = subprocess.run(command, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            return MCPServerResponse(
                name=request.name,
                status="added",
                message=f"MCP server '{request.name}' added successfully",
            )
        else:
            return MCPServerResponse(
                name=request.name,
                status="error",
                message=result.stderr or result.stdout or "Unknown error",
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add MCP server: {e}")


@router.delete("/{name}", response_model=MCPServerResponse)
async def remove_mcp_server(name: str) -> MCPServerResponse:
    """Remove an MCP server from Gemini CLI."""
    try:
        result = subprocess.run(
            ["gemini", "mcp", "remove", name],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            return MCPServerResponse(
                name=name,
                status="removed",
                message=f"MCP server '{name}' removed successfully",
            )
        else:
            return MCPServerResponse(
                name=name,
                status="error",
                message=result.stderr or result.stdout or "Server not found",
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove MCP server: {e}")
