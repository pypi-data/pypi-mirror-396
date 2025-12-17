"""
Error Density signal - measures error indicators in code.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Optional

from gade.signals.base import SignalPlugin


class ErrorDensitySignal(SignalPlugin):
    """
    Computes error density from code analysis.
    
    Metrics:
    - TODO/FIXME/HACK comment density
    - Exception handling patterns
    - Error-prone patterns (bare except, pass, etc.)
    """
    
    name = "error_density"
    description = "Error indicators and technical debt markers"
    
    # Patterns indicating potential issues
    ISSUE_PATTERNS = [
        (r"\bTODO\b", 0.3),
        (r"\bFIXME\b", 0.5),
        (r"\bHACK\b", 0.5),
        (r"\bXXX\b", 0.4),
        (r"\bBUG\b", 0.6),
        (r"\bWORKAROUND\b", 0.4),
        (r"\bTEMP\b", 0.3),
        (r"\bDEPRECATED\b", 0.3),
    ]
    
    # Error-prone code patterns
    CODE_SMELL_PATTERNS = [
        (r"except\s*:", 0.4),  # Bare except
        (r"except\s+Exception\s*:", 0.3),  # Catching all exceptions
        (r":\s*pass\s*$", 0.2),  # Empty blocks
        (r"#\s*type:\s*ignore", 0.2),  # Type ignore comments
        (r"#\s*noqa", 0.2),  # Linter ignores
        (r"#\s*pylint:\s*disable", 0.2),  # Pylint disables
        (r"raise\s+Exception\(", 0.3),  # Generic exception raising
        (r"assert\s+False", 0.4),  # Assertion failures
        (r"print\s*\(", 0.1),  # Debug prints (weak signal)
    ]
    
    def compute(
        self,
        file_path: Path,
        ast_range: tuple[int, int],
        context: Optional[dict[str, Any]] = None,
    ) -> float:
        """
        Compute error density for a code region.
        
        Returns higher values for code with many issue markers.
        """
        if not file_path.exists():
            return 0.0
        
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return 0.0
        
        # Extract region
        lines = content.splitlines()
        start_line, end_line = ast_range
        region_lines = lines[start_line - 1:end_line]
        region_content = "\n".join(region_lines)
        
        # Compute scores
        issue_score = self._compute_issue_score(region_content)
        smell_score = self._compute_smell_score(region_content)
        exception_score = self._compute_exception_score(region_content)
        
        # Normalize by region size
        line_count = max(1, len(region_lines))
        density_factor = min(1.0, 10 / line_count)  # Smaller regions get less weight
        
        # Combine scores
        raw_score = (
            0.4 * issue_score
            + 0.35 * smell_score
            + 0.25 * exception_score
        )
        
        return min(1.0, raw_score * (1.0 - 0.5 * density_factor + 0.5))
    
    def _compute_issue_score(self, code: str) -> float:
        """Score based on TODO/FIXME/HACK comments."""
        total_score = 0.0
        
        for pattern, weight in self.ISSUE_PATTERNS:
            matches = re.findall(pattern, code, re.IGNORECASE)
            total_score += len(matches) * weight
        
        return self.sigmoid_normalize(total_score, midpoint=2, steepness=0.8)
    
    def _compute_smell_score(self, code: str) -> float:
        """Score based on code smell patterns."""
        total_score = 0.0
        
        for pattern, weight in self.CODE_SMELL_PATTERNS:
            matches = re.findall(pattern, code, re.MULTILINE)
            total_score += len(matches) * weight
        
        return self.sigmoid_normalize(total_score, midpoint=3, steepness=0.5)
    
    def _compute_exception_score(self, code: str) -> float:
        """Score based on exception handling patterns."""
        # Count try/except blocks
        try_count = len(re.findall(r"\btry\s*:", code))
        except_count = len(re.findall(r"\bexcept\b", code))
        raise_count = len(re.findall(r"\braise\b", code))
        
        # Complex exception handling indicates difficult code
        complexity = try_count + except_count * 0.5 + raise_count * 0.3
        
        return self.sigmoid_normalize(complexity, midpoint=3, steepness=0.5)
