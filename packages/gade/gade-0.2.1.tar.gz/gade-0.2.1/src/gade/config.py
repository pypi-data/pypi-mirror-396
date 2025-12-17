"""
Configuration management for GADE.

Handles signal weights, EMA alpha, LLM settings, and token budgets.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field


class SignalWeights(BaseModel):
    """Weights for difficulty signal aggregation."""
    
    edit_churn: float = Field(default=0.15, ge=0.0, le=1.0)
    error_density: float = Field(default=0.20, ge=0.0, le=1.0)
    semantic_complexity: float = Field(default=0.25, ge=0.0, le=1.0)
    uncertainty_proxy: float = Field(default=0.15, ge=0.0, le=1.0)
    gradient_proxy: float = Field(default=0.25, ge=0.0, le=1.0)
    
    def normalize(self) -> "SignalWeights":
        """Normalize weights to sum to 1.0."""
        total = (
            self.edit_churn
            + self.error_density
            + self.semantic_complexity
            + self.uncertainty_proxy
            + self.gradient_proxy
        )
        if total == 0:
            return SignalWeights()
        return SignalWeights(
            edit_churn=self.edit_churn / total,
            error_density=self.error_density / total,
            semantic_complexity=self.semantic_complexity / total,
            uncertainty_proxy=self.uncertainty_proxy / total,
            gradient_proxy=self.gradient_proxy / total,
        )


class LLMConfig(BaseModel):
    """LLM provider configuration."""
    
    provider: str = Field(
        default="openai",
        description="LLM provider: openai, anthropic, ollama, etc."
    )
    model: str = Field(
        default="gpt-4o-mini",
        description="Model identifier"
    )
    api_key_env: str = Field(
        default="OPENAI_API_KEY",
        description="Environment variable for API key"
    )
    base_url: Optional[str] = Field(
        default=None,
        description="Custom API base URL for local models"
    )
    temperature: float = Field(
        default=0.1,
        ge=0.0,
        le=2.0,
        description="Sampling temperature"
    )
    max_tokens: int = Field(
        default=4096,
        description="Maximum response tokens"
    )


class AllocationConfig(BaseModel):
    """Token allocation strategy configuration."""
    
    # Tier thresholds
    # Tier thresholds
    shallow_threshold: float = Field(default=0.2)
    medium_threshold: float = Field(default=0.5)
    deep_threshold: float = Field(default=0.8)
    
    # Token percentages per tier
    shallow_tokens_pct: float = Field(default=0.05)
    medium_tokens_pct: float = Field(default=0.15)
    deep_tokens_pct: float = Field(default=0.30)
    critical_tokens_pct: float = Field(default=0.50)


class GADEConfig(BaseModel):
    """Main GADE configuration."""
    
    # EMA smoothing
    alpha: float = Field(
        default=0.2,
        ge=0.1,
        le=0.3,
        description="EMA smoothing factor"
    )
    
    # Signal weights
    signal_weights: SignalWeights = Field(default_factory=SignalWeights)
    
    # LLM settings
    llm: LLMConfig = Field(default_factory=LLMConfig)
    
    # Allocation settings
    allocation: AllocationConfig = Field(default_factory=AllocationConfig)
    
    # Analysis settings
    default_budget: int = Field(
        default=50000,
        description="Default token budget for refactor operations"
    )
    top_k: int = Field(
        default=20,
        description="Default number of top regions to analyze"
    )
    
    # File patterns
    include_patterns: list[str] = Field(
        default_factory=lambda: ["*.py", "*.js", "*.ts", "*.go", "*.rs"]
    )
    exclude_patterns: list[str] = Field(
        default_factory=lambda: [
            "**/node_modules/**",
            "**/__pycache__/**",
            "**/venv/**",
            "**/.git/**",
            "**/dist/**",
            "**/build/**",
        ]
    )
    
    # Determinism
    random_seed: int = Field(
        default=42,
        description="Seed for deterministic runs"
    )
    
    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "GADEConfig":
        """
        Load configuration from file.
        
        Searches in order:
        1. Provided path
        2. .gade/config.yaml in current directory
        3. ~/.gade/config.yaml
        4. Default values
        """
        search_paths = []
        
        if config_path:
            search_paths.append(config_path)
        
        search_paths.extend([
            Path.cwd() / ".gade" / "config.yaml",
            Path.home() / ".gade" / "config.yaml",
        ])
        
        for path in search_paths:
            if path.exists():
                with open(path) as f:
                    data = yaml.safe_load(f) or {}
                return cls.model_validate(data)
        
        return cls()
    
    def save(self, config_path: Path) -> None:
        """Save configuration to file."""
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False)


def get_default_config() -> GADEConfig:
    """Get default configuration."""
    return GADEConfig()


def init_gade_directory(repo_path: Path) -> Path:
    """
    Initialize .gade directory in repository.
    
    Creates:
    - .gade/config.yaml
    - .gade/history/ (for difficulty history)
    - .gade/cache/ (for analysis cache)
    
    Returns path to .gade directory.
    """
    gade_dir = repo_path / ".gade"
    gade_dir.mkdir(exist_ok=True)
    
    (gade_dir / "history").mkdir(exist_ok=True)
    (gade_dir / "cache").mkdir(exist_ok=True)
    
    config_path = gade_dir / "config.yaml"
    if not config_path.exists():
        config = GADEConfig()
        config.save(config_path)
    
    # Add to .gitignore if it exists
    gitignore = repo_path / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text()
        if ".gade/" not in content:
            with open(gitignore, "a") as f:
                f.write("\n# GADE analysis data\n.gade/\n")
    
    return gade_dir
