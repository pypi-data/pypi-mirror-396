"""
GADE MCP (Model Context Protocol) Server

Exposes GADE as MCP tools and resources for integration with
Claude Desktop, Cursor, and other MCP-compatible AI assistants.

Usage:
    python -m gade.mcp.server
    
Or via CLI:
    gade serve-mcp
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Tool,
        TextContent,
        Resource,
        ResourceContents,
    )
    HAS_MCP = True
except ImportError:
    HAS_MCP = False


# Server instance
app = Server("gade") if HAS_MCP else None

# Cache for analysis results
_analysis_cache: dict[str, Any] = {}


def check_mcp():
    """Check if MCP is available."""
    if not HAS_MCP:
        raise ImportError(
            "MCP is required. Install with: pip install mcp"
        )


if HAS_MCP:
    @app.list_tools()
    async def list_tools() -> list[Tool]:
        """List available GADE tools."""
        return [
            Tool(
                name="analyze_repository",
                description="Analyze code difficulty across a repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_path": {
                            "type": "string",
                            "description": "Path to repository"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of top regions",
                            "default": 20
                        }
                    },
                    "required": ["repo_path"]
                }
            ),
            Tool(
                name="get_difficulty_score",
                description="Get difficulty score for a file or region",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string"},
                        "start_line": {"type": "integer"},
                        "end_line": {"type": "integer"}
                    },
                    "required": ["file_path"]
                }
            ),
            Tool(
                name="get_hardest_regions",
                description="Get the N most difficult code regions",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "top_k": {"type": "integer", "default": 10}
                    }
                }
            ),
            Tool(
                name="suggest_refactor",
                description="Get refactoring suggestions for difficult code",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string"},
                        "function_name": {"type": "string"},
                        "budget": {"type": "integer", "default": 4000}
                    },
                    "required": ["file_path"]
                }
            ),
        ]

    @app.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        """Execute a GADE tool."""
        from ..config import GADEConfig
        from ..analyzer import analyze_repository
        
        try:
            if name == "analyze_repository":
                repo_path = Path(arguments["repo_path"])
                top_k = arguments.get("top_k", 20)
                
                config = GADEConfig()
                result = analyze_repository(repo_path, config)
                _analysis_cache[str(repo_path)] = result
                
                top_regions = [
                    {
                        "rank": i + 1,
                        "name": n.node_name,
                        "file": str(n.file_path.name),
                        "score": round(n.difficulty_score, 3),
                        "tier": n.difficulty_tier,
                    }
                    for i, n in enumerate(result.get_top_k(top_k))
                ]
                
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "total_files": result.total_files,
                        "total_functions": result.total_functions,
                        "average_difficulty": round(result.average_difficulty, 3),
                        "top_regions": top_regions
                    }, indent=2)
                )]
            
            elif name == "get_difficulty_score":
                file_path = Path(arguments["file_path"])
                
                config = GADEConfig()
                result = analyze_repository(file_path.parent, config)
                
                for node in result.nodes:
                    if node.file_path == file_path and node.node_type == "file":
                        return [TextContent(
                            type="text",
                            text=json.dumps({
                                "file": str(file_path.name),
                                "score": round(node.difficulty_score, 3),
                                "tier": node.difficulty_tier,
                                "signals": {
                                    "edit_churn": round(node.signals.edit_churn, 3),
                                    "complexity": round(node.signals.semantic_complexity, 3),
                                    "errors": round(node.signals.error_density, 3),
                                    "uncertainty": round(node.signals.uncertainty_proxy, 3),
                                    "gradient": round(node.signals.gradient_proxy, 3),
                                }
                            }, indent=2)
                        )]
                
                return [TextContent(type="text", text="File not found in analysis")]
            
            elif name == "get_hardest_regions":
                if not _analysis_cache:
                    return [TextContent(
                        type="text",
                        text="No analysis cached. Run analyze_repository first."
                    )]
                
                top_k = arguments.get("top_k", 10)
                result = list(_analysis_cache.values())[0]
                
                regions = [
                    {
                        "name": n.node_name,
                        "file": str(n.file_path.name),
                        "score": round(n.difficulty_score, 3),
                        "tier": n.difficulty_tier,
                    }
                    for n in result.get_top_k(top_k)
                ]
                
                return [TextContent(
                    type="text",
                    text=json.dumps({"regions": regions}, indent=2)
                )]
            
            elif name == "suggest_refactor":
                file_path = arguments["file_path"]
                budget = arguments.get("budget", 4000)
                
                return [TextContent(
                    type="text",
                    text=f"Refactor suggestions for {file_path} (budget: {budget} tokens). Requires LLM API key."
                )]
            
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
                
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    @app.list_resources()
    async def list_resources() -> list[Resource]:
        """List available GADE resources."""
        return [
            Resource(
                uri="gade://difficulty-map",
                name="Difficulty Map",
                description="Full difficulty map from last analysis",
                mimeType="application/json"
            ),
            Resource(
                uri="gade://config",
                name="GADE Configuration",
                description="Current GADE configuration",
                mimeType="application/json"
            ),
        ]

    @app.read_resource()
    async def read_resource(uri: str) -> ResourceContents:
        """Read a GADE resource."""
        from ..config import GADEConfig
        
        if uri == "gade://difficulty-map":
            if not _analysis_cache:
                content = {"error": "No analysis cached"}
            else:
                result = list(_analysis_cache.values())[0]
                content = {
                    "total_files": result.total_files,
                    "total_functions": result.total_functions,
                    "nodes": [
                        {
                            "id": n.id,
                            "name": n.node_name,
                            "file": str(n.file_path),
                            "score": round(n.difficulty_score, 3),
                            "tier": n.difficulty_tier,
                        }
                        for n in result.nodes[:100]  # Limit for readability
                    ]
                }
            
            return ResourceContents(
                uri=uri,
                mimeType="application/json",
                text=json.dumps(content, indent=2)
            )
        
        elif uri == "gade://config":
            config = GADEConfig()
            return ResourceContents(
                uri=uri,
                mimeType="application/json",
                text=json.dumps(config.model_dump(), indent=2, default=str)
            )
        
        raise ValueError(f"Unknown resource: {uri}")


async def run_server():
    """Run the MCP server."""
    check_mcp()
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def main():
    """Entry point for MCP server."""
    import asyncio
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
