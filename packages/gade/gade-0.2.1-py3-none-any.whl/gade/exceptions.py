"""
GADE Custom Exceptions

Professional error handling with specific exception types.
"""


class GADEError(Exception):
    """Base exception for all GADE errors."""
    
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class AnalysisError(GADEError):
    """Failed to analyze repository or file."""
    pass


class ConfigurationError(GADEError):
    """Invalid or missing configuration."""
    pass


class LLMError(GADEError):
    """LLM API call failed."""
    
    def __init__(self, message: str, provider: str | None = None, model: str | None = None, **kwargs):
        super().__init__(message, kwargs)
        self.provider = provider
        self.model = model


class LLMRateLimitError(LLMError):
    """Rate limit exceeded."""
    
    def __init__(self, message: str, retry_after: float | None = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class LLMAuthenticationError(LLMError):
    """Invalid API key or authentication failed."""
    pass


class LLMConnectionError(LLMError):
    """Failed to connect to LLM provider."""
    pass


class SignalError(GADEError):
    """Error computing a difficulty signal."""
    
    def __init__(self, message: str, signal_name: str | None = None, **kwargs):
        super().__init__(message, kwargs)
        self.signal_name = signal_name


class CacheError(GADEError):
    """Cache operation failed."""
    pass


class MCPError(GADEError):
    """MCP server/tool error."""
    pass
