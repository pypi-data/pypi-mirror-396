"""
Celery worker for async Gemini CLI task execution.

This module provides the Celery app and task for processing
Gemini prompts asynchronously.
"""

from typing import Any, Dict, Optional

from celery import Celery

from gemini_agent.core import GeminiAgent
from gemini_agent.core.models import ApprovalMode, OutputFormat
from gemini_agent.server.config import get_settings

settings = get_settings()

celery_app = Celery(
    "gemini_agent",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_soft_time_limit=settings.task_soft_time_limit,
    task_time_limit=settings.task_time_limit,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    worker_concurrency=4,
    result_expires=3600,
)


@celery_app.task(bind=True, name="run_gemini_task", max_retries=2, default_retry_delay=30)
def run_gemini_task(
    self,
    prompt: str,
    files: Optional[Dict[str, str]] = None,
    model: Optional[str] = None,
    approval_mode: str = "yolo",
    sandbox: bool = False,
    mcp_servers: Optional[list[str]] = None,
    allowed_tools: Optional[list[str]] = None,
    extensions: Optional[list[str]] = None,
    include_directories: Optional[list[str]] = None,
    output_format: str = "json",
    resume_session: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Execute a Gemini CLI task asynchronously.

    This task wraps the GeminiAgent.run() method for Celery execution.
    """
    import logging

    logger = logging.getLogger(__name__)
    task_id = self.request.id

    logger.info(f"[{task_id}] Starting Gemini task")
    logger.info(f"[{task_id}] Prompt (first 100 chars): {prompt[:100]}...")

    try:
        agent = GeminiAgent(
            api_key=settings.gemini_api_key,
            model=model or settings.gemini_model,
            timeout=settings.gemini_timeout,
            approval_mode=ApprovalMode(approval_mode),
            sandbox=sandbox,
            output_format=OutputFormat(output_format),
        )

        result = agent.run(
            prompt=prompt,
            files=files,
            mcp_servers=mcp_servers,
            allowed_tools=allowed_tools,
            extensions=extensions,
            include_directories=include_directories,
            resume_session=resume_session,
        )

        logger.info(f"[{task_id}] Task completed: success={result.success}")

        return {
            "success": result.success,
            "response": result.response,
            "modified_files": result.modified_files,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.return_code,
            "error": result.error,
            "options_used": {
                "model": model or settings.gemini_model,
                "approval_mode": approval_mode,
                "sandbox": sandbox,
                "mcp_servers": mcp_servers,
                "output_format": output_format,
            },
        }

    except Exception as e:
        logger.exception(f"[{task_id}] Error executing task: {e}")
        try:
            raise self.retry(exc=e)
        except self.MaxRetriesExceededError:
            return {
                "success": False,
                "error": str(e),
                "response": None,
                "modified_files": {},
                "stdout": "",
                "stderr": "",
                "return_code": -1,
            }
