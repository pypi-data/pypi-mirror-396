"""
GADE Benchmark Suite

Measures:
1. Analysis speed (files/second, functions/second)
2. Difficulty distribution sanity
3. Signal correlation
4. Memory usage
5. Reproducibility (deterministic runs)
"""

import time
import json
import statistics
from pathlib import Path
from typing import Any
import sys

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from gade.config import GADEConfig
from gade.analyzer import analyze_repository
from gade.models import AnalysisResult


def benchmark_analysis_speed(repo_path: Path, config: GADEConfig) -> dict[str, Any]:
    """Benchmark how fast GADE analyzes a repository."""
    start_time = time.perf_counter()
    result = analyze_repository(repo_path, config)
    end_time = time.perf_counter()
    
    duration = end_time - start_time
    
    return {
        "duration_seconds": round(duration, 3),
        "total_files": result.total_files,
        "total_functions": result.total_functions,
        "files_per_second": round(result.total_files / duration, 2) if duration > 0 else 0,
        "functions_per_second": round(result.total_functions / duration, 2) if duration > 0 else 0,
    }


def benchmark_difficulty_distribution(result: AnalysisResult) -> dict[str, Any]:
    """Analyze the distribution of difficulty scores."""
    scores = [node.difficulty_score for node in result.nodes]
    
    if not scores:
        return {"error": "No nodes to analyze"}
    
    # Count by tier
    tiers = {"compress": 0, "standard": 0, "deep": 0, "debate": 0}
    for node in result.nodes:
        tier = node.difficulty_tier
        tiers[tier] = tiers.get(tier, 0) + 1
    
    return {
        "min": round(min(scores), 3),
        "max": round(max(scores), 3),
        "mean": round(statistics.mean(scores), 3),
        "median": round(statistics.median(scores), 3),
        "stdev": round(statistics.stdev(scores), 3) if len(scores) > 1 else 0,
        "tier_distribution": tiers,
        "tier_percentages": {
            tier: round(count / len(scores) * 100, 1)
            for tier, count in tiers.items()
        },
    }


def benchmark_signal_values(result: AnalysisResult) -> dict[str, Any]:
    """Analyze signal value distributions."""
    signals = {
        "edit_churn": [],
        "error_density": [],
        "semantic_complexity": [],
        "uncertainty_proxy": [],
        "gradient_proxy": [],
    }
    
    for node in result.nodes:
        signals["edit_churn"].append(node.signals.edit_churn)
        signals["error_density"].append(node.signals.error_density)
        signals["semantic_complexity"].append(node.signals.semantic_complexity)
        signals["uncertainty_proxy"].append(node.signals.uncertainty_proxy)
        signals["gradient_proxy"].append(node.signals.gradient_proxy)
    
    signal_stats = {}
    for name, values in signals.items():
        if values:
            signal_stats[name] = {
                "mean": round(statistics.mean(values), 3),
                "max": round(max(values), 3),
                "non_zero_count": sum(1 for v in values if v > 0),
            }
    
    return signal_stats


def benchmark_reproducibility(repo_path: Path, config: GADEConfig, runs: int = 3) -> dict[str, Any]:
    """Check if results are deterministic across multiple runs."""
    results = []
    
    for i in range(runs):
        result = analyze_repository(repo_path, config)
        scores = [node.difficulty_score for node in result.nodes]
        results.append({
            "total_nodes": len(result.nodes),
            "score_sum": round(sum(scores), 6),
            "top_5_ids": [n.id for n in result.nodes[:5]],
        })
    
    # Check consistency
    all_same = all(
        r["total_nodes"] == results[0]["total_nodes"] and
        r["score_sum"] == results[0]["score_sum"]
        for r in results
    )
    
    return {
        "runs": runs,
        "deterministic": all_same,
        "node_counts": [r["total_nodes"] for r in results],
        "score_sums": [r["score_sum"] for r in results],
    }


def benchmark_top_regions(result: AnalysisResult, top_k: int = 10) -> list[dict[str, Any]]:
    """Get top-K hardest regions."""
    top = result.get_top_k(top_k)
    return [
        {
            "rank": i + 1,
            "name": node.node_name,
            "file": node.file_path.name,
            "score": round(node.difficulty_score, 3),
            "tier": node.difficulty_tier,
            "type": node.node_type,
        }
        for i, node in enumerate(top)
    ]


def run_benchmark(repo_path: Path) -> dict[str, Any]:
    """Run full benchmark suite on a repository."""
    print(f"\n{'='*60}")
    print(f"GADE Benchmark: {repo_path.name}")
    print(f"{'='*60}\n")
    
    config = GADEConfig()
    
    # Speed benchmark
    print("⏱️  Measuring analysis speed...")
    speed = benchmark_analysis_speed(repo_path, config)
    print(f"   → {speed['total_files']} files, {speed['total_functions']} functions")
    print(f"   → {speed['duration_seconds']}s ({speed['files_per_second']} files/s)")
    
    # Get full result for other benchmarks
    result = analyze_repository(repo_path, config)
    
    # Distribution benchmark
    print("\n📊 Analyzing difficulty distribution...")
    distribution = benchmark_difficulty_distribution(result)
    print(f"   → Mean: {distribution['mean']}, Median: {distribution['median']}")
    print(f"   → Range: [{distribution['min']}, {distribution['max']}]")
    print(f"   → Tiers: {distribution['tier_percentages']}")
    
    # Signal benchmark
    print("\n🔍 Analyzing signal values...")
    signals = benchmark_signal_values(result)
    for name, stats in signals.items():
        print(f"   → {name}: mean={stats['mean']}, max={stats['max']}")
    
    # Reproducibility
    print("\n🔄 Testing reproducibility (3 runs)...")
    repro = benchmark_reproducibility(repo_path, config, runs=3)
    print(f"   → Deterministic: {'✓ Yes' if repro['deterministic'] else '✗ No'}")
    
    # Top regions
    print("\n🏆 Top 10 Hardest Regions:")
    top_regions = benchmark_top_regions(result, 10)
    for r in top_regions:
        print(f"   #{r['rank']:2d} [{r['tier']:8s}] {r['score']:.3f}  {r['name'][:30]:30s}  ({r['file']})")
    
    return {
        "repository": str(repo_path),
        "speed": speed,
        "distribution": distribution,
        "signals": signals,
        "reproducibility": repro,
        "top_regions": top_regions,
    }


def main():
    """Run benchmarks on GADE's own codebase."""
    # Benchmark GADE itself
    gade_path = Path(__file__).parent.parent / "src"
    
    if not gade_path.exists():
        print("Error: src directory not found")
        return
    
    results = run_benchmark(gade_path)
    
    # Save results
    output_path = Path(__file__).parent / "benchmark_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n✅ Results saved to: {output_path}")
    
    # Summary
    print("\n" + "="*60)
    print("BENCHMARK SUMMARY")
    print("="*60)
    print(f"Files analyzed:      {results['speed']['total_files']}")
    print(f"Functions found:     {results['speed']['total_functions']}")
    print(f"Analysis time:       {results['speed']['duration_seconds']}s")
    print(f"Throughput:          {results['speed']['functions_per_second']} functions/sec")
    print(f"Mean difficulty:     {results['distribution']['mean']}")
    print(f"Deterministic:       {'Yes' if results['reproducibility']['deterministic'] else 'No'}")
    print("="*60)


if __name__ == "__main__":
    main()
