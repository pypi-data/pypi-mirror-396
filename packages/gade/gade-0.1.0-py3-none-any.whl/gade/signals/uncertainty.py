"""
Uncertainty Proxy signal - LLM confidence estimation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from gade.signals.base import SignalPlugin


class UncertaintyProxySignal(SignalPlugin):
    """
    Estimates LLM uncertainty for code understanding.
    
    Metrics (when LLM is available):
    - Self-confidence score
    - Multiple solution disagreement
    - Temperature sensitivity
    
    Fallback metrics (static analysis):
    - Naming ambiguity
    - Magic numbers/strings
    - Uncommented complex sections
    """
    
    name = "uncertainty_proxy"
    description = "LLM confidence proxy and code clarity metrics"
    
    def compute(
        self,
        file_path: Path,
        ast_range: tuple[int, int],
        context: Optional[dict[str, Any]] = None,
    ) -> float:
        """
        Compute uncertainty proxy for a code region.
        
        If LLM context is available, uses model confidence.
        Otherwise, falls back to static clarity metrics.
        """
        if context is None:
            context = {}
        
        # Check for LLM confidence data
        llm_confidence = context.get("llm_confidence")
        if llm_confidence is not None:
            # LLM confidence is typically 0-1, where 1 = confident
            # We want uncertainty, so invert
            return 1.0 - llm_confidence
        
        # Fall back to static analysis
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
        
        # Static uncertainty indicators
        naming_score = self._compute_naming_ambiguity(region_content)
        magic_score = self._compute_magic_values(region_content)
        comment_score = self._compute_comment_ratio(region_lines)
        
        return (
            0.4 * naming_score
            + 0.35 * magic_score
            + 0.25 * (1.0 - comment_score)  # Low comments = high uncertainty
        )
    
    def _compute_naming_ambiguity(self, code: str) -> float:
        """Score based on unclear/short variable names."""
        import re
        
        # Find variable-like patterns
        identifiers = re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\b", code)
        
        if not identifiers:
            return 0.0
        
        # Count short/ambiguous names
        ambiguous_count = 0
        ambiguous_patterns = {"x", "y", "i", "j", "k", "n", "m", "tmp", "temp", "data", "val", "res"}
        
        for ident in identifiers:
            # Single-letter names (except common loop vars in context)
            if len(ident) <= 2 and ident.lower() not in {"id", "ok", "db", "io"}:
                ambiguous_count += 1
            # Known ambiguous names
            elif ident.lower() in ambiguous_patterns:
                ambiguous_count += 0.5
        
        ratio = ambiguous_count / len(identifiers)
        return self.normalize(ratio, 0, 0.3)
    
    def _compute_magic_values(self, code: str) -> float:
        """Score based on magic numbers and strings."""
        import re
        
        # Find numeric literals (excluding 0, 1, common values)
        numbers = re.findall(r"\b(\d+(?:\.\d+)?)\b", code)
        magic_numbers = [
            n for n in numbers
            if float(n) not in {0, 1, 2, 10, 100, 1000, -1}
        ]
        
        # Find string literals that might be magic
        strings = re.findall(r'["\']([^"\']{10,})["\']', code)
        long_strings = [s for s in strings if not s.startswith(("http", "/", "\\"))]
        
        magic_count = len(magic_numbers) + len(long_strings) * 2
        
        return self.sigmoid_normalize(magic_count, midpoint=5, steepness=0.4)
    
    def _compute_comment_ratio(self, lines: list[str]) -> float:
        """Compute ratio of commented lines."""
        if not lines:
            return 0.0
        
        comment_lines = 0
        code_lines = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            
            # Python comments
            if stripped.startswith("#"):
                comment_lines += 1
            # JS/TS comments
            elif stripped.startswith("//"):
                comment_lines += 1
            # Docstrings (rough detection)
            elif stripped.startswith('"""') or stripped.startswith("'''"):
                comment_lines += 1
            else:
                code_lines += 1
        
        total = comment_lines + code_lines
        if total == 0:
            return 0.5
        
        return comment_lines / total
