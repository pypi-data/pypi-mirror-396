"""
GADE - Gradient-Aware Development Environment

Allocate AI attention and compute dynamically based on code difficulty.

Usage:
    # CLI
    gade analyze ./repo --top 20
    gade heatmap ./repo
    gade serve --port 8000
    
    # Programmatic
    from gade import analyze, get_difficulty
    result = analyze("./my-repo")
    score = get_difficulty("./file.py")
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

__version__ = "1.0.0"
__author__ = "GADE Team"

# Lazy imports for performance
if TYPE_CHECKING:
    from .models import DifficultyNode, SignalVector, AnalysisResult
    from .config import GADEConfig


def analyze(
    repo_path: str | Path,
    top_k: int = 20,
    include_patterns: list[str] | None = None,
) -> "AnalysisResult":
    """
    Analyze code difficulty across a repository.
    
    Args:
        repo_path: Path to repository
        top_k: Number of top regions to include in quick access
        include_patterns: File patterns to include (default: ["*.py", "*.js", "*.ts"])
    
    Returns:
        AnalysisResult with all difficulty nodes
    
    Example:
        result = analyze("./my-project")
        for node in result.get_top_k(10):
            print(f"{node.name}: {node.difficulty_score:.2f}")
    """
    from .config import GADEConfig
    from .analyzer import analyze_repository
    
    config = GADEConfig()
    if include_patterns:
        config.include_patterns = include_patterns
    
    return analyze_repository(Path(repo_path), config)


def get_difficulty(file_path: str | Path) -> float:
    """
    Get difficulty score for a file.
    
    Args:
        file_path: Path to file
    
    Returns:
        Difficulty score (0.0 - 1.0)
    """
    from .config import GADEConfig
    from .analyzer import analyze_repository
    
    path = Path(file_path)
    config = GADEConfig()
    result = analyze_repository(path.parent, config)
    
    for node in result.nodes:
        if node.file_path == path and node.node_type == "file":
            return node.difficulty_score
    
    return 0.0


def heatmap(repo_path: str | Path) -> None:
    """
    Display difficulty heatmap in terminal.
    
    Args:
        repo_path: Path to repository
    """
    from .config import GADEConfig
    from .analyzer import analyze_repository
    from .output import render_heatmap
    
    config = GADEConfig()
    result = analyze_repository(Path(repo_path), config)
    render_heatmap(result.nodes, Path(repo_path))


# Public API
__all__ = [
    # Version
    "__version__",
    "__author__",
    # Core functions
    "analyze",
    "get_difficulty",
    "heatmap",
]
