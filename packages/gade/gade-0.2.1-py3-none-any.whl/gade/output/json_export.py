"""
JSON export utilities for GADE.
"""

from __future__ import annotations

import json
from pathlib import Path

from gade.models import AnalysisResult, DifficultyNode


def export_difficulty_map(
    result: AnalysisResult,
    output_path: Path,
) -> None:
    """
    Export difficulty_map.json with all region scores.
    
    Format:
    {
        "repo_path": "/path/to/repo",
        "timestamp": "2024-01-01T00:00:00",
        "files": {
            "file.py": {
                "score": 0.5,
                "tier": "standard",
                "regions": [...]
            }
        }
    }
    """
    # Group by file
    by_file: dict[str, dict] = {}
    
    for node in result.nodes:
        file_key = str(node.file_path)
        
        if file_key not in by_file:
            by_file[file_key] = {
                "score": 0.0,
                "tier": "compress",
                "signals": {},
                "regions": [],
            }
        
        if node.node_type == "file":
            by_file[file_key]["score"] = node.difficulty_score
            by_file[file_key]["tier"] = node.difficulty_tier
            by_file[file_key]["signals"] = node.signals.to_dict()
        else:
            by_file[file_key]["regions"].append({
                "name": node.node_name,
                "type": node.node_type,
                "range": list(node.ast_range),
                "score": node.difficulty_score,
                "tier": node.difficulty_tier,
            })
    
    output = {
        "repo_path": str(result.repo_path),
        "timestamp": result.analysis_timestamp,
        "total_files": result.total_files,
        "total_functions": result.total_functions,
        "average_difficulty": result.average_difficulty,
        "files": by_file,
    }
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)


def export_ranked_regions(
    result: AnalysisResult,
    output_path: Path,
    top_k: int = 50,
) -> None:
    """
    Export ranked_regions.json with top-K hardest regions.
    
    Format:
    [
        {
            "rank": 1,
            "file": "file.py",
            "name": "complex_function",
            "type": "function",
            "range": [10, 50],
            "score": 0.85,
            "tier": "debate",
            "signals": {...}
        }
    ]
    """
    top_nodes = result.get_top_k(top_k)
    
    output = []
    
    for i, node in enumerate(top_nodes, 1):
        output.append({
            "rank": i,
            "id": node.id,
            "file": str(node.file_path),
            "name": node.node_name,
            "type": node.node_type,
            "range": list(node.ast_range),
            "score": node.difficulty_score,
            "tier": node.difficulty_tier,
            "signals": node.signals.to_dict(),
        })
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)


def load_difficulty_map(input_path: Path) -> dict:
    """Load a difficulty map from JSON."""
    with open(input_path) as f:
        return json.load(f)


def load_ranked_regions(input_path: Path) -> list[dict]:
    """Load ranked regions from JSON."""
    with open(input_path) as f:
        return json.load(f)


def compare_results(
    before: AnalysisResult,
    after: AnalysisResult,
) -> dict:
    """
    Compare two analysis results to measure difficulty delta.
    
    Returns statistics on improvement/regression.
    """
    before_by_id = {n.id: n for n in before.nodes}
    after_by_id = {n.id: n for n in after.nodes}
    
    common_ids = set(before_by_id.keys()) & set(after_by_id.keys())
    
    improvements = []
    regressions = []
    
    for node_id in common_ids:
        before_node = before_by_id[node_id]
        after_node = after_by_id[node_id]
        
        delta = after_node.difficulty_score - before_node.difficulty_score
        
        if delta < -0.05:  # Significant improvement
            improvements.append({
                "name": before_node.node_name,
                "file": str(before_node.file_path),
                "before": before_node.difficulty_score,
                "after": after_node.difficulty_score,
                "delta": delta,
            })
        elif delta > 0.05:  # Significant regression
            regressions.append({
                "name": before_node.node_name,
                "file": str(before_node.file_path),
                "before": before_node.difficulty_score,
                "after": after_node.difficulty_score,
                "delta": delta,
            })
    
    avg_before = before.average_difficulty
    avg_after = after.average_difficulty
    
    return {
        "before_average": avg_before,
        "after_average": avg_after,
        "overall_delta": avg_after - avg_before,
        "improvements": len(improvements),
        "regressions": len(regressions),
        "improved_regions": sorted(improvements, key=lambda x: x["delta"])[:10],
        "regressed_regions": sorted(regressions, key=lambda x: -x["delta"])[:10],
    }
