"""
Semantic Complexity signal - AST-based code complexity metrics.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from gade.signals.base import SignalPlugin


class SemanticComplexitySignal(SignalPlugin):
    """
    Computes semantic complexity from AST analysis.
    
    Metrics:
    - Maximum AST depth
    - Cyclomatic complexity
    - Nested control flow depth
    - Halstead complexity measures
    """
    
    name = "semantic_complexity"
    description = "AST-based code complexity metrics"
    
    def compute(
        self,
        file_path: Path,
        ast_range: tuple[int, int],
        context: Optional[dict[str, Any]] = None,
    ) -> float:
        """
        Compute semantic complexity for a code region.
        
        Returns higher values for deeply nested, complex code.
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
        
        # Compute metrics
        ast_depth = self._compute_ast_depth(region_content, file_path.suffix)
        cyclomatic = self._compute_cyclomatic_complexity(region_content)
        nesting = self._compute_nesting_depth(region_content)
        
        # Normalize and combine
        depth_score = self.normalize(ast_depth, 0, 15)
        cyclomatic_score = self.sigmoid_normalize(cyclomatic, midpoint=10, steepness=0.3)
        nesting_score = self.normalize(nesting, 0, 6)
        
        # Weighted combination
        return (
            0.3 * depth_score
            + 0.4 * cyclomatic_score
            + 0.3 * nesting_score
        )
    
    def _compute_ast_depth(self, code: str, suffix: str) -> int:
        """Compute maximum AST depth for the code."""
        # For Python, try using ast module
        if suffix in (".py",):
            try:
                import ast
                tree = ast.parse(code)
                return self._get_max_depth(tree)
            except SyntaxError:
                pass
        
        # Fallback: estimate from indentation
        max_depth = 0
        for line in code.splitlines():
            if line.strip():
                indent = len(line) - len(line.lstrip())
                # Assume 4 spaces per level
                depth = indent // 4
                max_depth = max(max_depth, depth)
        
        return max_depth
    
    def _get_max_depth(self, node: Any, current_depth: int = 0) -> int:
        """Recursively compute max AST depth."""
        import ast
        
        max_depth = current_depth
        for child in ast.iter_child_nodes(node):
            child_depth = self._get_max_depth(child, current_depth + 1)
            max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def _compute_cyclomatic_complexity(self, code: str) -> int:
        """
        Estimate cyclomatic complexity.
        
        Count decision points: if, for, while, and, or, except, etc.
        """
        decision_keywords = [
            "if ", "elif ", "for ", "while ", "except ",
            " and ", " or ", "case ", "?",  # ternary
        ]
        
        complexity = 1  # Base complexity
        code_lower = code.lower()
        
        for keyword in decision_keywords:
            complexity += code_lower.count(keyword)
        
        return complexity
    
    def _compute_nesting_depth(self, code: str) -> int:
        """Compute maximum nesting depth of control structures."""
        nesting_keywords = {"if", "for", "while", "with", "try", "def", "class"}
        
        max_nesting = 0
        current_nesting = 0
        current_indent = 0
        
        for line in code.splitlines():
            if not line.strip():
                continue
            
            indent = len(line) - len(line.lstrip())
            
            # Reset nesting when indent decreases
            if indent < current_indent:
                current_nesting = max(0, current_nesting - 1)
            
            current_indent = indent
            
            # Check for nesting keywords
            first_word = line.strip().split()[0] if line.strip().split() else ""
            first_word = first_word.rstrip(":")
            
            if first_word in nesting_keywords:
                current_nesting += 1
                max_nesting = max(max_nesting, current_nesting)
        
        return max_nesting
