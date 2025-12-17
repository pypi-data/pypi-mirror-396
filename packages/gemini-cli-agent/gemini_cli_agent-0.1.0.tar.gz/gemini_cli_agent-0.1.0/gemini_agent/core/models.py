"""Data models for the core agent."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


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


@dataclass
class AgentConfig:
    """Configuration for GeminiAgent."""

    api_key: str = ""
    model: str = ""
    timeout: int = 300
    approval_mode: ApprovalMode = ApprovalMode.YOLO
    sandbox: bool = False
    output_format: OutputFormat = OutputFormat.JSON


@dataclass
class AgentResult:
    """Result from a Gemini agent execution."""

    success: bool
    response: Optional[dict[str, Any]] = None
    modified_files: dict[str, str] = field(default_factory=dict)
    stdout: str = ""
    stderr: str = ""
    return_code: int = 0
    error: Optional[str] = None

    @classmethod
    def from_error(cls, error: str) -> "AgentResult":
        """Create a failed result from an error message."""
        return cls(success=False, error=error, return_code=-1)
