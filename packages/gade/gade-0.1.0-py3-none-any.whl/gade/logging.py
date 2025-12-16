"""
GADE Structured Logging

Professional logging with structlog for observability.
"""

import logging
import sys
from typing import Any

try:
    import structlog
    HAS_STRUCTLOG = True
except ImportError:
    HAS_STRUCTLOG = False


def setup_logging(
    level: str = "INFO",
    json_output: bool = False,
    log_file: str | None = None
) -> Any:
    """
    Configure GADE logging.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        json_output: If True, output JSON logs (for production)
        log_file: Optional file to write logs to
    
    Returns:
        Configured logger
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    if HAS_STRUCTLOG:
        # Use structlog for structured logging
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.UnicodeDecoder(),
        ]
        
        if json_output:
            processors.append(structlog.processors.JSONRenderer())
        else:
            processors.append(structlog.dev.ConsoleRenderer(colors=True))
        
        structlog.configure(
            processors=processors,
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
        
        # Configure standard logging
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=log_level,
        )
        
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(log_level)
            logging.getLogger().addHandler(file_handler)
        
        return structlog.get_logger("gade")
    
    else:
        # Fallback to standard logging
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        handler.setLevel(log_level)
        
        logger = logging.getLogger("gade")
        logger.setLevel(log_level)
        logger.addHandler(handler)
        
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            file_handler.setLevel(log_level)
            logger.addHandler(file_handler)
        
        return logger


# Default logger instance
_logger = None


def get_logger(name: str = "gade") -> Any:
    """Get a logger instance."""
    global _logger
    if _logger is None:
        _logger = setup_logging()
    
    if HAS_STRUCTLOG:
        return structlog.get_logger(name)
    else:
        return logging.getLogger(name)


# Convenience functions
def log_analysis_start(repo_path: str, file_count: int) -> None:
    """Log analysis start."""
    get_logger().info(
        "analysis_started",
        repo=repo_path,
        files=file_count
    )


def log_analysis_complete(duration: float, nodes: int, avg_score: float) -> None:
    """Log analysis completion."""
    get_logger().info(
        "analysis_complete",
        duration_seconds=round(duration, 2),
        nodes=nodes,
        avg_difficulty=round(avg_score, 3)
    )


def log_llm_request(provider: str, model: str, tokens: int) -> None:
    """Log LLM API request."""
    get_logger().debug(
        "llm_request",
        provider=provider,
        model=model,
        tokens=tokens
    )


def log_llm_error(provider: str, model: str, error: str) -> None:
    """Log LLM API error."""
    get_logger().error(
        "llm_error",
        provider=provider,
        model=model,
        error=error
    )
