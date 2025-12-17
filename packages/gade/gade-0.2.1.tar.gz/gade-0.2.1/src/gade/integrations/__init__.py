"""
GADE Integrations Package

Provides integrations with agentic AI frameworks:
- OpenAI function calling / tools
- LangChain tools
- MCP (Model Context Protocol)
"""

from .openai_tools import GADE_TOOLS, execute_tool

__all__ = ["GADE_TOOLS", "execute_tool"]
