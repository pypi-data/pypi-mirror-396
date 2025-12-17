"""
Core data structures for GADE.

Defines DifficultyNode, SignalVector, and ComputeBudget models.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, computed_field


class SignalVector(BaseModel):
    """
    Normalized difficulty signals, all in range [0, 1].
    
    Each signal represents a different dimension of code difficulty:
    - edit_churn: How frequently the code changes (git history)
    - error_density: Test failures, exceptions, TODO/FIXME density
    - semantic_complexity: AST depth, cyclomatic complexity, nesting
    - uncertainty_proxy: LLM self-confidence, solution disagreement
    - gradient_proxy: Reasoning instability (rewrites, variance, retries)
    """
    
    edit_churn: float = Field(default=0.0, ge=0.0, le=1.0)
    error_density: float = Field(default=0.0, ge=0.0, le=1.0)
    semantic_complexity: float = Field(default=0.0, ge=0.0, le=1.0)
    uncertainty_proxy: float = Field(default=0.0, ge=0.0, le=1.0)
    gradient_proxy: float = Field(default=0.0, ge=0.0, le=1.0)
    
    def weighted_sum(self, weights: Optional[dict[str, float]] = None) -> float:
        """
        Compute weighted sum of all signals.
        
        Dynamically redistributes weights when signals are zero (missing).
        Emphasizes semantic complexity and gradient proxy.
        """
        if weights is None:
            weights = {
                "edit_churn": 0.15,
                "error_density": 0.20,
                "semantic_complexity": 0.30,  # Boosted
                "uncertainty_proxy": 0.15,
                "gradient_proxy": 0.20,
            }
        
        # Get signal values
        signals = [
            ("edit_churn", self.edit_churn, weights.get("edit_churn", 0.15)),
            ("error_density", self.error_density, weights.get("error_density", 0.20)),
            ("semantic_complexity", self.semantic_complexity, weights.get("semantic_complexity", 0.30)),
            ("uncertainty_proxy", self.uncertainty_proxy, weights.get("uncertainty_proxy", 0.15)),
            ("gradient_proxy", self.gradient_proxy, weights.get("gradient_proxy", 0.20)),
        ]
        
        # Calculate total weight of non-zero signals for redistribution
        active_weight = sum(w for _, v, w in signals if v > 0.01)
        total_weight = sum(w for _, _, w in signals)
        
        if active_weight == 0:
            return 0.0
        
        # Redistribute weight from zero signals to non-zero signals
        # This prevents edit_churn=0 from dragging down scores
        multiplier = total_weight / active_weight if active_weight > 0 else 1.0
        
        total = 0.0
        for name, value, weight in signals:
            if value > 0.01:
                # Scale up weight to compensate for missing signals
                adjusted_weight = weight * multiplier
                total += value * adjusted_weight
        
        return min(1.0, max(0.0, total))
    
    def to_dict(self) -> dict[str, float]:
        """Return signals as dictionary."""
        return {
            "edit_churn": self.edit_churn,
            "error_density": self.error_density,
            "semantic_complexity": self.semantic_complexity,
            "uncertainty_proxy": self.uncertainty_proxy,
            "gradient_proxy": self.gradient_proxy,
        }


class DifficultyNode(BaseModel):
    """
    Represents a code region with its difficulty metrics.
    
    A node can represent a file, function, class, or arbitrary code range.
    """
    
    id: str = Field(description="Unique identifier for this node")
    file_path: Path = Field(description="Absolute path to the source file")
    ast_range: tuple[int, int] = Field(
        description="Line range (start, end), 1-indexed inclusive"
    )
    node_type: str = Field(
        default="unknown",
        description="Type of code element: file, function, class, method"
    )
    node_name: str = Field(
        default="",
        description="Name of the function/class if applicable"
    )
    difficulty_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="EMA-smoothed difficulty score"
    )
    signals: SignalVector = Field(
        default_factory=SignalVector,
        description="Current signal values"
    )
    history: list[float] = Field(
        default_factory=list,
        description="Historical difficulty scores for EMA"
    )
    
    @computed_field
    @property
    def difficulty_tier(self) -> str:
        """
        Return the AI strategy tier based on difficulty score.
        
        - D < 0.2: shallow (summarize)
        - 0.2 <= D < 0.5: medium (single-pass)
        - 0.5 <= D < 0.8: deep (multi-step + tools)
        - D >= 0.8: critical (multi-pass synthesis)
        """
        if self.difficulty_score < 0.2:
            return "shallow"
        elif self.difficulty_score < 0.5:
            return "medium"
        elif self.difficulty_score < 0.8:
            return "deep"
        else:
            return "critical"
            
    def get_compute_budget(self) -> int:
        """Return token budget based on tier."""
        tier = self.difficulty_tier
        if tier == "shallow":
            return 500
        elif tier == "medium":
            return 2000
        elif tier == "deep":
            return 6000
        else:  # critical
            return 12000
    
    @classmethod
    def generate_id(cls, file_path: Path, ast_range: tuple[int, int]) -> str:
        """Generate deterministic ID from file path and range."""
        key = f"{file_path.as_posix()}:{ast_range[0]}-{ast_range[1]}"
        return hashlib.sha256(key.encode()).hexdigest()[:16]
    
    def update_difficulty(self, alpha: float = 0.2) -> float:
        """
        Update difficulty score using EMA formula.
        
        D_t = α * S_t + (1 - α) * D_{t-1}
        
        Args:
            alpha: Smoothing factor in range [0.1, 0.3]
            
        Returns:
            Updated difficulty score
        """
        current_signal = self.signals.weighted_sum()
        
        if not self.history:
            self.difficulty_score = current_signal
        else:
            self.difficulty_score = (
                alpha * current_signal + (1 - alpha) * self.history[-1]
            )
        
        self.history.append(self.difficulty_score)
        
        # Keep history bounded
        if len(self.history) > 100:
            self.history = self.history[-100:]
        
        return self.difficulty_score


class ComputeBudget(BaseModel):
    """
    Tracks token allocation across code regions.
    
    Ensures 80% of compute goes to top 20% difficulty regions.
    """
    
    total_tokens: int = Field(
        default=50000,
        description="Total token budget for the operation"
    )
    spent_tokens: int = Field(
        default=0,
        description="Tokens consumed so far"
    )
    allocation_map: dict[str, int] = Field(
        default_factory=dict,
        description="Mapping of region_id -> allocated tokens"
    )
    
    @computed_field
    @property
    def remaining_tokens(self) -> int:
        """Tokens still available."""
        return max(0, self.total_tokens - self.spent_tokens)
    
    @computed_field
    @property
    def utilization(self) -> float:
        """Fraction of budget consumed."""
        if self.total_tokens == 0:
            return 0.0
        return self.spent_tokens / self.total_tokens
    
    def allocate(self, region_id: str, tokens: int) -> bool:
        """
        Allocate tokens to a region.
        
        Returns False if insufficient budget.
        """
        if tokens > self.remaining_tokens:
            return False
        
        self.allocation_map[region_id] = (
            self.allocation_map.get(region_id, 0) + tokens
        )
        self.spent_tokens += tokens
        return True
    
    def get_allocation(self, region_id: str) -> int:
        """Get tokens allocated to a specific region."""
        return self.allocation_map.get(region_id, 0)
    
    @classmethod
    def from_difficulty_ranking(
        cls,
        nodes: list[DifficultyNode],
        total_tokens: int,
    ) -> "ComputeBudget":
        """
        Create budget with 80/20 allocation based on difficulty.
        
        Top 20% difficulty regions get 80% of tokens.
        """
        budget = cls(total_tokens=total_tokens)
        
        if not nodes:
            return budget
        
        # Sort by difficulty descending
        sorted_nodes = sorted(
            nodes, key=lambda n: n.difficulty_score, reverse=True
        )
        
        # Top 20% get 80% of tokens
        top_count = max(1, len(sorted_nodes) // 5)
        top_nodes = sorted_nodes[:top_count]
        bottom_nodes = sorted_nodes[top_count:]
        
        top_budget = int(total_tokens * 0.8)
        bottom_budget = total_tokens - top_budget
        
        # Distribute within tiers proportionally to difficulty
        if top_nodes:
            top_total_diff = sum(n.difficulty_score for n in top_nodes)
            for node in top_nodes:
                if top_total_diff > 0:
                    share = node.difficulty_score / top_total_diff
                else:
                    share = 1.0 / len(top_nodes)
                budget.allocation_map[node.id] = int(top_budget * share)
        
        if bottom_nodes:
            bottom_total_diff = sum(n.difficulty_score for n in bottom_nodes)
            for node in bottom_nodes:
                if bottom_total_diff > 0:
                    share = node.difficulty_score / bottom_total_diff
                else:
                    share = 1.0 / len(bottom_nodes)
                budget.allocation_map[node.id] = int(bottom_budget * share)
        
        return budget


class AnalysisResult(BaseModel):
    """
    Complete analysis result for a repository.
    """
    
    repo_path: Path
    nodes: list[DifficultyNode] = Field(default_factory=list)
    total_files: int = 0
    total_functions: int = 0
    analysis_timestamp: str = ""
    
    @computed_field
    @property
    def average_difficulty(self) -> float:
        """Average difficulty across all nodes."""
        if not self.nodes:
            return 0.0
        return sum(n.difficulty_score for n in self.nodes) / len(self.nodes)
    
    def get_top_k(self, k: int = 10) -> list[DifficultyNode]:
        """Get top K most difficult regions."""
        return sorted(
            self.nodes,
            key=lambda n: n.difficulty_score,
            reverse=True
        )[:k]
    
    def get_by_tier(self, tier: str) -> list[DifficultyNode]:
        """Get all nodes in a specific difficulty tier."""
        return [n for n in self.nodes if n.difficulty_tier == tier]
