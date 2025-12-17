"""
GeminiAgent - Direct wrapper for Gemini CLI.

This class provides a Pythonic interface to the Gemini CLI's agentic capabilities.
Requires Node.js and @google/gemini-cli to be installed.
"""

import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from gemini_agent.core.models import AgentConfig, AgentResult, ApprovalMode, OutputFormat

logger = logging.getLogger(__name__)


class GeminiAgent:
    """
    Python wrapper for Gemini CLI agentic capabilities.

    Example:
        >>> agent = GeminiAgent(api_key="your-key")
        >>> result = agent.run("Create a hello world Python script")
        >>> print(result.response)

    Requires:
        - Node.js installed
        - @google/gemini-cli installed globally (npm install -g @google/gemini-cli)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "",
        timeout: int = 300,
        approval_mode: ApprovalMode = ApprovalMode.YOLO,
        sandbox: bool = False,
        output_format: OutputFormat = OutputFormat.JSON,
    ):
        """
        Initialize the Gemini Agent.

        Args:
            api_key: Gemini API key. If not provided, reads from GEMINI_API_KEY env var.
            model: Model to use (e.g., "gemini-2.5-flash"). Empty = let CLI choose.
            timeout: Command timeout in seconds.
            approval_mode: Tool approval mode (default, auto_edit, yolo).
            sandbox: Run in sandbox mode for isolation.
            output_format: Output format (text, json, stream-json).
        """
        self.config = AgentConfig(
            api_key=api_key or os.environ.get("GEMINI_API_KEY", ""),
            model=model,
            timeout=timeout,
            approval_mode=approval_mode,
            sandbox=sandbox,
            output_format=output_format,
        )
        self._verify_cli_installed()

    def _verify_cli_installed(self) -> None:
        """Verify that Gemini CLI is installed and accessible."""
        try:
            result = subprocess.run(
                ["gemini", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                logger.debug(f"Gemini CLI version: {result.stdout.strip()}")
            else:
                logger.warning("Gemini CLI found but returned non-zero exit code")
        except FileNotFoundError:
            raise RuntimeError(
                "Gemini CLI not found. Please install it with: " "npm install -g @google/gemini-cli"
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("Gemini CLI version check timed out")

    def run(
        self,
        prompt: str,
        *,
        files: Optional[dict[str, str]] = None,
        mcp_servers: Optional[list[str]] = None,
        allowed_tools: Optional[list[str]] = None,
        extensions: Optional[list[str]] = None,
        include_directories: Optional[list[str]] = None,
        working_directory: Optional[str] = None,
        resume_session: Optional[str] = None,
    ) -> AgentResult:
        """
        Execute a prompt with Gemini CLI.

        Args:
            prompt: The prompt to send to Gemini.
            files: Dict of filename -> content to provide as context.
            mcp_servers: List of MCP server names to enable.
            allowed_tools: Tools allowed to run without confirmation.
            extensions: Extensions to use.
            include_directories: Additional directories to include.
            working_directory: Directory to run in (creates temp dir if not specified).
            resume_session: Session ID to resume ("latest" for most recent).

        Returns:
            AgentResult with success status, response, and any modified files.
        """
        files = files or {}
        use_temp_dir = working_directory is None

        if use_temp_dir:
            temp_dir = tempfile.mkdtemp(prefix="gemini_agent_")
            work_path = Path(temp_dir)
        else:
            work_path = Path(working_directory)
            work_path.mkdir(parents=True, exist_ok=True)

        try:
            return self._execute(
                prompt=prompt,
                work_path=work_path,
                files=files,
                mcp_servers=mcp_servers,
                allowed_tools=allowed_tools,
                extensions=extensions,
                include_directories=include_directories,
                resume_session=resume_session,
            )
        finally:
            if use_temp_dir:
                import shutil

                shutil.rmtree(temp_dir, ignore_errors=True)

    def _execute(
        self,
        prompt: str,
        work_path: Path,
        files: dict[str, str],
        mcp_servers: Optional[list[str]],
        allowed_tools: Optional[list[str]],
        extensions: Optional[list[str]],
        include_directories: Optional[list[str]],
        resume_session: Optional[str],
    ) -> AgentResult:
        """Execute the CLI command."""
        initial_files: dict[str, str] = {}

        for filename, content in files.items():
            file_path = (work_path / filename).resolve()
            # Security: ensure path is within working directory
            if not str(file_path).startswith(str(work_path.resolve())):
                logger.warning(f"Blocked path traversal attempt: {filename}")
                continue
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
            initial_files[filename] = content

        command = ["gemini", "--output-format", self.config.output_format.value]

        if self.config.model:
            command.extend(["--model", self.config.model])

        if self.config.approval_mode == ApprovalMode.YOLO:
            command.append("-y")
        elif self.config.approval_mode in (ApprovalMode.DEFAULT, ApprovalMode.AUTO_EDIT):
            command.extend(["--approval-mode", self.config.approval_mode.value])

        if self.config.sandbox:
            command.append("--sandbox")

        if mcp_servers:
            command.append("--allowed-mcp-server-names")
            command.extend(mcp_servers)

        if allowed_tools:
            command.append("--allowed-tools")
            command.extend(allowed_tools)

        if extensions:
            command.append("--extensions")
            command.extend(extensions)

        if include_directories:
            for directory in include_directories:
                command.extend(["--include-directories", directory])

        if resume_session:
            command.extend(["--resume", resume_session])

        command.append(prompt)

        env = os.environ.copy()
        if self.config.api_key:
            env["GEMINI_API_KEY"] = self.config.api_key

        logger.debug(f"Executing: {' '.join(command[:-1])} '<prompt>'")

        try:
            result = subprocess.run(
                command,
                cwd=work_path,
                env=env,
                capture_output=True,
                text=True,
                timeout=self.config.timeout,
            )
        except subprocess.TimeoutExpired:
            return AgentResult.from_error(f"Command timed out after {self.config.timeout} seconds")
        except Exception as e:
            return AgentResult.from_error(str(e))

        response = None
        if result.stdout:
            if self.config.output_format == OutputFormat.JSON:
                try:
                    response = json.loads(result.stdout)
                except json.JSONDecodeError:
                    response = {"raw_output": result.stdout}
            else:
                response = {"raw_output": result.stdout}

        modified_files: dict[str, str] = {}
        for file_path in work_path.rglob("*"):
            if file_path.is_file():
                relative_path = str(file_path.relative_to(work_path))
                if relative_path.startswith("."):
                    continue
                try:
                    content = file_path.read_text(encoding="utf-8")
                    if relative_path not in initial_files:
                        modified_files[relative_path] = content
                    elif initial_files[relative_path] != content:
                        modified_files[relative_path] = content
                except (UnicodeDecodeError, Exception):
                    pass

        return AgentResult(
            success=result.returncode == 0,
            response=response,
            modified_files=modified_files,
            stdout=result.stdout,
            stderr=result.stderr,
            return_code=result.returncode,
        )
