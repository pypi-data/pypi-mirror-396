"""
Compute allocation engine for GADE.

Distributes token budget based on difficulty tiers.
"""

from __future__ import annotations

from gade.models import ComputeBudget, DifficultyNode


def create_refactor_plan(
    nodes: list[DifficultyNode],
    budget: ComputeBudget,
) -> list[dict]:
    """
    Create a refactoring plan with token allocations.
    
    Returns list of plan items with:
    - name: Node name
    - difficulty: Difficulty score
    - strategy: AI strategy to use
    - tokens: Allocated tokens
    """
    plan = []
    
    for node in nodes:
        tier = node.difficulty_tier
        strategy = get_strategy_name(tier)
        tokens = budget.get_allocation(node.id)
        
        plan.append({
            "id": node.id,
            "name": node.node_name or node.file_path.name,
            "file": str(node.file_path),
            "range": list(node.ast_range),
            "difficulty": node.difficulty_score,
            "tier": tier,
            "strategy": strategy,
            "tokens": tokens,
        })
    
    return plan


def get_strategy_name(tier: str) -> str:
    """Get human-readable strategy name for a tier."""
    strategies = {
        "compress": "Summarize",
        "standard": "Standard Analysis",
        "deep": "Deep Reasoning + Tools",
        "debate": "Multi-pass Debate",
    }
    return strategies.get(tier, "Unknown")


def allocate_by_tier(
    nodes: list[DifficultyNode],
    total_budget: int,
) -> dict[str, int]:
    """
    Allocate tokens by difficulty tier.
    
    Distribution:
    - compress: 5%
    - standard: 15%
    - deep: 30%
    - debate: 50%
    """
    tier_budgets = {
        "compress": int(total_budget * 0.05),
        "standard": int(total_budget * 0.15),
        "deep": int(total_budget * 0.30),
        "debate": int(total_budget * 0.50),
    }
    
    # Group nodes by tier
    by_tier: dict[str, list[DifficultyNode]] = {
        "compress": [],
        "standard": [],
        "deep": [],
        "debate": [],
    }
    
    for node in nodes:
        by_tier[node.difficulty_tier].append(node)
    
    # Allocate within each tier
    allocations = {}
    
    for tier, tier_nodes in by_tier.items():
        tier_budget = tier_budgets[tier]
        
        if not tier_nodes:
            continue
        
        # Distribute proportionally to difficulty within tier
        total_diff = sum(n.difficulty_score for n in tier_nodes)
        
        for node in tier_nodes:
            if total_diff > 0:
                share = node.difficulty_score / total_diff
            else:
                share = 1.0 / len(tier_nodes)
            
            allocations[node.id] = int(tier_budget * share)
    
    return allocations


def optimize_budget(
    nodes: list[DifficultyNode],
    total_budget: int,
    efficiency_target: float = 0.9,
) -> ComputeBudget:
    """
    Create optimized budget allocation.
    
    Uses 80/20 rule: 80% of tokens to top 20% difficulty.
    """
    budget = ComputeBudget.from_difficulty_ranking(nodes, total_budget)
    
    # Verify allocation meets efficiency target
    if not nodes:
        return budget
    
    top_20_count = max(1, len(nodes) // 5)
    top_nodes = sorted(nodes, key=lambda n: n.difficulty_score, reverse=True)[:top_20_count]
    
    top_allocation = sum(budget.get_allocation(n.id) for n in top_nodes)
    total_allocation = sum(budget.allocation_map.values())
    
    if total_allocation > 0:
        current_ratio = top_allocation / total_allocation
        
        # If we're below target, redistribute
        if current_ratio < efficiency_target * 0.8:
            # Increase top allocations
            for node in top_nodes:
                current = budget.allocation_map.get(node.id, 0)
                budget.allocation_map[node.id] = int(current * 1.2)
    
    return budget
