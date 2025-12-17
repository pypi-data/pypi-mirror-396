"""
GADE Enhanced LLM Client

Production-grade LLM client supporting multiple providers:
- OpenAI (GPT-4, GPT-4o, o1)
- Anthropic (Claude 3.5, Claude 3)
- Google (Gemini Pro)
- Local (Ollama, llama.cpp)
- Azure OpenAI
- AWS Bedrock
- Together AI
- Groq
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Iterator, Literal

from ..exceptions import (
    LLMError,
    LLMRateLimitError,
    LLMAuthenticationError,
    LLMConnectionError,
)
from ..logging import get_logger, log_llm_request, log_llm_error

# Provider type
Provider = Literal[
    "openai", "anthropic", "google", "ollama", 
    "azure", "bedrock", "together", "groq", "local"
]


@dataclass
class LLMConfig:
    """LLM configuration."""
    provider: Provider = "openai"
    model: str = "gpt-4o-mini"
    api_key: str | None = None
    base_url: str | None = None
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: float = 60.0
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Provider-specific
    azure_endpoint: str | None = None
    azure_deployment: str | None = None
    aws_region: str | None = None
    
    def __post_init__(self):
        # Auto-detect API key from environment
        if self.api_key is None:
            env_keys = {
                "openai": "OPENAI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY",
                "google": "GOOGLE_API_KEY",
                "together": "TOGETHER_API_KEY",
                "groq": "GROQ_API_KEY",
            }
            if self.provider in env_keys:
                self.api_key = os.getenv(env_keys[self.provider])


@dataclass
class LLMResponse:
    """Standardized LLM response."""
    content: str
    model: str
    provider: str
    tokens_used: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    finish_reason: str = "stop"
    confidence: float = 1.0
    latency_ms: float = 0.0
    raw_response: dict = field(default_factory=dict)


class LLMClient:
    """
    Production-grade LLM client with multi-provider support.
    
    Usage:
        client = LLMClient(provider="openai", model="gpt-4o")
        response = client.complete("Explain this code...")
        
        # Streaming
        for chunk in client.stream("Explain this code..."):
            print(chunk, end="")
    """
    
    SUPPORTED_PROVIDERS = [
        "openai", "anthropic", "google", "ollama",
        "azure", "bedrock", "together", "groq", "local"
    ]
    
    # Default models per provider
    DEFAULT_MODELS = {
        "openai": "gpt-4o-mini",
        "anthropic": "claude-3-5-sonnet-20241022",
        "google": "gemini-1.5-flash",
        "ollama": "llama3.2",
        "azure": "gpt-4o",
        "together": "meta-llama/Llama-3.2-3B-Instruct-Turbo",
        "groq": "llama-3.1-8b-instant",
    }
    
    def __init__(self, config: LLMConfig | None = None, **kwargs):
        """
        Initialize LLM client.
        
        Args:
            config: LLMConfig instance
            **kwargs: Override config values
        """
        if config is None:
            config = LLMConfig(**kwargs)
        else:
            # Allow kwargs to override config
            for k, v in kwargs.items():
                if hasattr(config, k):
                    setattr(config, k, v)
        
        self.config = config
        self.logger = get_logger("gade.llm")
        self._client = None
        self._init_client()
    
    def _init_client(self) -> None:
        """Initialize the underlying LLM client."""
        try:
            import litellm
            litellm.set_verbose = False
            self._litellm = litellm
        except ImportError:
            raise ImportError(
                "litellm is required for LLM support. "
                "Install with: pip install gade[llm]"
            )
    
    def _get_model_string(self) -> str:
        """Get the model string for litellm."""
        provider = self.config.provider
        model = self.config.model
        
        # LiteLLM uses prefixes for some providers
        prefixes = {
            "anthropic": "anthropic/",
            "google": "gemini/",
            "ollama": "ollama/",
            "azure": "azure/",
            "bedrock": "bedrock/",
            "together": "together_ai/",
            "groq": "groq/",
        }
        
        prefix = prefixes.get(provider, "")
        return f"{prefix}{model}"
    
    def _build_messages(self, prompt: str, system: str | None = None) -> list[dict]:
        """Build messages array for chat completion."""
        messages = []
        
        if system:
            messages.append({"role": "system", "content": system})
        
        messages.append({"role": "user", "content": prompt})
        
        return messages
    
    def complete(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        **kwargs
    ) -> LLMResponse:
        """
        Send a completion request.
        
        Args:
            prompt: User prompt
            system: Optional system prompt
            temperature: Override default temperature
            max_tokens: Override default max tokens
            **kwargs: Additional provider-specific parameters
        
        Returns:
            LLMResponse with completion
        """
        messages = self._build_messages(prompt, system)
        model = self._get_model_string()
        
        log_llm_request(
            self.config.provider,
            self.config.model,
            len(prompt)
        )
        
        start_time = time.perf_counter()
        
        for attempt in range(self.config.max_retries):
            try:
                response = self._litellm.completion(
                    model=model,
                    messages=messages,
                    temperature=temperature or self.config.temperature,
                    max_tokens=max_tokens or self.config.max_tokens,
                    api_key=self.config.api_key,
                    base_url=self.config.base_url,
                    timeout=self.config.timeout,
                    **kwargs
                )
                
                latency = (time.perf_counter() - start_time) * 1000
                
                return LLMResponse(
                    content=response.choices[0].message.content or "",
                    model=self.config.model,
                    provider=self.config.provider,
                    tokens_used=response.usage.total_tokens if response.usage else 0,
                    prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
                    completion_tokens=response.usage.completion_tokens if response.usage else 0,
                    finish_reason=response.choices[0].finish_reason or "stop",
                    latency_ms=latency,
                    raw_response=response.model_dump() if hasattr(response, 'model_dump') else {},
                )
                
            except Exception as e:
                error_str = str(e).lower()
                
                # Handle specific errors
                if "rate" in error_str or "429" in error_str:
                    if attempt < self.config.max_retries - 1:
                        delay = self.config.retry_delay * (2 ** attempt)
                        self.logger.warning(f"Rate limited, retrying in {delay}s...")
                        time.sleep(delay)
                        continue
                    raise LLMRateLimitError(
                        str(e),
                        provider=self.config.provider,
                        model=self.config.model
                    )
                
                elif "auth" in error_str or "401" in error_str or "api key" in error_str:
                    raise LLMAuthenticationError(
                        str(e),
                        provider=self.config.provider,
                        model=self.config.model
                    )
                
                elif "connect" in error_str or "timeout" in error_str:
                    if attempt < self.config.max_retries - 1:
                        delay = self.config.retry_delay * (2 ** attempt)
                        self.logger.warning(f"Connection error, retrying in {delay}s...")
                        time.sleep(delay)
                        continue
                    raise LLMConnectionError(
                        str(e),
                        provider=self.config.provider,
                        model=self.config.model
                    )
                
                else:
                    log_llm_error(self.config.provider, self.config.model, str(e))
                    raise LLMError(
                        str(e),
                        provider=self.config.provider,
                        model=self.config.model
                    )
        
        raise LLMError("Max retries exceeded", provider=self.config.provider, model=self.config.model)
    
    def stream(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        **kwargs
    ) -> Iterator[str]:
        """
        Stream a completion response.
        
        Args:
            prompt: User prompt
            system: Optional system prompt
            temperature: Override default temperature
            max_tokens: Override default max tokens
        
        Yields:
            Content chunks as they arrive
        """
        messages = self._build_messages(prompt, system)
        model = self._get_model_string()
        
        try:
            response = self._litellm.completion(
                model=model,
                messages=messages,
                temperature=temperature or self.config.temperature,
                max_tokens=max_tokens or self.config.max_tokens,
                api_key=self.config.api_key,
                base_url=self.config.base_url,
                timeout=self.config.timeout,
                stream=True,
                **kwargs
            )
            
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            log_llm_error(self.config.provider, self.config.model, str(e))
            raise LLMError(str(e), provider=self.config.provider, model=self.config.model)
    
    async def acomplete(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        **kwargs
    ) -> LLMResponse:
        """Async completion request."""
        messages = self._build_messages(prompt, system)
        model = self._get_model_string()
        
        start_time = time.perf_counter()
        
        try:
            response = await self._litellm.acompletion(
                model=model,
                messages=messages,
                temperature=temperature or self.config.temperature,
                max_tokens=max_tokens or self.config.max_tokens,
                api_key=self.config.api_key,
                base_url=self.config.base_url,
                timeout=self.config.timeout,
                **kwargs
            )
            
            latency = (time.perf_counter() - start_time) * 1000
            
            return LLMResponse(
                content=response.choices[0].message.content or "",
                model=self.config.model,
                provider=self.config.provider,
                tokens_used=response.usage.total_tokens if response.usage else 0,
                latency_ms=latency,
            )
            
        except Exception as e:
            log_llm_error(self.config.provider, self.config.model, str(e))
            raise LLMError(str(e), provider=self.config.provider, model=self.config.model)
    
    async def astream(
        self,
        prompt: str,
        system: str | None = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Async streaming completion."""
        messages = self._build_messages(prompt, system)
        model = self._get_model_string()
        
        try:
            response = await self._litellm.acompletion(
                model=model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                api_key=self.config.api_key,
                stream=True,
                **kwargs
            )
            
            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            log_llm_error(self.config.provider, self.config.model, str(e))
            raise LLMError(str(e), provider=self.config.provider, model=self.config.model)
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        try:
            return self._litellm.token_counter(model=self.config.model, text=text)
        except Exception:
            # Fallback estimate
            return len(text) // 4
    
    @classmethod
    def from_env(cls, provider: Provider = "openai") -> "LLMClient":
        """Create client from environment variables."""
        return cls(config=LLMConfig(provider=provider))
