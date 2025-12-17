"""
GADE REST API Server

FastAPI-based REST API for programmatic access to GADE.

Usage:
    gade serve --port 8000
    
Or directly:
    uvicorn gade.api.server:app --reload
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, List
import json

try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    FastAPI = None
    BaseModel = object


def check_fastapi():
    if not HAS_FASTAPI:
        raise ImportError(
            "FastAPI is required. Install with: pip install gade[api]"
        )


# API Models
if HAS_FASTAPI:
    class AnalyzeRequest(BaseModel):
        """Request to analyze a repository."""
        repo_path: str = Field(..., description="Path to repository")
        top_k: int = Field(20, description="Number of top regions")
        include_patterns: List[str] = Field(
            default=["*.py", "*.js", "*.ts"],
            description="File patterns to include"
        )


    class DifficultyNode(BaseModel):
        """A code region with difficulty score."""
        rank: int
        name: str
        file: str
        score: float
        tier: str
        type: str


    class AnalyzeResponse(BaseModel):
        """Response from analysis."""
        total_files: int
        total_functions: int
        average_difficulty: float
        top_regions: List[DifficultyNode]


    class ScoreRequest(BaseModel):
        """Request to score a file."""
        file_path: str
        function_name: Optional[str] = None


    class ScoreResponse(BaseModel):
        """Response with difficulty score."""
        file: str
        name: Optional[str] = None
        score: float
        tier: str
        signals: dict


    class RefactorRequest(BaseModel):
        """Request for refactor suggestions."""
        file_path: str
        function_name: Optional[str] = None
        budget: int = 4000


    class HealthResponse(BaseModel):
        """Health check response."""
        status: str
        version: str


# Create app
app = FastAPI(
    title="GADE API",
    description="Gradient-Aware Development Environment - REST API",
    version="0.2.1",
    docs_url="/docs",
    redoc_url="/redoc",
) if HAS_FASTAPI else None


if HAS_FASTAPI:
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Analysis cache
    _cache: dict = {}

    @app.get("/", response_model=HealthResponse)
    async def health():
        """Health check endpoint."""
        from .. import __version__
        return HealthResponse(status="healthy", version=__version__)

    @app.post("/analyze", response_model=AnalyzeResponse)
    async def analyze(request: AnalyzeRequest):
        """
        Analyze code difficulty in a repository.
        
        Returns ranked list of most difficult code regions.
        """
        from ..config import GADEConfig
        from ..analyzer import analyze_repository
        
        repo_path = Path(request.repo_path)
        
        if not repo_path.exists():
            raise HTTPException(404, f"Path not found: {request.repo_path}")
        
        try:
            config = GADEConfig(include_patterns=request.include_patterns)
            result = analyze_repository(repo_path, config)
            _cache[str(repo_path)] = result
            
            top_regions = [
                DifficultyNode(
                    rank=i + 1,
                    name=n.node_name,
                    file=str(n.file_path.name),
                    score=round(n.difficulty_score, 3),
                    tier=n.difficulty_tier,
                    type=n.node_type,
                )
                for i, n in enumerate(result.get_top_k(request.top_k))
            ]
            
            return AnalyzeResponse(
                total_files=result.total_files,
                total_functions=result.total_functions,
                average_difficulty=round(result.average_difficulty, 3),
                top_regions=top_regions,
            )
            
        except Exception as e:
            raise HTTPException(500, str(e))

    @app.post("/score", response_model=ScoreResponse)
    async def get_score(request: ScoreRequest):
        """Get difficulty score for a specific file or function."""
        from ..config import GADEConfig
        from ..analyzer import analyze_repository
        
        file_path = Path(request.file_path)
        
        if not file_path.exists():
            raise HTTPException(404, f"File not found: {request.file_path}")
        
        try:
            config = GADEConfig()
            result = analyze_repository(file_path.parent, config)
            
            for node in result.nodes:
                if request.function_name:
                    if node.node_name == request.function_name:
                        return ScoreResponse(
                            file=str(file_path.name),
                            name=node.node_name,
                            score=round(node.difficulty_score, 3),
                            tier=node.difficulty_tier,
                            signals={
                                "edit_churn": round(node.signals.edit_churn, 3),
                                "error_density": round(node.signals.error_density, 3),
                                "semantic_complexity": round(node.signals.semantic_complexity, 3),
                                "uncertainty_proxy": round(node.signals.uncertainty_proxy, 3),
                                "gradient_proxy": round(node.signals.gradient_proxy, 3),
                            }
                        )
                else:
                    if node.file_path == file_path and node.node_type == "file":
                        return ScoreResponse(
                            file=str(file_path.name),
                            score=round(node.difficulty_score, 3),
                            tier=node.difficulty_tier,
                            signals={
                                "edit_churn": round(node.signals.edit_churn, 3),
                                "error_density": round(node.signals.error_density, 3),
                                "semantic_complexity": round(node.signals.semantic_complexity, 3),
                                "uncertainty_proxy": round(node.signals.uncertainty_proxy, 3),
                                "gradient_proxy": round(node.signals.gradient_proxy, 3),
                            }
                        )
            
            raise HTTPException(404, "Target not found in analysis")
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(500, str(e))

    @app.get("/regions")
    async def get_regions(
        top_k: int = Query(10, description="Number of regions"),
        tier: Optional[str] = Query(None, description="Filter by tier")
    ):
        """Get hardest regions from cached analysis."""
        if not _cache:
            raise HTTPException(400, "No analysis cached. Call /analyze first.")
        
        result = list(_cache.values())[0]
        regions = result.get_top_k(top_k * 2)
        
        if tier:
            regions = [r for r in regions if r.difficulty_tier == tier]
        
        return {
            "regions": [
                {
                    "name": n.node_name,
                    "file": str(n.file_path.name),
                    "score": round(n.difficulty_score, 3),
                    "tier": n.difficulty_tier,
                }
                for n in regions[:top_k]
            ]
        }

    @app.post("/refactor")
    async def refactor(request: RefactorRequest):
        """Get refactoring suggestions for a code region."""
        file_path = Path(request.file_path)
        
        if not file_path.exists():
            raise HTTPException(404, f"File not found: {request.file_path}")
        
        # Placeholder - would integrate with LLM
        return {
            "file": str(file_path.name),
            "function": request.function_name,
            "budget": request.budget,
            "message": "Refactor suggestions require LLM API key."
        }

    @app.get("/config")
    async def get_config():
        """Get current GADE configuration."""
        from ..config import GADEConfig
        config = GADEConfig()
        return config.model_dump()


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the API server."""
    check_fastapi()
    import os
    import uvicorn
    # Railway sets PORT env variable
    port = int(os.environ.get("PORT", port))
    print(f"Starting GADE API server on {host}:{port}")
    print(f"Docs: http://{host}:{port}/docs")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()

