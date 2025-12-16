"""
Base interface for difficulty signal plugins.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional


class SignalPlugin(ABC):
    """
    Abstract base class for difficulty signal computation.
    
    All signals must return values normalized to [0, 1] range.
    """
    
    name: str = "base"
    description: str = "Base signal plugin"
    
    @abstractmethod
    def compute(
        self,
        file_path: Path,
        ast_range: tuple[int, int],
        context: Optional[dict[str, Any]] = None,
    ) -> float:
        """
        Compute normalized signal for a code region.
        
        Args:
            file_path: Absolute path to the source file
            ast_range: Line range (start, end), 1-indexed inclusive
            context: Optional context (repo path, git info, etc.)
            
        Returns:
            Normalized signal value in [0, 1]
        """
        pass
    
    @staticmethod
    def normalize(value: float, min_val: float, max_val: float) -> float:
        """
        Normalize a value to [0, 1] range.
        
        Uses min-max normalization with clamping.
        """
        if max_val <= min_val:
            return 0.0
        normalized = (value - min_val) / (max_val - min_val)
        return max(0.0, min(1.0, normalized))
    
    @staticmethod
    def sigmoid_normalize(value: float, midpoint: float = 5.0, steepness: float = 1.0) -> float:
        """
        Normalize using sigmoid function for unbounded values.
        
        Useful for metrics that can grow without bound (like churn count).
        """
        import math
        return 1.0 / (1.0 + math.exp(-steepness * (value - midpoint)))
