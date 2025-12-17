"""
Client module - Python client for a deployed Gemini Agent API service.

Usage:
    >>> from gemini_agent.client import GeminiAgentClient
    >>> client = GeminiAgentClient("http://localhost:8000")
    >>> result = await client.run("Create a hello world script")
    >>> print(result)
"""

from gemini_agent.client.client import GeminiAgentClient

__all__ = ["GeminiAgentClient"]
