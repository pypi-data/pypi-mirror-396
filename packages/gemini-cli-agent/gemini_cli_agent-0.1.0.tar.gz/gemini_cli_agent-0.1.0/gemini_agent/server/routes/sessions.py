"""Sessions and extensions endpoints."""

import subprocess

from fastapi import APIRouter, HTTPException, status

from gemini_agent.server.models import ExtensionListResponse, SessionListResponse

router = APIRouter(tags=["Sessions"])


@router.get("/extensions", response_model=ExtensionListResponse, tags=["Extensions"])
async def list_extensions() -> ExtensionListResponse:
    """List all available Gemini CLI extensions."""
    try:
        result = subprocess.run(
            ["gemini", "--list-extensions"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        extensions = []
        if result.returncode == 0 and result.stdout.strip():
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    extensions.append({"name": line.strip()})

        return ExtensionListResponse(extensions=extensions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list extensions: {e}")


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions() -> SessionListResponse:
    """List available sessions."""
    try:
        result = subprocess.run(
            ["gemini", "--list-sessions"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        sessions = []
        if result.returncode == 0 and result.stdout.strip():
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    sessions.append({"session": line.strip()})

        return SessionListResponse(sessions=sessions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {e}")


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: str) -> None:
    """Delete a session by index number."""
    try:
        result = subprocess.run(
            ["gemini", "--delete-session", session_id],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            raise HTTPException(
                status_code=404,
                detail=result.stderr or f"Session {session_id} not found",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {e}")
