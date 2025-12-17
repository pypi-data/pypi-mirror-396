"""Pydantic models for Gemini Agent API."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Task execution status."""

    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RETRY = "RETRY"
    REVOKED = "REVOKED"


class ApprovalMode(str, Enum):
    """Tool execution approval mode."""

    DEFAULT = "default"
    AUTO_EDIT = "auto_edit"
    YOLO = "yolo"


class OutputFormat(str, Enum):
    """Output format for Gemini CLI."""

    TEXT = "text"
    JSON = "json"
    STREAM_JSON = "stream-json"


class TaskRequest(BaseModel):
    """Request model for submitting a task to Gemini CLI."""

    prompt: str = Field(
        ..., min_length=1, max_length=100000, description="The prompt to send to Gemini"
    )
    model: Optional[str] = Field(None, description="Gemini model to use (e.g., gemini-2.5-flash)")
    approval_mode: ApprovalMode = Field(
        ApprovalMode.YOLO, description="Approval mode for tool execution"
    )
    sandbox: bool = Field(False, description="Run in sandbox mode for isolation")
    mcp_servers: Optional[list[str]] = Field(None, description="List of MCP server names to enable")
    allowed_tools: Optional[list[str]] = Field(
        None, description="Tools allowed to run without confirmation"
    )
    extensions: Optional[list[str]] = Field(None, description="Extensions to use")
    include_directories: Optional[list[str]] = Field(
        None, description="Additional directories to include"
    )
    output_format: OutputFormat = Field(OutputFormat.JSON, description="Output format")
    files: Optional[dict[str, str]] = Field(
        None, description="Files to provide as context (filename -> content)"
    )
    context: Optional[dict[str, Any]] = Field(
        None, description="Additional context data to include in prompt"
    )


class TaskCreateResponse(BaseModel):
    """Response when a task is created."""

    task_id: str
    status: TaskStatus = TaskStatus.PENDING
    message: str = "Task submitted successfully"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TaskResultResponse(BaseModel):
    """Response with task status and result."""

    task_id: str
    status: TaskStatus
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
    app_name: str
    app_version: str
    gemini_cli_version: Optional[str] = None
    mcp_servers: list[str] = []
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MCPServerRequest(BaseModel):
    """Request model for adding an MCP server."""

    name: str = Field(..., description="Name for the MCP server")
    url: str = Field(..., description="URL or command for the MCP server")
    args: Optional[list[str]] = Field(None, description="Additional arguments for the MCP server")


class MCPServerResponse(BaseModel):
    """Response for MCP server operations."""

    name: str
    status: str
    message: str


class MCPServerListResponse(BaseModel):
    """Response listing MCP servers."""

    servers: list[dict[str, str]]


class ExtensionListResponse(BaseModel):
    """Response listing extensions."""

    extensions: list[dict[str, Any]]


class SessionListResponse(BaseModel):
    """Response listing sessions."""

    sessions: list[dict[str, Any]]
