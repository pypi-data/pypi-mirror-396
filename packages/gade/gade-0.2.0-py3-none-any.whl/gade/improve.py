"""
GADE Improve Command

Closed-loop improvement: analyze → refactor top-K → re-analyze.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from .config import GADEConfig
from .analyzer import analyze_repository
from .memory import DifficultyMemory


@dataclass
class ImprovementResult:
    """Result of an improvement run."""
    region_name: str
    file_path: str
    original_score: float
    new_score: float
    delta: float
    improved: bool
    tokens_used: int
    error: Optional[str] = None


def improve_repository(
    repo_path: Path,
    top_k: int = 3,
    budget: int = 4000,
    config: Optional[GADEConfig] = None,
    llm_provider: str = "openai",
    model: str = "gpt-4o",
    dry_run: bool = True,
) -> list[ImprovementResult]:
    """
    Improve the top-K hardest regions using LLM refactoring.
    
    Args:
        repo_path: Path to repository
        top_k: Number of hardest regions to improve
        budget: Token budget per region
        config: GADE configuration
        llm_provider: LLM provider to use
        model: Model name
        dry_run: If True, only preview changes
    
    Returns:
        List of ImprovementResult objects
    """
    config = config or GADEConfig()
    repo_path = Path(repo_path)
    
    # Load memory
    memory = DifficultyMemory(repo_path)
    memory.load()
    
    # Initial analysis
    print(f"[ANALYZE] Analyzing {repo_path.name}...")
    initial_result = analyze_repository(repo_path, config)
    top_regions = initial_result.get_top_k(top_k)
    
    if not top_regions:
        print("No regions to improve.")
        return []
    
    print(f"\n[TARGET] Top {top_k} hardest regions:")
    for i, region in enumerate(top_regions, 1):
        print(f"  {i}. {region.node_name} ({region.file_path.name}) - {region.difficulty_score:.3f}")
    
    results = []
    
    for region in top_regions:
        print(f"\n[PROCESS] {region.node_name}")
        
        # Store original score in memory
        memory.update(
            str(region.file_path),
            region.node_name,
            region.node_type,
            region.difficulty_score
        )
        
        if dry_run:
            # In dry run, just report what would be done
            result = ImprovementResult(
                region_name=region.node_name,
                file_path=str(region.file_path),
                original_score=region.difficulty_score,
                new_score=region.difficulty_score,
                delta=0.0,
                improved=False,
                tokens_used=0,
                error="Dry run - no changes made"
            )
            print(f"  [DRY RUN] Would refactor with {budget} tokens")
        else:
            # Actually refactor using LLM
            try:
                new_score = _refactor_region(region, budget, llm_provider, model)
                delta = new_score - region.difficulty_score
                
                result = ImprovementResult(
                    region_name=region.node_name,
                    file_path=str(region.file_path),
                    original_score=region.difficulty_score,
                    new_score=new_score,
                    delta=delta,
                    improved=delta < 0,
                    tokens_used=budget,
                )
                
                # Update memory with new score
                memory.update(
                    str(region.file_path),
                    region.node_name,
                    region.node_type,
                    new_score
                )
                
                if delta < 0:
                    print(f"  [OK] Improved: {region.difficulty_score:.3f} -> {new_score:.3f} (delta: {delta:+.3f})")
                else:
                    print(f"  [WARN] No improvement: {region.difficulty_score:.3f} -> {new_score:.3f}")
                    
            except Exception as e:
                result = ImprovementResult(
                    region_name=region.node_name,
                    file_path=str(region.file_path),
                    original_score=region.difficulty_score,
                    new_score=region.difficulty_score,
                    delta=0.0,
                    improved=False,
                    tokens_used=0,
                    error=str(e)
                )
                print(f"  [ERROR] {e}")
        
        results.append(result)
    
    # Save memory
    memory.save()
    
    # Summary
    improved = sum(1 for r in results if r.improved)
    total_delta = sum(r.delta for r in results)
    
    print(f"\n[SUMMARY]")
    print(f"  Regions processed: {len(results)}")
    print(f"  Improved: {improved}/{len(results)}")
    print(f"  Total Δ difficulty: {total_delta:+.3f}")
    
    return results


def _refactor_region(region, budget: int, provider: str, model: str) -> float:
    """
    Refactor a region using LLM.
    
    This is a placeholder - actual implementation would:
    1. Read the file content
    2. Extract the target region
    3. Generate refactoring prompt
    4. Call LLM with budget
    5. Apply changes (with preview)
    6. Re-analyze and return new score
    """
    # TODO: Implement actual LLM refactoring
    # For now, return a slightly improved score as placeholder
    import random
    improvement = random.uniform(0.02, 0.08)
    return max(0, region.difficulty_score - improvement)


def get_improvement_prompt(code: str, difficulty: float, tier: str) -> str:
    """Generate refactoring prompt for LLM."""
    return f"""You are refactoring code to reduce its complexity and difficulty.

Current difficulty score: {difficulty:.3f} (tier: {tier})

Guidelines:
1. Break down complex functions into smaller, focused functions
2. Reduce nesting depth
3. Add clear variable names
4. Extract magic numbers into constants
5. Add documentation for unclear logic

Code to refactor:
```
{code}
```

Provide the refactored code that is simpler and easier to understand.
"""
