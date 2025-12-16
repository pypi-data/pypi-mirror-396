"""GADE API Package."""

try:
    from .server import app, run_server
    __all__ = ["app", "run_server"]
except ImportError:
    pass
