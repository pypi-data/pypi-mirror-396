"""
GADE Command Line Interface.

Main entry point for all GADE commands.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.tree import Tree

from gade import __version__
from gade.config import GADEConfig, init_gade_directory
from gade.models import AnalysisResult, ComputeBudget, DifficultyNode

console = Console()


def get_difficulty_color(score: float) -> str:
    """Return Rich color based on difficulty score."""
    if score < 0.2:
        return "green"
    elif score < 0.5:
        return "yellow"
    elif score < 0.8:
        return "orange1"
    else:
        return "red"


def format_difficulty_bar(score: float, width: int = 20) -> str:
    """Create ASCII difficulty bar."""
    filled = int(score * width)
    bar = "█" * filled + "░" * (width - filled)
    return bar


@click.group()
@click.version_option(version=__version__, prog_name="GADE")
def main() -> None:
    """
    GADE - Gradient-Aware Development Environment
    
    Allocate AI attention and compute dynamically based on code difficulty.
    """
    pass


@main.command()
@click.argument("repo_path", type=click.Path(exists=True, file_okay=False, path_type=Path))
def init(repo_path: Path) -> None:
    """Initialize GADE tracking in a repository."""
    gade_dir = init_gade_directory(repo_path)
    console.print(f"[green]✓[/green] Initialized GADE in {gade_dir}")
    console.print("\nConfiguration saved to .gade/config.yaml")
    console.print("Run [cyan]gade analyze .[/cyan] to analyze the codebase.")


@main.command()
@click.argument("repo_path", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--output", "-o", type=click.Choice(["json", "table", "tree"]), default="table")
@click.option("--top", "-k", type=int, default=20, help="Number of top regions to show")
@click.option("--save", is_flag=True, help="Save results to .gade/ directory")
def analyze(repo_path: Path, output: str, top: int, save: bool) -> None:
    """
    Analyze difficulty across a repository.
    
    Scans all supported files, computes difficulty signals,
    and ranks code regions by composite difficulty score.
    """
    repo_path = repo_path.resolve()
    config = GADEConfig.load(repo_path / ".gade" / "config.yaml")
    
    console.print(Panel.fit(
        f"[bold]Analyzing:[/bold] {repo_path.name}",
        title="GADE Difficulty Analysis"
    ))
    
    # Import analyzer here to avoid circular imports
    from gade.analyzer import analyze_repository
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Scanning files...", total=None)
        result = analyze_repository(repo_path, config, progress, task)
    
    # Display results
    if output == "json":
        _output_json(result, top, save, repo_path)
    elif output == "tree":
        _output_tree(result, top)
    else:
        _output_table(result, top)
    
    # Summary
    console.print()
    console.print(f"[bold]Total files:[/bold] {result.total_files}")
    console.print(f"[bold]Total functions:[/bold] {result.total_functions}")
    console.print(f"[bold]Average difficulty:[/bold] {result.average_difficulty:.3f}")


def _output_json(result: AnalysisResult, top: int, save: bool, repo_path: Path) -> None:
    """Output results as JSON."""
    top_nodes = result.get_top_k(top)
    
    difficulty_map = {
        str(node.file_path): {
            "score": node.difficulty_score,
            "tier": node.difficulty_tier,
            "signals": node.signals.to_dict(),
        }
        for node in result.nodes
    }
    
    ranked_regions = [
        {
            "rank": i + 1,
            "file": str(node.file_path),
            "name": node.node_name,
            "type": node.node_type,
            "range": list(node.ast_range),
            "score": node.difficulty_score,
            "tier": node.difficulty_tier,
        }
        for i, node in enumerate(top_nodes)
    ]
    
    if save:
        gade_dir = repo_path / ".gade"
        gade_dir.mkdir(exist_ok=True)
        
        with open(gade_dir / "difficulty_map.json", "w") as f:
            json.dump(difficulty_map, f, indent=2)
        
        with open(gade_dir / "ranked_regions.json", "w") as f:
            json.dump(ranked_regions, f, indent=2)
        
        console.print(f"[green]✓[/green] Saved to .gade/difficulty_map.json")
        console.print(f"[green]✓[/green] Saved to .gade/ranked_regions.json")
    else:
        console.print_json(json.dumps(ranked_regions, indent=2))


def _output_table(result: AnalysisResult, top: int) -> None:
    """Output results as Rich table."""
    table = Table(title=f"Top {top} Hardest Regions")
    
    table.add_column("Rank", style="dim", width=5)
    table.add_column("Difficulty", width=25)
    table.add_column("Score", width=8)
    table.add_column("Tier", width=10)
    table.add_column("Name", style="cyan")
    table.add_column("File", style="dim")
    
    for i, node in enumerate(result.get_top_k(top)):
        color = get_difficulty_color(node.difficulty_score)
        bar = format_difficulty_bar(node.difficulty_score)
        
        table.add_row(
            str(i + 1),
            f"[{color}]{bar}[/{color}]",
            f"{node.difficulty_score:.3f}",
            f"[{color}]{node.difficulty_tier}[/{color}]",
            node.node_name or "(file)",
            str(node.file_path.name),
        )
    
    console.print(table)


def _output_tree(result: AnalysisResult, top: int) -> None:
    """Output results as tree view."""
    tree = Tree("[bold]📊 Difficulty Hierarchy")
    
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
    )[:top]
    
    for file_path, nodes in sorted_files:
        file_max = max(n.difficulty_score for n in nodes)
        color = get_difficulty_color(file_max)
        
        file_branch = tree.add(
            f"[{color}]📄 {file_path.name}[/{color}] ({file_max:.2f})"
        )
        
        sorted_nodes = sorted(nodes, key=lambda n: n.difficulty_score, reverse=True)[:5]
        for node in sorted_nodes:
            node_color = get_difficulty_color(node.difficulty_score)
            icon = "🔧" if node.node_type == "function" else "📦"
            file_branch.add(
                f"{icon} [{node_color}]{node.node_name or 'module'}[/{node_color}] "
                f"({node.difficulty_score:.2f})"
            )
    
    console.print(tree)


@main.command()
@click.argument("repo_path", type=click.Path(exists=True, file_okay=False, path_type=Path))
def heatmap(repo_path: Path) -> None:
    """Display terminal heatmap of difficulty across files."""
    repo_path = repo_path.resolve()
    config = GADEConfig.load(repo_path / ".gade" / "config.yaml")
    
    from gade.analyzer import analyze_repository
    from gade.output.heatmap import render_heatmap
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing...", total=None)
        result = analyze_repository(repo_path, config, progress, task)
    
    render_heatmap(result, console)


@main.command()
@click.option("--top", "-k", type=int, default=10, help="Number of regions to refactor")
@click.option("--budget", "-b", type=int, default=50000, help="Token budget")
@click.option("--dry-run", is_flag=True, help="Show plan without executing")
@click.argument("repo_path", type=click.Path(exists=True, file_okay=False, path_type=Path))
def refactor(repo_path: Path, top: int, budget: int, dry_run: bool) -> None:
    """
    Apply AI-assisted refactoring to hardest regions.
    
    Allocates 80% of compute budget to top 20% difficulty regions.
    """
    repo_path = repo_path.resolve()
    config = GADEConfig.load(repo_path / ".gade" / "config.yaml")
    
    from gade.analyzer import analyze_repository
    from gade.allocation import create_refactor_plan
    
    console.print(Panel.fit(
        f"[bold]Budget:[/bold] {budget:,} tokens\n"
        f"[bold]Top regions:[/bold] {top}",
        title="GADE Refactor"
    ))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing difficulty...", total=None)
        result = analyze_repository(repo_path, config, progress, task)
    
    # Create allocation plan
    target_nodes = result.get_top_k(top)
    compute_budget = ComputeBudget.from_difficulty_ranking(target_nodes, budget)
    plan = create_refactor_plan(target_nodes, compute_budget)
    
    # Display plan
    table = Table(title="Refactor Plan")
    table.add_column("Region")
    table.add_column("Difficulty")
    table.add_column("Strategy")
    table.add_column("Tokens")
    
    for item in plan:
        color = get_difficulty_color(item["difficulty"])
        table.add_row(
            item["name"],
            f"[{color}]{item['difficulty']:.3f}[/{color}]",
            item["strategy"],
            f"{item['tokens']:,}",
        )
    
    console.print(table)
    
    if dry_run:
        console.print("\n[yellow]Dry run - no changes applied[/yellow]")
        return
    
    # Execute refactoring
    from gade.refactor import execute_refactor
    
    if click.confirm("\nProceed with refactoring?"):
        execute_refactor(target_nodes, compute_budget, config, console)


@main.command()
@click.option("--host", "-h", default="0.0.0.0", help="Host to bind to")
@click.option("--port", "-p", type=int, default=8000, help="Port to bind to")
def serve(host: str, port: int) -> None:
    """Start the GADE REST API server."""
    try:
        from gade.api.server import run_server
        console.print(f"[green]Starting GADE API server on {host}:{port}[/green]")
        console.print(f"[dim]Docs: http://{host}:{port}/docs[/dim]")
        run_server(host=host, port=port)
    except ImportError:
        console.print("[red]FastAPI not installed.[/red]")
        console.print("Install with: pip install gade[api]")


@main.command("serve-mcp")
def serve_mcp() -> None:
    """Start the GADE MCP server for Claude Desktop integration."""
    try:
        from gade.mcp.server import main as mcp_main
        console.print("[green]Starting GADE MCP server...[/green]")
        mcp_main()
    except ImportError:
        console.print("[red]MCP not installed.[/red]")
        console.print("Install with: pip install gade[mcp]")


@main.command()
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option("--top", "-k", type=int, default=3, help="Number of regions to improve")
@click.option("--budget", "-b", type=int, default=4000, help="Token budget per region")
@click.option("--dry-run/--no-dry-run", default=True, help="Preview without changes")
def improve(path: str, top: int, budget: int, dry_run: bool) -> None:
    """Improve top-K hardest regions using LLM refactoring.
    
    Example:
        gade improve ./src --top 3 --budget 4000
        gade improve ./src --top 5 --no-dry-run
    """
    from gade.improve import improve_repository
    
    repo_path = Path(path).resolve()
    
    console.print(Panel(
        f"[bold]Improving: {repo_path.name}[/bold]\n"
        f"Top {top} regions | Budget: {budget} tokens | Dry run: {dry_run}",
        title="GADE Improve",
        border_style="cyan"
    ))
    
    results = improve_repository(
        repo_path,
        top_k=top,
        budget=budget,
        dry_run=dry_run
    )
    
    if not results:
        console.print("[yellow]No regions found to improve.[/yellow]")
        return
    
    # Show results table
    table = Table(title="Improvement Results")
    table.add_column("Region", style="cyan")
    table.add_column("Original", justify="right")
    table.add_column("New", justify="right")
    table.add_column("Delta", justify="right")
    table.add_column("Status")
    
    for r in results:
        delta_color = "green" if r.delta < 0 else "red" if r.delta > 0 else "dim"
        status = "[OK]" if r.improved else "[SKIP]" if r.error else "[-]"
        table.add_row(
            r.region_name,
            f"{r.original_score:.3f}",
            f"{r.new_score:.3f}",
            f"[{delta_color}]{r.delta:+.3f}[/{delta_color}]",
            status
        )
    
    console.print(table)


@main.command()
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option("--show/--no-show", default=True, help="Show memory stats")
@click.option("--clear", is_flag=True, help="Clear stored memory")
def memory(path: str, show: bool, clear: bool) -> None:
    """Manage persistent difficulty memory.
    
    Example:
        gade memory ./src           # Show stats
        gade memory ./src --clear   # Clear memory
    """
    from gade.memory import DifficultyMemory
    
    repo_path = Path(path).resolve()
    mem = DifficultyMemory(repo_path)
    mem.load()
    
    if clear:
        mem.clear()
        console.print(f"[green]Cleared difficulty memory for {repo_path.name}[/green]")
        return
    
    if show:
        stats = mem.get_stats()
        
        if stats["total_regions"] == 0:
            console.print(f"[yellow]No difficulty memory stored for {repo_path.name}[/yellow]")
            console.print("[dim]Run 'gade analyze' or 'gade improve' to build memory.[/dim]")
            return
        
        console.print(Panel(
            f"[bold]Difficulty Memory: {repo_path.name}[/bold]\n\n"
            f"Total regions: {stats['total_regions']}\n"
            f"Average difficulty: {stats['avg_difficulty']:.3f}\n"
            f"Max difficulty: {stats['max_difficulty']:.3f}\n"
            f"Min difficulty: {stats['min_difficulty']:.3f}",
            title="Memory Stats",
            border_style="blue"
        ))


@main.command()
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option("--top", "-k", type=int, default=10, help="Number of regions to benchmark")
@click.option("--output", "-o", type=click.Path(), help="Save results to JSON file")
def benchmark(path: str, top: int, output: str) -> None:
    """Run benchmark comparing baseline vs GADE allocation.
    
    Example:
        gade benchmark ./src --top 10
        gade benchmark ./src -o results.json
    """
    from gade.benchmark import BenchmarkHarness
    
    repo_path = Path(path).resolve()
    
    console.print(Panel(
        f"[bold]Benchmarking: {repo_path.name}[/bold]\n"
        f"Regions: {top}",
        title="GADE Benchmark",
        border_style="cyan"
    ))
    
    harness = BenchmarkHarness(repo_path)
    result = harness.run_benchmark(top_k=top)
    
    # Print report
    console.print(harness.print_report(result))
    
    # Save if requested
    if output:
        harness.save_results(Path(output))
        console.print(f"\n[green]Results saved to {output}[/green]")


if __name__ == "__main__":
    main()


