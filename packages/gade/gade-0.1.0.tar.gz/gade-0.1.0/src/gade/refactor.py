"""
Refactoring execution engine for GADE.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from gade.config import GADEConfig
from gade.llm import get_client, get_strategy_for_tier
from gade.models import ComputeBudget, DifficultyNode


def execute_refactor(
    nodes: list[DifficultyNode],
    budget: ComputeBudget,
    config: GADEConfig,
    console: Console,
) -> dict[str, Any]:
    """
    Execute refactoring on target nodes.
    
    Applies appropriate strategy based on difficulty tier.
    """
    client = get_client(config.llm)
    results = []
    
    console.print()
    console.print(Panel.fit(
        f"[bold]Processing {len(nodes)} regions[/bold]",
        title="Refactor Execution"
    ))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Starting...", total=len(nodes))
        
        for i, node in enumerate(nodes):
            progress.update(
                task,
                description=f"Processing {node.node_name} ({node.difficulty_tier})",
                completed=i,
            )
            
            # Get token allocation for this node
            node_budget = budget.get_allocation(node.id)
            
            if node_budget == 0:
                continue
            
            # Get appropriate strategy
            strategy = get_strategy_for_tier(node.difficulty_tier, client)
            
            # Read code
            try:
                code = read_code_region(node.file_path, node.ast_range)
            except Exception as e:
                console.print(f"[red]Error reading {node.file_path}: {e}[/red]")
                continue
            
            # Execute strategy
            context = {
                "file_name": node.file_path.name,
                "node_name": node.node_name,
                "node_type": node.node_type,
                "difficulty": node.difficulty_score,
            }
            
            try:
                result = strategy.execute(code, context, node_budget)
                result["node_id"] = node.id
                result["node_name"] = node.node_name
                result["file"] = str(node.file_path)
                results.append(result)
                
                # Update spent tokens
                budget.spent_tokens += result.get("tokens_used", 0)
                
            except Exception as e:
                console.print(f"[red]Error processing {node.node_name}: {e}[/red]")
                continue
        
        progress.update(task, description="Complete", completed=len(nodes))
    
    # Display results summary
    display_refactor_results(results, budget, console)
    
    return {
        "results": results,
        "total_tokens_used": budget.spent_tokens,
        "nodes_processed": len(results),
    }


def read_code_region(file_path: Path, ast_range: tuple[int, int]) -> str:
    """Read code from a specific region of a file."""
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    lines = content.splitlines()
    
    start, end = ast_range
    region_lines = lines[start - 1:end]
    
    return "\n".join(region_lines)


def display_refactor_results(
    results: list[dict[str, Any]],
    budget: ComputeBudget,
    console: Console,
) -> None:
    """Display refactoring results summary."""
    console.print()
    console.print(Panel.fit("[bold]Refactor Results[/bold]"))
    
    for result in results:
        strategy = result.get("strategy", "unknown")
        node_name = result.get("node_name", "unknown")
        tokens = result.get("tokens_used", 0)
        
        console.print(f"\n[cyan]{node_name}[/cyan] ({strategy})")
        console.print(f"Tokens used: {tokens:,}")
        
        # Display key output based on strategy
        if strategy == "compress":
            summary = result.get("summary", "")
            console.print(f"Summary: {summary[:200]}")
            
        elif strategy == "standard":
            analysis = result.get("analysis", "")
            console.print(f"Analysis: {analysis[:300]}...")
            
        elif strategy == "deep":
            solution = result.get("solution", "")
            console.print(f"Solution: {solution[:300]}...")
            
        elif strategy == "debate":
            synthesis = result.get("synthesis", "")
            console.print(f"Synthesis: {synthesis[:300]}...")
    
    # Budget summary
    console.print()
    console.print(f"[bold]Total tokens used:[/bold] {budget.spent_tokens:,} / {budget.total_tokens:,}")
    console.print(f"[bold]Budget utilization:[/bold] {budget.utilization * 100:.1f}%")


def apply_refactoring(
    node: DifficultyNode,
    new_code: str,
    backup: bool = True,
) -> bool:
    """
    Apply refactored code to file.
    
    Creates backup before modification.
    """
    try:
        file_path = node.file_path
        
        # Read original
        original = file_path.read_text(encoding="utf-8")
        lines = original.splitlines()
        
        # Create backup
        if backup:
            backup_path = file_path.with_suffix(f"{file_path.suffix}.gade.bak")
            backup_path.write_text(original, encoding="utf-8")
        
        # Replace region
        start, end = node.ast_range
        new_lines = new_code.splitlines()
        
        modified_lines = lines[:start - 1] + new_lines + lines[end:]
        modified_content = "\n".join(modified_lines)
        
        # Write modified
        file_path.write_text(modified_content, encoding="utf-8")
        
        return True
        
    except Exception:
        return False
