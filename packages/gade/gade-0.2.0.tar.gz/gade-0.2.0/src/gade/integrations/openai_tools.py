"""
GADE OpenAI Function Calling / Tools Integration

Provides tool schemas for OpenAI's function calling API,
enabling GADE to be used with ChatGPT, Assistants API, or any
OpenAI-compatible endpoint.
"""

from __future__ import annotations

from typing import Any
from pathlib import Path

# Tool schemas for OpenAI function calling
GADE_TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "analyze_code_difficulty",
            "description": "Analyze difficulty of code across a repository or directory. Returns ranked list of hardest code regions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to the repository or directory to analyze"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of top difficult regions to return",
                        "default": 20
                    },
                    "include_patterns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Glob patterns for files to include (e.g., ['*.py', '*.js'])",
                        "default": ["*.py", "*.js", "*.ts", "*.go", "*.rs"]
                    }
                },
                "required": ["repo_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_difficulty_score",
            "description": "Get difficulty score for a specific file or code region",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file"
                    },
                    "start_line": {
                        "type": "integer",
                        "description": "Start line of region (optional, analyzes whole file if not provided)"
                    },
                    "end_line": {
                        "type": "integer",
                        "description": "End line of region (optional)"
                    }
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_hardest_regions",
            "description": "Get the N most difficult code regions from a previous analysis",
            "parameters": {
                "type": "object",
                "properties": {
                    "top_k": {
                        "type": "integer",
                        "description": "Number of regions to return",
                        "default": 10
                    },
                    "tier": {
                        "type": "string",
                        "enum": ["compress", "standard", "deep", "debate"],
                        "description": "Filter by difficulty tier (optional)"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_refactor_suggestions",
            "description": "Get AI-powered refactoring suggestions for a difficult code region",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file containing the region"
                    },
                    "function_name": {
                        "type": "string",
                        "description": "Name of the function/class to refactor (optional)"
                    },
                    "budget": {
                        "type": "integer",
                        "description": "Token budget for AI reasoning",
                        "default": 4000
                    }
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "show_difficulty_heatmap",
            "description": "Display a visual heatmap of code difficulty",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to the repository"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["text", "json", "html"],
                        "description": "Output format",
                        "default": "text"
                    }
                },
                "required": ["repo_path"]
            }
        }
    }
]


def execute_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """
    Execute a GADE tool by name.
    
    Args:
        tool_name: Name of the tool to execute
        arguments: Tool arguments
    
    Returns:
        Tool result as dictionary
    """
    from ..config import GADEConfig
    from ..analyzer import analyze_repository
    from ..models import AnalysisResult
    
    handlers = {
        "analyze_code_difficulty": _handle_analyze,
        "get_difficulty_score": _handle_get_score,
        "get_hardest_regions": _handle_get_hardest,
        "get_refactor_suggestions": _handle_refactor,
        "show_difficulty_heatmap": _handle_heatmap,
    }
    
    handler = handlers.get(tool_name)
    if not handler:
        return {"error": f"Unknown tool: {tool_name}"}
    
    try:
        return handler(arguments)
    except Exception as e:
        return {"error": str(e)}


# Cache for analysis results
_analysis_cache: dict[str, Any] = {}


def _handle_analyze(args: dict) -> dict:
    """Handle analyze_code_difficulty tool."""
    from ..config import GADEConfig
    from ..analyzer import analyze_repository
    
    repo_path = Path(args["repo_path"])
    top_k = args.get("top_k", 20)
    include = args.get("include_patterns", ["*.py", "*.js", "*.ts"])
    
    config = GADEConfig(include_patterns=include)
    result = analyze_repository(repo_path, config)
    
    # Cache for later use
    _analysis_cache[str(repo_path)] = result
    
    top_regions = [
        {
            "rank": i + 1,
            "name": n.node_name,
            "file": str(n.file_path),
            "score": round(n.difficulty_score, 3),
            "tier": n.difficulty_tier,
            "type": n.node_type,
        }
        for i, n in enumerate(result.get_top_k(top_k))
    ]
    
    return {
        "total_files": result.total_files,
        "total_functions": result.total_functions,
        "average_difficulty": round(result.average_difficulty, 3),
        "top_regions": top_regions,
    }


def _handle_get_score(args: dict) -> dict:
    """Handle get_difficulty_score tool."""
    from ..config import GADEConfig
    from ..analyzer import analyze_repository
    
    file_path = Path(args["file_path"])
    
    if not file_path.exists():
        return {"error": f"File not found: {file_path}"}
    
    config = GADEConfig()
    result = analyze_repository(file_path.parent, config)
    
    # Find the specific file
    for node in result.nodes:
        if node.file_path == file_path and node.node_type == "file":
            return {
                "file": str(file_path),
                "score": round(node.difficulty_score, 3),
                "tier": node.difficulty_tier,
                "signals": {
                    "edit_churn": round(node.signals.edit_churn, 3),
                    "error_density": round(node.signals.error_density, 3),
                    "semantic_complexity": round(node.signals.semantic_complexity, 3),
                    "uncertainty_proxy": round(node.signals.uncertainty_proxy, 3),
                    "gradient_proxy": round(node.signals.gradient_proxy, 3),
                }
            }
    
    return {"error": "File not found in analysis"}


def _handle_get_hardest(args: dict) -> dict:
    """Handle get_hardest_regions tool."""
    top_k = args.get("top_k", 10)
    tier_filter = args.get("tier")
    
    # Use cached result if available
    if not _analysis_cache:
        return {"error": "No analysis results. Run analyze_code_difficulty first."}
    
    result = list(_analysis_cache.values())[0]
    regions = result.get_top_k(top_k * 2)  # Get extra for filtering
    
    if tier_filter:
        regions = [r for r in regions if r.difficulty_tier == tier_filter]
    
    return {
        "regions": [
            {
                "name": n.node_name,
                "file": str(n.file_path),
                "score": round(n.difficulty_score, 3),
                "tier": n.difficulty_tier,
            }
            for n in regions[:top_k]
        ]
    }


def _handle_refactor(args: dict) -> dict:
    """Handle get_refactor_suggestions tool."""
    file_path = Path(args["file_path"])
    budget = args.get("budget", 4000)
    
    if not file_path.exists():
        return {"error": f"File not found: {file_path}"}
    
    # Return placeholder - actual LLM integration would go here
    return {
        "file": str(file_path),
        "budget": budget,
        "message": "Refactor suggestions require LLM API key. Set OPENAI_API_KEY or similar.",
    }


def _handle_heatmap(args: dict) -> dict:
    """Handle show_difficulty_heatmap tool."""
    from ..config import GADEConfig
    from ..analyzer import analyze_repository
    
    repo_path = Path(args["repo_path"])
    fmt = args.get("format", "json")
    
    config = GADEConfig()
    result = analyze_repository(repo_path, config)
    
    if fmt == "json":
        return {
            "heatmap": [
                {
                    "file": str(n.file_path.relative_to(repo_path)),
                    "score": round(n.difficulty_score, 3),
                    "tier": n.difficulty_tier,
                }
                for n in result.nodes
                if n.node_type == "file"
            ]
        }
    
    return {"format": fmt, "message": "Only JSON format supported via API"}
