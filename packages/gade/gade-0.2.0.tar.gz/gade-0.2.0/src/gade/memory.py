"""
GADE Difficulty Memory

Persistent storage for difficulty scores across runs.
Enables EMA smoothing and regression detection.
"""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, asdict


@dataclass
class RegionScore:
    """Stored difficulty score for a code region."""
    region_hash: str
    file_path: str
    node_name: str
    node_type: str
    score: float
    ema_score: float
    last_updated: str
    update_count: int = 1


class DifficultyMemory:
    """
    Persistent difficulty memory with EMA smoothing.
    
    Stores difficulty scores per region across runs, enabling:
    - Historical tracking of difficulty changes
    - EMA-smoothed scores for stability
    - Regression detection (difficulty increases)
    
    Usage:
        memory = DifficultyMemory(repo_path)
        memory.load()
        memory.update("file.py", "function_name", 0.75)
        if memory.detect_regression("file.py", "function_name"):
            print("Warning: Difficulty increased!")
        memory.save()
    """
    
    CACHE_DIR = ".gade"
    CACHE_FILE = "difficulty.json"
    EMA_ALPHA = 0.3  # Weight for new values (0.3 = 30% new, 70% history)
    REGRESSION_THRESHOLD = 0.1  # 10% increase triggers regression
    
    def __init__(self, repo_path: Path, ema_alpha: float = 0.3):
        self.repo_path = Path(repo_path)
        self.cache_path = self.repo_path / self.CACHE_DIR / self.CACHE_FILE
        self.ema_alpha = ema_alpha
        self.scores: dict[str, RegionScore] = {}
        self._loaded = False
    
    @staticmethod
    def hash_region(file_path: str, node_name: str, node_type: str) -> str:
        """Create stable hash for a code region."""
        key = f"{file_path}::{node_type}::{node_name}"
        return hashlib.sha256(key.encode()).hexdigest()[:16]
    
    def load(self) -> bool:
        """Load difficulty scores from cache."""
        if not self.cache_path.exists():
            self._loaded = True
            return False
        
        try:
            with open(self.cache_path, 'r') as f:
                data = json.load(f)
            
            self.scores = {
                k: RegionScore(**v) for k, v in data.get("scores", {}).items()
            }
            self._loaded = True
            return True
        except (json.JSONDecodeError, KeyError, TypeError):
            self._loaded = True
            return False
    
    def save(self) -> None:
        """Save difficulty scores to cache."""
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "version": "1.0.0",
            "updated_at": datetime.now().isoformat(),
            "total_regions": len(self.scores),
            "scores": {k: asdict(v) for k, v in self.scores.items()}
        }
        
        with open(self.cache_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def update(
        self,
        file_path: str,
        node_name: str,
        node_type: str,
        new_score: float
    ) -> RegionScore:
        """
        Update difficulty score with EMA smoothing.
        
        Args:
            file_path: Path to the file
            node_name: Name of the function/class
            node_type: Type (file, function, class)
            new_score: New difficulty score (0-1)
        
        Returns:
            Updated RegionScore
        """
        region_hash = self.hash_region(file_path, node_name, node_type)
        
        if region_hash in self.scores:
            existing = self.scores[region_hash]
            # EMA: new_ema = alpha * new_value + (1 - alpha) * old_ema
            ema = self.ema_alpha * new_score + (1 - self.ema_alpha) * existing.ema_score
            
            updated = RegionScore(
                region_hash=region_hash,
                file_path=file_path,
                node_name=node_name,
                node_type=node_type,
                score=new_score,
                ema_score=round(ema, 4),
                last_updated=datetime.now().isoformat(),
                update_count=existing.update_count + 1
            )
        else:
            # First time seeing this region
            updated = RegionScore(
                region_hash=region_hash,
                file_path=file_path,
                node_name=node_name,
                node_type=node_type,
                score=new_score,
                ema_score=new_score,
                last_updated=datetime.now().isoformat(),
                update_count=1
            )
        
        self.scores[region_hash] = updated
        return updated
    
    def get_score(
        self,
        file_path: str,
        node_name: str,
        node_type: str
    ) -> Optional[RegionScore]:
        """Get stored score for a region."""
        region_hash = self.hash_region(file_path, node_name, node_type)
        return self.scores.get(region_hash)
    
    def detect_regression(
        self,
        file_path: str,
        node_name: str,
        node_type: str,
        new_score: float,
        threshold: float = None
    ) -> tuple[bool, float]:
        """
        Detect if difficulty has regressed (increased significantly).
        
        Args:
            file_path: Path to the file
            node_name: Name of the function/class
            node_type: Type (file, function, class)
            new_score: New difficulty score
            threshold: Regression threshold (default: 0.1)
        
        Returns:
            Tuple of (is_regression, delta)
        """
        threshold = threshold or self.REGRESSION_THRESHOLD
        existing = self.get_score(file_path, node_name, node_type)
        
        if not existing:
            return False, 0.0
        
        delta = new_score - existing.ema_score
        is_regression = delta > threshold
        
        return is_regression, round(delta, 4)
    
    def get_regressions(self, current_scores: dict[str, float]) -> list[dict]:
        """
        Find all regions that have regressed.
        
        Args:
            current_scores: Dict of region_hash -> new_score
        
        Returns:
            List of regression details
        """
        regressions = []
        
        for region_hash, new_score in current_scores.items():
            if region_hash in self.scores:
                existing = self.scores[region_hash]
                delta = new_score - existing.ema_score
                
                if delta > self.REGRESSION_THRESHOLD:
                    regressions.append({
                        "file": existing.file_path,
                        "name": existing.node_name,
                        "type": existing.node_type,
                        "previous": existing.ema_score,
                        "current": new_score,
                        "delta": round(delta, 4),
                    })
        
        return sorted(regressions, key=lambda x: x["delta"], reverse=True)
    
    def get_stats(self) -> dict:
        """Get memory statistics."""
        if not self.scores:
            return {"total_regions": 0}
        
        scores = [s.ema_score for s in self.scores.values()]
        return {
            "total_regions": len(self.scores),
            "avg_difficulty": round(sum(scores) / len(scores), 4),
            "max_difficulty": round(max(scores), 4),
            "min_difficulty": round(min(scores), 4),
        }
    
    def clear(self) -> None:
        """Clear all stored scores."""
        self.scores = {}
        if self.cache_path.exists():
            self.cache_path.unlink()
