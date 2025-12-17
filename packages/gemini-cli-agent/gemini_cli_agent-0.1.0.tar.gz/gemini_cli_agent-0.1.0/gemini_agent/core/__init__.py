"""
Core module - Direct Gemini CLI wrapper.

Requires Node.js and @google/gemini-cli to be installed on the system.

Usage:
    >>> from gemini_agent.core import GeminiAgent
    >>> agent = GeminiAgent(api_key="your-key")
    >>> result = agent.run("Create a Python script that prints hello world")
    >>> print(result.response)
"""

from gemini_agent.core.agent import GeminiAgent
from gemini_agent.core.models import AgentResult, AgentConfig

__all__ = ["GeminiAgent", "AgentResult", "AgentConfig"]
