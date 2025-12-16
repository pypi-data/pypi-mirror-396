"""
Reasoning strategies by difficulty tier.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional

from gade.llm.client import LLMClient


class ReasoningStrategy(ABC):
    """Base class for difficulty-tier reasoning strategies."""
    
    name: str = "base"
    description: str = "Base strategy"
    
    def __init__(self, client: LLMClient):
        self.client = client
        self.tokens_used = 0
    
    @abstractmethod
    def execute(
        self,
        code: str,
        context: dict[str, Any],
        budget: int,
    ) -> dict[str, Any]:
        """
        Execute the reasoning strategy.
        
        Args:
            code: Code to process
            context: Additional context
            budget: Token budget for this execution
            
        Returns:
            Result with analysis/refactored code
        """
        pass


class CompressStrategy(ReasoningStrategy):
    """
    Strategy for easy code (D < 0.2).
    
    Simply summarizes the code with minimal token usage.
    """
    
    name = "compress"
    description = "Summarize simple code"
    
    def execute(
        self,
        code: str,
        context: dict[str, Any],
        budget: int,
    ) -> dict[str, Any]:
        # For very easy code, just provide a quick summary
        prompt = f"""Summarize this code in one sentence:

```
{code[:500]}
```"""
        
        response = self.client.complete(
            prompt=prompt,
            max_tokens=min(100, budget),
        )
        
        self.tokens_used = response.get("tokens_used", 0)
        
        return {
            "strategy": self.name,
            "action": "summarized",
            "summary": response.get("content", ""),
            "tokens_used": self.tokens_used,
            "recommendation": "Code is straightforward, no changes needed.",
        }


class StandardStrategy(ReasoningStrategy):
    """
    Strategy for medium code (0.2 <= D < 0.5).
    
    Standard single-pass analysis.
    """
    
    name = "standard"
    description = "Standard analysis"
    
    def execute(
        self,
        code: str,
        context: dict[str, Any],
        budget: int,
    ) -> dict[str, Any]:
        file_name = context.get("file_name", "code")
        
        prompt = f"""Analyze this code from {file_name}:

```
{code}
```

Provide:
1. Brief summary (1-2 sentences)
2. Key concerns (if any)
3. Recommended action (refactor/leave as-is)"""
        
        response = self.client.complete(
            prompt=prompt,
            max_tokens=min(500, budget),
            system_prompt="Be concise. Focus on actionable insights.",
        )
        
        self.tokens_used = response.get("tokens_used", 0)
        
        return {
            "strategy": self.name,
            "action": "analyzed",
            "analysis": response.get("content", ""),
            "tokens_used": self.tokens_used,
            "confidence": response.get("confidence", 0.5),
        }


class DeepStrategy(ReasoningStrategy):
    """
    Strategy for hard code (0.5 <= D < 0.8).
    
    Multi-step analysis with tool usage.
    """
    
    name = "deep"
    description = "Deep analysis with tools"
    
    def execute(
        self,
        code: str,
        context: dict[str, Any],
        budget: int,
    ) -> dict[str, Any]:
        file_name = context.get("file_name", "code")
        
        # Step 1: Understand the code
        understand_prompt = f"""Analyze this complex code from {file_name}:

```
{code}
```

Answer:
1. What is this code's purpose?
2. What are the main data flows?
3. What are the edge cases?"""
        
        understand_response = self.client.complete(
            prompt=understand_prompt,
            max_tokens=min(800, budget // 3),
        )
        
        understanding = understand_response.get("content", "")
        
        # Step 2: Identify issues
        issues_prompt = f"""Given this understanding of the code:
{understanding}

And the code:
```
{code}
```

List specific issues:
1. Complexity hotspots (with line references)
2. Potential bugs
3. Missing error handling
4. Performance concerns"""
        
        issues_response = self.client.complete(
            prompt=issues_prompt,
            max_tokens=min(600, budget // 3),
        )
        
        issues = issues_response.get("content", "")
        
        # Step 3: Propose solution
        solution_prompt = f"""Given these issues:
{issues}

Propose concrete refactoring steps:
1. Specific changes to make
2. Expected difficulty reduction
3. Risk assessment"""
        
        solution_response = self.client.complete(
            prompt=solution_prompt,
            max_tokens=min(600, budget // 3),
        )
        
        self.tokens_used = (
            understand_response.get("tokens_used", 0)
            + issues_response.get("tokens_used", 0)
            + solution_response.get("tokens_used", 0)
        )
        
        return {
            "strategy": self.name,
            "action": "deep_analysis",
            "understanding": understanding,
            "issues": issues,
            "solution": solution_response.get("content", ""),
            "tokens_used": self.tokens_used,
            "steps": 3,
        }


class DebateStrategy(ReasoningStrategy):
    """
    Strategy for critical code (D >= 0.8).
    
    Multi-pass debate with synthesis.
    """
    
    name = "debate"
    description = "Multi-perspective debate"
    
    def execute(
        self,
        code: str,
        context: dict[str, Any],
        budget: int,
    ) -> dict[str, Any]:
        file_name = context.get("file_name", "code")
        
        # Perspective 1: Conservative
        conservative_prompt = f"""You are a CONSERVATIVE code reviewer. 
Your priority is stability and minimal changes.

Review this complex code from {file_name}:
```
{code}
```

Provide:
1. What MUST change (critical issues only)
2. What should NOT change (working parts)
3. Risk of each proposed change"""
        
        conservative = self.client.complete(
            prompt=conservative_prompt,
            max_tokens=min(700, budget // 4),
        )
        
        # Perspective 2: Aggressive
        aggressive_prompt = f"""You are an AGGRESSIVE refactoring advocate.
Your priority is clean, modern, maintainable code.

Review this complex code from {file_name}:
```
{code}
```

Provide:
1. Complete refactoring plan
2. Modern patterns to apply
3. Expected improvement metrics"""
        
        aggressive = self.client.complete(
            prompt=aggressive_prompt,
            max_tokens=min(700, budget // 4),
        )
        
        # Perspective 3: Testing focus
        testing_prompt = f"""You are a TEST ENGINEER.
Your priority is testability and edge cases.

Review this complex code from {file_name}:
```
{code}
```

Provide:
1. Test cases that must exist
2. Untestable parts that need refactoring
3. Edge cases not handled"""
        
        testing = self.client.complete(
            prompt=testing_prompt,
            max_tokens=min(700, budget // 4),
        )
        
        # Synthesis
        synthesis_prompt = f"""Synthesize these three perspectives on the code:

CONSERVATIVE VIEW:
{conservative.get('content', '')}

AGGRESSIVE VIEW:
{aggressive.get('content', '')}

TESTING VIEW:
{testing.get('content', '')}

Provide a FINAL RECOMMENDATION:
1. Priority changes (ranked)
2. Balanced approach
3. Step-by-step implementation plan"""
        
        synthesis = self.client.complete(
            prompt=synthesis_prompt,
            max_tokens=min(900, budget // 4),
        )
        
        self.tokens_used = (
            conservative.get("tokens_used", 0)
            + aggressive.get("tokens_used", 0)
            + testing.get("tokens_used", 0)
            + synthesis.get("tokens_used", 0)
        )
        
        return {
            "strategy": self.name,
            "action": "debate_synthesis",
            "perspectives": {
                "conservative": conservative.get("content", ""),
                "aggressive": aggressive.get("content", ""),
                "testing": testing.get("content", ""),
            },
            "synthesis": synthesis.get("content", ""),
            "tokens_used": self.tokens_used,
            "passes": 4,
        }


def get_strategy_for_tier(tier: str, client: LLMClient) -> ReasoningStrategy:
    """Get appropriate strategy for a difficulty tier."""
    strategies = {
        "compress": CompressStrategy,
        "standard": StandardStrategy,
        "deep": DeepStrategy,
        "debate": DebateStrategy,
    }
    
    strategy_class = strategies.get(tier, StandardStrategy)
    return strategy_class(client)
