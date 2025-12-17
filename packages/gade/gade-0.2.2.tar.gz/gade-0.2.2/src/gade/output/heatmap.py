"""
Terminal heatmap visualization for GADE.
"""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from gade.models import AnalysisResult, DifficultyNode


# Heatmap color gradient (green -> yellow -> orange -> red)
HEATMAP_COLORS = [
    (0.0, "bright_green"),
    (0.2, "green"),
    (0.4, "yellow"),
    (0.6, "orange1"),
    (0.8, "red"),
    (1.0, "bright_red"),
]


def get_heatmap_color(score: float) -> str:
    """Get Rich color for a difficulty score."""
    for threshold, color in HEATMAP_COLORS:
        if score <= threshold:
            return color
    return "bright_red"


def render_heatmap(
    result: AnalysisResult,
    console: Console,
    max_files: int = 30,
    show_functions: bool = True,
) -> None:
    """
    Render terminal heatmap of difficulty across files.
    
    Shows color-coded difficulty visualization with optional
    function-level breakdown.
    """
    # Group by file
    by_file: dict[Path, list[DifficultyNode]] = {}
    for node in result.nodes:
        if node.file_path not in by_file:
            by_file[node.file_path] = []
        by_file[node.file_path].append(node)
    
    # Sort files by max difficulty
    sorted_files = sorted(
        by_file.items(),
        key=lambda x: max(n.difficulty_score for n in x[1]),
        reverse=True
    )[:max_files]
    
    # Create header
    console.print()
    console.print(Panel.fit(
        "[bold]Difficulty Heatmap[/bold]\n"
        "🟢 Low (<0.2)  🟡 Medium (0.2-0.5)  🟠 High (0.5-0.8)  🔴 Critical (≥0.8)",
        title="GADE"
    ))
    console.print()
    
    # Render each file
    for file_path, nodes in sorted_files:
        # Get file-level node
        file_nodes = [n for n in nodes if n.node_type == "file"]
        file_score = file_nodes[0].difficulty_score if file_nodes else 0.0
        
        # Create file header with heatmap bar
        color = get_heatmap_color(file_score)
        bar = render_difficulty_bar(file_score, width=30)
        
        rel_path = file_path.name
        try:
            rel_path = str(file_path.relative_to(result.repo_path))
        except ValueError:
            pass
        
        file_text = Text()
        file_text.append("📄 ", style="dim")
        file_text.append(rel_path, style=f"bold {color}")
        file_text.append(f"  {bar}  ", style=color)
        file_text.append(f"{file_score:.3f}", style=f"bold {color}")
        
        console.print(file_text)
        
        # Show function-level breakdown if enabled
        if show_functions:
            func_nodes = [
                n for n in nodes
                if n.node_type in ("function", "class", "method")
            ]
            func_nodes.sort(key=lambda n: n.difficulty_score, reverse=True)
            
            for node in func_nodes[:5]:  # Top 5 per file
                func_color = get_heatmap_color(node.difficulty_score)
                func_bar = render_difficulty_bar(node.difficulty_score, width=20)
                
                icon = "🔧" if node.node_type == "function" else "📦"
                
                func_text = Text()
                func_text.append("    ", style="dim")
                func_text.append(f"{icon} ", style="dim")
                func_text.append(node.node_name[:30], style=func_color)
                func_text.append("  ")
                func_text.append(func_bar, style=func_color)
                func_text.append(f"  {node.difficulty_score:.3f}", style=func_color)
                
                console.print(func_text)
    
    # Summary table
    console.print()
    render_summary_table(result, console)


def render_difficulty_bar(score: float, width: int = 20) -> str:
    """Create ASCII difficulty bar."""
    filled = int(score * width)
    bar = "█" * filled + "░" * (width - filled)
    return bar


def render_summary_table(result: AnalysisResult, console: Console) -> None:
    """Render summary statistics table."""
    table = Table(title="Difficulty Summary", show_header=True)
    
    table.add_column("Tier", style="bold")
    table.add_column("Count")
    table.add_column("% of Total")
    table.add_column("Avg Score")
    
    tiers = ["shallow", "medium", "deep", "critical"]
    tier_colors = {
        "shallow": "green",
        "medium": "yellow",
        "deep": "orange1",
        "critical": "red",
    }
    
    total = len(result.nodes)
    
    for tier in tiers:
        tier_nodes = result.get_by_tier(tier)
        count = len(tier_nodes)
        pct = (count / total * 100) if total > 0 else 0
        avg = (
            sum(n.difficulty_score for n in tier_nodes) / count
            if count > 0 else 0
        )
        
        color = tier_colors[tier]
        
        table.add_row(
            f"[{color}]{tier.capitalize()}[/{color}]",
            str(count),
            f"{pct:.1f}%",
            f"{avg:.3f}",
        )
    
    console.print(table)


def render_file_detail(
    file_path: Path,
    nodes: list[DifficultyNode],
    console: Console,
) -> None:
    """Render detailed view for a single file."""
    console.print()
    console.print(Panel.fit(f"[bold]File: {file_path.name}[/bold]"))
    
    # Read file content
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        lines = content.splitlines()
    except Exception:
        console.print("[red]Could not read file[/red]")
        return
    
    # Sort nodes by start line
    sorted_nodes = sorted(nodes, key=lambda n: n.ast_range[0])
    
    # Create line-level heatmap
    line_scores: dict[int, float] = {}
    
    for node in sorted_nodes:
        start, end = node.ast_range
        for line_num in range(start, end + 1):
            if line_num not in line_scores:
                line_scores[line_num] = node.difficulty_score
            else:
                # Take max if overlapping
                line_scores[line_num] = max(
                    line_scores[line_num],
                    node.difficulty_score
                )
    
    # Render with line numbers and colors
    for i, line in enumerate(lines[:50], 1):  # First 50 lines
        score = line_scores.get(i, 0.0)
        color = get_heatmap_color(score)
        
        line_text = Text()
        line_text.append(f"{i:4d} ", style="dim")
        line_text.append("│ ", style="dim")
        line_text.append(line[:100], style=color)
        
        console.print(line_text)
