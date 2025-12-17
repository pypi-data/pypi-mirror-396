"""Task execution endpoints."""

import json

from celery.result import AsyncResult
from fastapi import APIRouter, status

from gemini_agent.server.config import get_settings
from gemini_agent.server.models import (
    TaskCreateResponse,
    TaskRequest,
    TaskResultResponse,
    TaskStatus,
)
from gemini_agent.server.worker import celery_app, run_gemini_task

router = APIRouter(prefix="/tasks", tags=["Tasks"])
settings = get_settings()


@router.post("", response_model=TaskCreateResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_task(request: TaskRequest) -> TaskCreateResponse:
    """Submit a new task to Gemini CLI."""
    full_prompt = request.prompt
    if request.context:
        context_str = json.dumps(request.context, indent=2)
        full_prompt = f"{request.prompt}\n\n---\n\nContext:\n{context_str}"

    task = run_gemini_task.delay(
        prompt=full_prompt,
        files=request.files,
        model=request.model or settings.gemini_model,
        approval_mode=request.approval_mode.value,
        sandbox=request.sandbox,
        mcp_servers=request.mcp_servers,
        allowed_tools=request.allowed_tools,
        extensions=request.extensions,
        include_directories=request.include_directories,
        output_format=request.output_format.value,
    )
    return TaskCreateResponse(task_id=task.id, status=TaskStatus.PENDING)


@router.get("/{task_id}", response_model=TaskResultResponse)
async def get_task(task_id: str) -> TaskResultResponse:
    """Get task status and result."""
    async_result = AsyncResult(task_id, app=celery_app)

    status_map = {
        "PENDING": TaskStatus.PENDING,
        "STARTED": TaskStatus.STARTED,
        "SUCCESS": TaskStatus.SUCCESS,
        "FAILURE": TaskStatus.FAILURE,
        "RETRY": TaskStatus.RETRY,
        "REVOKED": TaskStatus.REVOKED,
    }

    current_status = status_map.get(async_result.status, TaskStatus.PENDING)
    response = TaskResultResponse(task_id=task_id, status=current_status)

    if current_status == TaskStatus.SUCCESS:
        response.result = async_result.result
    elif current_status == TaskStatus.FAILURE:
        try:
            response.error = str(async_result.result) if async_result.result else "Unknown error"
        except Exception:
            response.error = "Unable to retrieve error details"

    return response


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_task(task_id: str) -> None:
    """Cancel a pending or running task."""
    async_result = AsyncResult(task_id, app=celery_app)
    async_result.revoke(terminate=True)
