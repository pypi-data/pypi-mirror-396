"""
Gradient Proxy signal - measures reasoning instability.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from gade.signals.base import SignalPlugin


class GradientProxySignal(SignalPlugin):
    """
    Measures reasoning instability (the "gradient" of difficulty).
    
    Metrics:
    - Rewrites required (from history)
    - Token-level variance across attempts
    - Retry count
    - Historical difficulty volatility
    """
    
    name = "gradient_proxy"
    description = "Reasoning instability and difficulty change rate"
    
    def compute(
        self,
        file_path: Path,
        ast_range: tuple[int, int],
        context: Optional[dict[str, Any]] = None,
    ) -> float:
        """
        Compute gradient proxy for a code region.
        
        Uses historical data if available, otherwise estimates from
        code structure indicating likely refactoring needs.
        """
        if context is None:
            context = {}
        
        # Check for historical gradient data
        history_data = context.get("gradient_history")
        if history_data:
            return self._compute_from_history(history_data)
        
        # Check for rewrite count from LLM interactions
        rewrite_count = context.get("rewrite_count", 0)
        retry_count = context.get("retry_count", 0)
        
        if rewrite_count > 0 or retry_count > 0:
            return self._compute_from_interactions(rewrite_count, retry_count)
        
        # Fall back to structural analysis
        if not file_path.exists():
            return 0.0
        
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return 0.0
        
        lines = content.splitlines()
        start_line, end_line = ast_range
        region_lines = lines[start_line - 1:end_line]
        region_content = "\n".join(region_lines)
        
        # Estimate gradient from structural indicators
        return self._estimate_from_structure(region_content, file_path, context)
    
    def _compute_from_history(self, history: list[float]) -> float:
        """Compute gradient from difficulty history."""
        if len(history) < 2:
            return 0.0
        
        # Compute variance of difficulty changes
        changes = [
            abs(history[i] - history[i-1])
            for i in range(1, len(history))
        ]
        
        if not changes:
            return 0.0
        
        avg_change = sum(changes) / len(changes)
        
        # High average change = high instability
        return self.sigmoid_normalize(avg_change, midpoint=0.1, steepness=10)
    
    def _compute_from_interactions(
        self,
        rewrite_count: int,
        retry_count: int,
    ) -> float:
        """Compute gradient from LLM interaction history."""
        # More rewrites/retries = higher gradient
        combined = rewrite_count * 0.7 + retry_count * 0.3
        return self.sigmoid_normalize(combined, midpoint=3, steepness=0.5)
    
    def _estimate_from_structure(
        self,
        code: str,
        file_path: Path,
        context: dict[str, Any],
    ) -> float:
        """
        Estimate gradient from code structure.
        
        Looks for patterns that typically require multiple refactoring attempts.
        """
        import re
        
        scores = []
        
        # 1. High coupling indicators
        import_count = len(re.findall(r"^(?:from|import)\s+", code, re.MULTILINE))
        coupling_score = self.sigmoid_normalize(import_count, midpoint=10, steepness=0.2)
        scores.append(coupling_score)
        
        # 2. Long functions (likely need splitting)
        line_count = len(code.splitlines())
        length_score = self.sigmoid_normalize(line_count, midpoint=50, steepness=0.05)
        scores.append(length_score)
        
        # 3. Deeply nested structures
        max_indent = 0
        for line in code.splitlines():
            if line.strip():
                indent = len(line) - len(line.lstrip())
                max_indent = max(max_indent, indent)
        nesting_score = self.normalize(max_indent // 4, 0, 6)
        scores.append(nesting_score)
        
        # 4. Multiple return statements (complex logic)
        return_count = len(re.findall(r"\breturn\b", code))
        return_score = self.sigmoid_normalize(return_count, midpoint=4, steepness=0.4)
        scores.append(return_score)
        
        # 5. Global/nonlocal usage (state management complexity)
        global_count = len(re.findall(r"\b(?:global|nonlocal)\b", code))
        global_score = self.sigmoid_normalize(global_count, midpoint=1, steepness=1.0)
        scores.append(global_score)
        
        # Load historical data if available
        gade_dir = context.get("gade_dir")
        if gade_dir:
            history_score = self._load_history_score(gade_dir, file_path)
            if history_score is not None:
                scores.append(history_score)
        
        if not scores:
            return 0.0
        
        return sum(scores) / len(scores)
    
    def _load_history_score(
        self,
        gade_dir: Path,
        file_path: Path,
    ) -> Optional[float]:
        """Load historical gradient data if available."""
        history_file = gade_dir / "history" / f"{file_path.stem}_gradient.json"
        
        if not history_file.exists():
            return None
        
        try:
            with open(history_file) as f:
                data = json.load(f)
            
            history = data.get("difficulty_history", [])
            return self._compute_from_history(history)
        except Exception:
            return None
    
    def save_gradient_data(
        self,
        gade_dir: Path,
        file_path: Path,
        difficulty_score: float,
    ) -> None:
        """Append difficulty score to history."""
        history_dir = gade_dir / "history"
        history_dir.mkdir(exist_ok=True)
        
        history_file = history_dir / f"{file_path.stem}_gradient.json"
        
        try:
            if history_file.exists():
                with open(history_file) as f:
                    data = json.load(f)
            else:
                data = {"difficulty_history": []}
            
            data["difficulty_history"].append(difficulty_score)
            
            # Keep bounded history
            if len(data["difficulty_history"]) > 100:
                data["difficulty_history"] = data["difficulty_history"][-100:]
            
            with open(history_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass
