"""GADE MCP Package."""

try:
    from .server import app, run_server, main
    __all__ = ["app", "run_server", "main"]
except ImportError:
    # MCP not installed
    pass
