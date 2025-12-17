"""
Gemini Agent - Python wrapper for Google's Gemini CLI agentic capabilities.

This package provides three ways to use Gemini's agentic features:

1. Core (Direct CLI): Run Gemini CLI directly (requires Node.js + CLI installed)
   >>> from gemini_agent.core import GeminiAgent
   >>> agent = GeminiAgent()
   >>> result = agent.run("Create a hello world script")

2. Server: Deploy as a REST API service
   $ podman-compose up -d
   $ curl http://localhost:8000/tasks -d '{"prompt": "..."}'

3. Client: Python client for a deployed service
   >>> from gemini_agent.client import GeminiAgentClient
   >>> client = GeminiAgentClient("http://localhost:8000")
   >>> result = await client.run("Create a hello world script")
"""

from gemini_agent._version import __version__

__all__ = ["__version__"]
