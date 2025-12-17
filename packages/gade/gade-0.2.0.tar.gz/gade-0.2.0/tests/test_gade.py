"""
Unit tests for GADE.
"""

import pytest
from pathlib import Path
import tempfile
import os


class TestSignalVector:
    """Tests for SignalVector model."""
    
    def test_weighted_sum_defaults(self):
        from gade.models import SignalVector
        
        vector = SignalVector(
            edit_churn=0.5,
            error_density=0.5,
            semantic_complexity=0.5,
            uncertainty_proxy=0.5,
            gradient_proxy=0.5,
        )
        
        result = vector.weighted_sum()
        assert 0.0 <= result <= 1.0
        assert result == pytest.approx(0.5)
    
    def test_weighted_sum_custom_weights(self):
        from gade.models import SignalVector
        
        vector = SignalVector(
            edit_churn=1.0,
            error_density=0.0,
            semantic_complexity=0.0,
            uncertainty_proxy=0.0,
            gradient_proxy=0.0,
        )
        
        weights = {"edit_churn": 1.0}
        result = vector.weighted_sum(weights)
        assert result == pytest.approx(1.0)
    
    def test_signal_bounds(self):
        from gade.models import SignalVector
        
        # Should clamp to bounds
        vector = SignalVector(edit_churn=0.0, error_density=1.0)
        assert vector.edit_churn == 0.0
        assert vector.error_density == 1.0


class TestDifficultyNode:
    """Tests for DifficultyNode model."""
    
    def test_generate_id_deterministic(self):
        from gade.models import DifficultyNode
        
        path = Path("/test/file.py")
        range1 = (1, 10)
        
        id1 = DifficultyNode.generate_id(path, range1)
        id2 = DifficultyNode.generate_id(path, range1)
        
        assert id1 == id2
        assert len(id1) == 16
    
    def test_difficulty_tiers(self):
        from gade.models import DifficultyNode, SignalVector
        
        # Compress tier
        node = DifficultyNode(
            id="test1",
            file_path=Path("/test.py"),
            ast_range=(1, 10),
            difficulty_score=0.1,
            signals=SignalVector(),
        )
        assert node.difficulty_tier == "compress"
        
        # Standard tier
        node.difficulty_score = 0.3
        assert node.difficulty_tier == "standard"
        
        # Deep tier
        node.difficulty_score = 0.6
        assert node.difficulty_tier == "deep"
        
        # Debate tier
        node.difficulty_score = 0.9
        assert node.difficulty_tier == "debate"
    
    def test_update_difficulty_ema(self):
        from gade.models import DifficultyNode, SignalVector
        
        node = DifficultyNode(
            id="test",
            file_path=Path("/test.py"),
            ast_range=(1, 10),
            signals=SignalVector(
                edit_churn=0.8,
                error_density=0.8,
                semantic_complexity=0.8,
                uncertainty_proxy=0.8,
                gradient_proxy=0.8,
            ),
        )
        
        # First update - no history
        score1 = node.update_difficulty(alpha=0.2)
        assert 0.0 <= score1 <= 1.0
        assert len(node.history) == 1
        
        # Second update - uses EMA
        node.signals = SignalVector(
            edit_churn=0.2,
            error_density=0.2,
            semantic_complexity=0.2,
            uncertainty_proxy=0.2,
            gradient_proxy=0.2,
        )
        score2 = node.update_difficulty(alpha=0.2)
        
        # Score should decrease but smoothly
        assert score2 < score1
        assert len(node.history) == 2


class TestComputeBudget:
    """Tests for ComputeBudget model."""
    
    def test_allocation(self):
        from gade.models import ComputeBudget
        
        budget = ComputeBudget(total_tokens=1000)
        
        assert budget.allocate("region1", 500)
        assert budget.spent_tokens == 500
        assert budget.remaining_tokens == 500
        assert budget.get_allocation("region1") == 500
    
    def test_budget_exceeded(self):
        from gade.models import ComputeBudget
        
        budget = ComputeBudget(total_tokens=100)
        
        assert not budget.allocate("region1", 200)
        assert budget.spent_tokens == 0
    
    def test_80_20_allocation(self):
        from gade.models import ComputeBudget, DifficultyNode, SignalVector
        
        # Create nodes with varying difficulty
        nodes = [
            DifficultyNode(
                id=f"node{i}",
                file_path=Path(f"/test{i}.py"),
                ast_range=(1, 10),
                difficulty_score=i * 0.1,
                signals=SignalVector(),
            )
            for i in range(10)
        ]
        
        budget = ComputeBudget.from_difficulty_ranking(nodes, 10000)
        
        # Top 2 nodes (20%) should get ~80% of tokens
        top_2 = sorted(nodes, key=lambda n: n.difficulty_score, reverse=True)[:2]
        top_allocation = sum(budget.get_allocation(n.id) for n in top_2)
        
        assert top_allocation >= 7000  # At least 70%


class TestSemanticComplexitySignal:
    """Tests for semantic complexity signal."""
    
    def test_python_ast_depth(self):
        from gade.signals.semantic_complexity import SemanticComplexitySignal
        
        signal = SemanticComplexitySignal()
        
        # Create temp file with nested code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
def complex_function():
    if True:
        for i in range(10):
            while True:
                if i > 5:
                    try:
                        pass
                    except:
                        pass
""")
            f.flush()
            
            score = signal.compute(Path(f.name), (1, 12))
            
        os.unlink(f.name)
        
        # Should have high complexity due to nesting
        assert score > 0.3
    
    def test_simple_code_low_complexity(self):
        from gade.signals.semantic_complexity import SemanticComplexitySignal
        
        signal = SemanticComplexitySignal()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("x = 1\n")
            f.flush()
            
            score = signal.compute(Path(f.name), (1, 1))
            
        os.unlink(f.name)
        
        # Simple assignment should have low complexity
        assert score < 0.3


class TestErrorDensitySignal:
    """Tests for error density signal."""
    
    def test_todo_detection(self):
        from gade.signals.error_density import ErrorDensitySignal
        
        signal = ErrorDensitySignal()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
# TODO: Fix this
# FIXME: Urgent bug
# HACK: Temporary workaround
def broken():
    pass  # XXX: Review this
""")
            f.flush()
            
            score = signal.compute(Path(f.name), (1, 6))
            
        os.unlink(f.name)
        
        # Should have high error density due to markers
        assert score > 0.3
    
    def test_code_smell_detection(self):
        from gade.signals.error_density import ErrorDensitySignal
        
        signal = ErrorDensitySignal()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
try:
    risky()
except:
    pass
""")
            f.flush()
            
            score = signal.compute(Path(f.name), (1, 5))
            
        os.unlink(f.name)
        
        # Bare except + pass should increase score
        assert score > 0.2


class TestConfig:
    """Tests for configuration management."""
    
    def test_default_config(self):
        from gade.config import GADEConfig
        
        config = GADEConfig()
        
        assert config.alpha == 0.2
        assert 0.1 <= config.alpha <= 0.3
        assert config.default_budget == 50000
    
    def test_signal_weights_normalize(self):
        from gade.config import SignalWeights
        
        # SignalWeights in config doesn't have bounds like SignalVector
        weights = SignalWeights(
            edit_churn=0.5,
            error_density=0.5,
            semantic_complexity=0.5,
            uncertainty_proxy=0.5,
            gradient_proxy=0.5,
        )
        
        normalized = weights.normalize()
        total = (
            normalized.edit_churn
            + normalized.error_density
            + normalized.semantic_complexity
            + normalized.uncertainty_proxy
            + normalized.gradient_proxy
        )
        
        assert total == pytest.approx(1.0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
