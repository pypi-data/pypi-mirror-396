"""
GeminiAgentClient - HTTP client for the Gemini Agent API service.

This client connects to a deployed Gemini Agent API and provides
a simple interface to submit tasks and retrieve results.
"""

import asyncio
import time
from dataclasses import dataclass
from typing import Any, Optional

import httpx


@dataclass
class TaskResult:
    """Result from a Gemini Agent task."""

    task_id: str
    status: str
    success: bool
    response: Optional[dict[str, Any]] = None
    modified_files: Optional[dict[str, str]] = None
    error: Optional[str] = None


class GeminiAgentClient:
    """
    Async HTTP client for the Gemini Agent API.

    Example:
        >>> async with GeminiAgentClient("http://localhost:8000") as client:
        ...     result = await client.run("Create a hello world script")
        ...     print(result.response)

    Or with polling:
        >>> client = GeminiAgentClient("http://localhost:8000")
        >>> task_id = await client.submit("Create a hello world script")
        >>> result = await client.wait_for_result(task_id)
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: float = 300.0,
        poll_interval: float = 1.0,
    ):
        """
        Initialize the client.

        Args:
            base_url: Base URL of the Gemini Agent API service.
            timeout: Request timeout in seconds.
            poll_interval: Interval between status polls in seconds.
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.poll_interval = poll_interval
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "GeminiAgentClient":
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
        )
        return self

    async def __aexit__(self, *args) -> None:
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
            self._client = None

    def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
            )
        return self._client

    async def health(self) -> dict[str, Any]:
        """Check service health."""
        client = self._get_client()
        response = await client.get("/health")
        response.raise_for_status()
        return response.json()

    async def submit(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        approval_mode: str = "yolo",
        sandbox: bool = False,
        mcp_servers: Optional[list[str]] = None,
        allowed_tools: Optional[list[str]] = None,
        extensions: Optional[list[str]] = None,
        files: Optional[dict[str, str]] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> str:
        """
        Submit a task and return the task ID.

        Args:
            prompt: The prompt to send to Gemini.
            model: Model to use (optional).
            approval_mode: Tool approval mode (default, auto_edit, yolo).
            sandbox: Run in sandbox mode.
            mcp_servers: List of MCP servers to enable.
            allowed_tools: Tools allowed without confirmation.
            extensions: Extensions to use.
            files: Files to provide as context.
            context: Additional context data.

        Returns:
            Task ID for tracking the request.
        """
        client = self._get_client()

        payload = {
            "prompt": prompt,
            "approval_mode": approval_mode,
            "sandbox": sandbox,
        }

        if model:
            payload["model"] = model
        if mcp_servers:
            payload["mcp_servers"] = mcp_servers
        if allowed_tools:
            payload["allowed_tools"] = allowed_tools
        if extensions:
            payload["extensions"] = extensions
        if files:
            payload["files"] = files
        if context:
            payload["context"] = context

        response = await client.post("/tasks", json=payload)
        response.raise_for_status()
        return response.json()["task_id"]

    async def get_status(self, task_id: str) -> dict[str, Any]:
        """Get the status of a task."""
        client = self._get_client()
        response = await client.get(f"/tasks/{task_id}")
        response.raise_for_status()
        return response.json()

    async def wait_for_result(
        self,
        task_id: str,
        timeout: Optional[float] = None,
    ) -> TaskResult:
        """
        Wait for a task to complete and return the result.

        Args:
            task_id: The task ID to wait for.
            timeout: Maximum time to wait (uses client timeout if not specified).

        Returns:
            TaskResult with the final status and response.

        Raises:
            TimeoutError: If the task doesn't complete within the timeout.
        """
        timeout = timeout or self.timeout
        start_time = time.time()

        while True:
            status = await self.get_status(task_id)

            if status["status"] in ("SUCCESS", "FAILURE", "REVOKED"):
                result = status.get("result", {})
                return TaskResult(
                    task_id=task_id,
                    status=status["status"],
                    success=status["status"] == "SUCCESS" and result.get("success", False),
                    response=result.get("response"),
                    modified_files=result.get("modified_files"),
                    error=status.get("error") or result.get("error"),
                )

            if time.time() - start_time > timeout:
                raise TimeoutError(f"Task {task_id} did not complete within {timeout}s")

            await asyncio.sleep(self.poll_interval)

    async def cancel(self, task_id: str) -> None:
        """Cancel a pending or running task."""
        client = self._get_client()
        response = await client.delete(f"/tasks/{task_id}")
        response.raise_for_status()

    async def run(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        approval_mode: str = "yolo",
        sandbox: bool = False,
        mcp_servers: Optional[list[str]] = None,
        allowed_tools: Optional[list[str]] = None,
        extensions: Optional[list[str]] = None,
        files: Optional[dict[str, str]] = None,
        context: Optional[dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> TaskResult:
        """
        Submit a task and wait for the result.

        This is a convenience method that combines submit() and wait_for_result().

        Args:
            prompt: The prompt to send to Gemini.
            model: Model to use (optional).
            approval_mode: Tool approval mode (default, auto_edit, yolo).
            sandbox: Run in sandbox mode.
            mcp_servers: List of MCP servers to enable.
            allowed_tools: Tools allowed without confirmation.
            extensions: Extensions to use.
            files: Files to provide as context.
            context: Additional context data.
            timeout: Maximum time to wait for result.

        Returns:
            TaskResult with the response and any modified files.
        """
        task_id = await self.submit(
            prompt=prompt,
            model=model,
            approval_mode=approval_mode,
            sandbox=sandbox,
            mcp_servers=mcp_servers,
            allowed_tools=allowed_tools,
            extensions=extensions,
            files=files,
            context=context,
        )
        return await self.wait_for_result(task_id, timeout=timeout)

    async def list_mcp_servers(self) -> list[dict[str, str]]:
        """List configured MCP servers."""
        client = self._get_client()
        response = await client.get("/mcp/servers")
        response.raise_for_status()
        return response.json()["servers"]

    async def add_mcp_server(
        self,
        name: str,
        url: str,
        args: Optional[list[str]] = None,
    ) -> dict[str, str]:
        """Add an MCP server."""
        client = self._get_client()
        payload = {"name": name, "url": url}
        if args:
            payload["args"] = args
        response = await client.post("/mcp/servers", json=payload)
        response.raise_for_status()
        return response.json()

    async def remove_mcp_server(self, name: str) -> dict[str, str]:
        """Remove an MCP server."""
        client = self._get_client()
        response = await client.delete(f"/mcp/servers/{name}")
        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
