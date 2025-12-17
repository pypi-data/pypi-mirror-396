"""
Repository analyzer - core analysis engine for GADE.

Scans repositories, extracts code regions, and computes difficulty scores.
"""

from __future__ import annotations

import fnmatch
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from rich.progress import Progress

from gade.config import GADEConfig
from gade.models import AnalysisResult, DifficultyNode, SignalVector
from gade.signals import get_all_signals


def analyze_repository(
    repo_path: Path,
    config: GADEConfig,
    progress: Optional[Progress] = None,
    task_id: Optional[Any] = None,
) -> AnalysisResult:
    """
    Analyze a repository and compute difficulty for all code regions.
    
    Args:
        repo_path: Path to the repository root
        config: GADE configuration
        progress: Optional Rich progress bar
        task_id: Optional progress task ID
        
    Returns:
        AnalysisResult with all difficulty nodes
    """
    result = AnalysisResult(
        repo_path=repo_path,
        analysis_timestamp=datetime.now().isoformat(),
    )
    
    # Find all matching files
    files = find_matching_files(repo_path, config)
    result.total_files = len(files)
    
    if progress and task_id:
        progress.update(task_id, description=f"Found {len(files)} files")
    
    # Initialize signal plugins
    signals = get_all_signals()
    
    # Build context for signals
    context = {
        "repo_path": repo_path,
        "gade_dir": repo_path / ".gade",
    }
    
    # Analyze each file
    for i, file_path in enumerate(files):
        if progress and task_id:
            progress.update(
                task_id,
                description=f"Analyzing {file_path.name} ({i+1}/{len(files)})"
            )
        
        try:
            file_nodes = analyze_file(file_path, signals, context, config)
            result.nodes.extend(file_nodes)
            result.total_functions += len([n for n in file_nodes if n.node_type == "function"])
        except Exception as e:
            # Skip files that fail to parse
            continue
    
    # Sort by difficulty
    result.nodes.sort(key=lambda n: n.difficulty_score, reverse=True)
    
    if progress and task_id:
        progress.update(task_id, description="Analysis complete")
    
    return result


def find_matching_files(repo_path: Path, config: GADEConfig) -> list[Path]:
    """Find all files matching include/exclude patterns."""
    files = []
    
    for pattern in config.include_patterns:
        # Handle glob patterns properly
        # *.py -> search for *.py recursively
        search_pattern = pattern.lstrip("*")  # *.py -> .py won't work
        if pattern.startswith("*."):
            # Extension pattern like *.py - use ** prefix for recursive search
            search_pattern = f"**/{pattern}"
        
        for file_path in repo_path.glob(search_pattern):
            if file_path.is_file():
                # Check exclude patterns
                rel_path = str(file_path.relative_to(repo_path))
                excluded = False
                
                for exclude in config.exclude_patterns:
                    # Check against relative path
                    if fnmatch.fnmatch(rel_path, exclude):
                        excluded = True
                        break
                    if fnmatch.fnmatch(rel_path.replace("\\", "/"), exclude):
                        excluded = True
                        break
                
                if not excluded:
                    files.append(file_path)
    
    return sorted(set(files))


def analyze_file(
    file_path: Path,
    signals: list[Any],
    context: dict[str, Any],
    config: GADEConfig,
) -> list[DifficultyNode]:
    """
    Analyze a single file and extract difficulty nodes.
    
    Extracts:
    - File-level node
    - Function-level nodes
    - Class-level nodes
    """
    nodes = []
    
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return nodes
    
    lines = content.splitlines()
    total_lines = len(lines)
    
    if total_lines == 0:
        return nodes
    
    # File-level node
    file_node = create_node(
        file_path=file_path,
        ast_range=(1, total_lines),
        node_type="file",
        node_name=file_path.name,
        signals=signals,
        context=context,
        config=config,
    )
    nodes.append(file_node)
    
    # Extract function/class nodes based on file type
    suffix = file_path.suffix.lower()
    
    if suffix == ".py":
        func_nodes = extract_python_nodes(file_path, content, signals, context, config)
        nodes.extend(func_nodes)
    elif suffix in (".js", ".ts", ".jsx", ".tsx"):
        func_nodes = extract_js_nodes(file_path, content, signals, context, config)
        nodes.extend(func_nodes)
    elif suffix == ".go":
        func_nodes = extract_go_nodes(file_path, content, signals, context, config)
        nodes.extend(func_nodes)
    else:
        # Generic function extraction
        func_nodes = extract_generic_nodes(file_path, content, signals, context, config)
        nodes.extend(func_nodes)
    
    return nodes


def create_node(
    file_path: Path,
    ast_range: tuple[int, int],
    node_type: str,
    node_name: str,
    signals: list[Any],
    context: dict[str, Any],
    config: GADEConfig,
) -> DifficultyNode:
    """Create a DifficultyNode with computed signals."""
    # Compute all signals
    signal_values = {}
    
    for signal in signals:
        try:
            value = signal.compute(file_path, ast_range, context)
            signal_values[signal.name] = value
        except Exception:
            signal_values[signal.name] = 0.0
    
    vector = SignalVector(
        edit_churn=signal_values.get("edit_churn", 0.0),
        error_density=signal_values.get("error_density", 0.0),
        semantic_complexity=signal_values.get("semantic_complexity", 0.0),
        uncertainty_proxy=signal_values.get("uncertainty_proxy", 0.0),
        gradient_proxy=signal_values.get("gradient_proxy", 0.0),
    )
    
    node = DifficultyNode(
        id=DifficultyNode.generate_id(file_path, ast_range),
        file_path=file_path,
        ast_range=ast_range,
        node_type=node_type,
        node_name=node_name,
        signals=vector,
    )
    
    # Compute difficulty score using EMA
    node.update_difficulty(alpha=config.alpha)
    
    return node


def extract_python_nodes(
    file_path: Path,
    content: str,
    signals: list[Any],
    context: dict[str, Any],
    config: GADEConfig,
) -> list[DifficultyNode]:
    """Extract function and class nodes from Python code."""
    import ast
    
    nodes = []
    
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return nodes
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            start_line = node.lineno
            end_line = node.end_lineno or start_line
            
            diff_node = create_node(
                file_path=file_path,
                ast_range=(start_line, end_line),
                node_type="function",
                node_name=node.name,
                signals=signals,
                context=context,
                config=config,
            )
            nodes.append(diff_node)
            
        elif isinstance(node, ast.AsyncFunctionDef):
            start_line = node.lineno
            end_line = node.end_lineno or start_line
            
            diff_node = create_node(
                file_path=file_path,
                ast_range=(start_line, end_line),
                node_type="function",
                node_name=f"async {node.name}",
                signals=signals,
                context=context,
                config=config,
            )
            nodes.append(diff_node)
            
        elif isinstance(node, ast.ClassDef):
            start_line = node.lineno
            end_line = node.end_lineno or start_line
            
            diff_node = create_node(
                file_path=file_path,
                ast_range=(start_line, end_line),
                node_type="class",
                node_name=node.name,
                signals=signals,
                context=context,
                config=config,
            )
            nodes.append(diff_node)
    
    return nodes


def extract_js_nodes(
    file_path: Path,
    content: str,
    signals: list[Any],
    context: dict[str, Any],
    config: GADEConfig,
) -> list[DifficultyNode]:
    """Extract function nodes from JavaScript/TypeScript code."""
    import re
    
    nodes = []
    lines = content.splitlines()
    
    # Match function declarations
    func_patterns = [
        r"(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(",
        r"(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s+)?\(",
        r"(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s+)?function",
    ]
    
    for i, line in enumerate(lines, 1):
        for pattern in func_patterns:
            match = re.search(pattern, line)
            if match:
                func_name = match.group(1)
                
                # Find end of function (heuristic: matching braces)
                end_line = find_block_end(lines, i - 1)
                
                diff_node = create_node(
                    file_path=file_path,
                    ast_range=(i, end_line),
                    node_type="function",
                    node_name=func_name,
                    signals=signals,
                    context=context,
                    config=config,
                )
                nodes.append(diff_node)
                break
    
    return nodes


def extract_go_nodes(
    file_path: Path,
    content: str,
    signals: list[Any],
    context: dict[str, Any],
    config: GADEConfig,
) -> list[DifficultyNode]:
    """Extract function nodes from Go code."""
    import re
    
    nodes = []
    lines = content.splitlines()
    
    func_pattern = r"func\s+(?:\([^)]+\)\s+)?(\w+)\s*\("
    
    for i, line in enumerate(lines, 1):
        match = re.search(func_pattern, line)
        if match:
            func_name = match.group(1)
            end_line = find_block_end(lines, i - 1)
            
            diff_node = create_node(
                file_path=file_path,
                ast_range=(i, end_line),
                node_type="function",
                node_name=func_name,
                signals=signals,
                context=context,
                config=config,
            )
            nodes.append(diff_node)
    
    return nodes


def extract_generic_nodes(
    file_path: Path,
    content: str,
    signals: list[Any],
    context: dict[str, Any],
    config: GADEConfig,
) -> list[DifficultyNode]:
    """Extract nodes using generic heuristics."""
    import re
    
    nodes = []
    lines = content.splitlines()
    
    # Generic function pattern
    func_pattern = r"(?:def|function|func|fn)\s+(\w+)\s*\("
    
    for i, line in enumerate(lines, 1):
        match = re.search(func_pattern, line)
        if match:
            func_name = match.group(1)
            end_line = find_block_end(lines, i - 1)
            
            diff_node = create_node(
                file_path=file_path,
                ast_range=(i, end_line),
                node_type="function",
                node_name=func_name,
                signals=signals,
                context=context,
                config=config,
            )
            nodes.append(diff_node)
    
    return nodes


def find_block_end(lines: list[str], start_idx: int) -> int:
    """
    Find the end of a code block starting at start_idx.
    
    Uses brace counting for C-style languages,
    indentation for Python-style.
    """
    if start_idx >= len(lines):
        return start_idx + 1
    
    start_line = lines[start_idx]
    
    # Check if this looks like Python (uses indentation)
    if start_line.rstrip().endswith(":"):
        # Python-style: find where indentation decreases
        if start_idx + 1 >= len(lines):
            return start_idx + 1
        
        # Get base indentation of the definition
        base_indent = len(start_line) - len(start_line.lstrip())
        
        for i in range(start_idx + 1, len(lines)):
            line = lines[i]
            if not line.strip():
                continue
            
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= base_indent:
                return i
        
        return len(lines)
    
    # Brace counting for C-style languages
    brace_count = 0
    started = False
    
    for i in range(start_idx, len(lines)):
        line = lines[i]
        for char in line:
            if char == "{":
                brace_count += 1
                started = True
            elif char == "}":
                brace_count -= 1
        
        if started and brace_count <= 0:
            return i + 1
    
    return len(lines)
