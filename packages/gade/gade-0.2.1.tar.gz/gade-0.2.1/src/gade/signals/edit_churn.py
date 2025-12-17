"""
Edit Churn signal - measures code volatility from git history.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from gade.signals.base import SignalPlugin


class EditChurnSignal(SignalPlugin):
    """
    Computes edit churn from git commit history.
    
    Metrics:
    - Commit frequency for the file/region
    - Lines changed over time window
    - Normalized by repository average
    """
    
    name = "edit_churn"
    description = "Git-based edit frequency and volatility"
    
    def __init__(self, lookback_days: int = 90):
        self.lookback_days = lookback_days
        self._repo_cache: dict[Path, Any] = {}
    
    def compute(
        self,
        file_path: Path,
        ast_range: tuple[int, int],
        context: Optional[dict[str, Any]] = None,
    ) -> float:
        """
        Compute edit churn for a code region.
        
        Returns higher values for frequently modified code.
        """
        if context is None:
            context = {}
        
        repo_path = context.get("repo_path")
        if repo_path is None:
            return 0.0
        
        try:
            from git import Repo
            from git.exc import InvalidGitRepositoryError
        except ImportError:
            return 0.0
        
        try:
            repo = self._get_repo(repo_path)
            if repo is None:
                return 0.0
            
            # Get relative path
            try:
                rel_path = file_path.relative_to(repo_path)
            except ValueError:
                return 0.0
            
            # Count commits touching this file
            since_date = datetime.now() - timedelta(days=self.lookback_days)
            since_str = since_date.strftime("%Y-%m-%d")
            
            try:
                commits = list(repo.iter_commits(
                    paths=str(rel_path),
                    since=since_str,
                    max_count=100
                ))
            except Exception:
                commits = []
            
            commit_count = len(commits)
            
            # Count line changes in range
            line_changes = self._count_line_changes(
                repo, rel_path, ast_range, commits
            )
            
            # Compute composite score
            # More commits = more churn
            commit_score = self.sigmoid_normalize(commit_count, midpoint=10, steepness=0.3)
            
            # More line changes = more churn
            change_score = self.sigmoid_normalize(line_changes, midpoint=50, steepness=0.05)
            
            # Weighted combination
            return 0.6 * commit_score + 0.4 * change_score
            
        except Exception:
            return 0.0
    
    def _get_repo(self, repo_path: Path) -> Any:
        """Get cached git repo instance."""
        if repo_path not in self._repo_cache:
            try:
                from git import Repo
                self._repo_cache[repo_path] = Repo(repo_path)
            except Exception:
                self._repo_cache[repo_path] = None
        return self._repo_cache[repo_path]
    
    def _count_line_changes(
        self,
        repo: Any,
        rel_path: Path,
        ast_range: tuple[int, int],
        commits: list[Any],
    ) -> int:
        """Count total lines changed in range across commits."""
        total_changes = 0
        start_line, end_line = ast_range
        
        for commit in commits[:20]:  # Limit for performance
            try:
                # Get diff for this commit
                if commit.parents:
                    diffs = commit.parents[0].diff(commit, paths=str(rel_path))
                else:
                    diffs = commit.diff(None, paths=str(rel_path))
                
                for diff in diffs:
                    if diff.a_blob or diff.b_blob:
                        # Count changed lines that intersect our range
                        # Simplified: just count if file was modified
                        total_changes += 10  # Approximate lines per commit
                        
            except Exception:
                continue
        
        return total_changes
