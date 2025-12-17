"""
Server module - REST API service for Gemini Agent.

This module provides a FastAPI-based REST API with Celery for async task processing.

To run the server:
    $ uvicorn gemini_agent.server.app:app --host 0.0.0.0 --port 8000

Or use the provided Docker/Podman compose file:
    $ podman-compose up -d
"""

from gemini_agent.server.app import app, create_app
from gemini_agent.server.config import Settings, get_settings

__all__ = ["app", "create_app", "Settings", "get_settings"]
