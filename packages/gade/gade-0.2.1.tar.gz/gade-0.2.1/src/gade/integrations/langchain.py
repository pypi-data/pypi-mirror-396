"""
GADE LangChain Integration

Provides LangChain-compatible tools for GADE functionality.
Works with LangChain agents, chains, and the LangGraph framework.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Type

try:
    from langchain.tools import BaseTool
    from langchain.callbacks.manager import CallbackManagerForToolRun
    from pydantic import BaseModel, Field
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False
    BaseTool = object
    BaseModel = object
    CallbackManagerForToolRun = None


def _check_langchain():
    if not HAS_LANGCHAIN:
        raise ImportError(
            "LangChain is required for this integration. "
            "Install with: pip install langchain langchain-core"
        )


# Input schemas
if HAS_LANGCHAIN:
    class AnalyzeInput(BaseModel):
        """Input for analyze tool."""
        repo_path: str = Field(description="Path to the repository to analyze")
        top_k: int = Field(default=20, description="Number of top regions to return")


    class GetScoreInput(BaseModel):
        """Input for get_score tool."""
        file_path: str = Field(description="Path to the file")
        function_name: Optional[str] = Field(default=None, description="Specific function to score")


    class RefactorInput(BaseModel):
        """Input for refactor tool."""
        file_path: str = Field(description="Path to the file to refactor")
        budget: int = Field(default=4000, description="Token budget for AI reasoning")


class GADEAnalyzeTool(BaseTool if HAS_LANGCHAIN else object):
    """
    LangChain tool to analyze code difficulty in a repository.
    
    Returns a ranked list of the most difficult code regions.
    """
    
    name: str = "gade_analyze"
    description: str = (
        "Analyze code difficulty across a repository. "
        "Returns ranked list of hardest code regions with scores and tiers."
    )
    args_schema: Type[BaseModel] = AnalyzeInput if HAS_LANGCHAIN else None
    
    def _run(
        self,
        repo_path: str,
        top_k: int = 20,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Run the analysis."""
        _check_langchain()
        
        from ..config import GADEConfig
        from ..analyzer import analyze_repository
        import json
        
        path = Path(repo_path)
        if not path.exists():
            return f"Error: Path not found: {repo_path}"
        
        config = GADEConfig()
        result = analyze_repository(path, config)
        
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
        
        return json.dumps({
            "total_files": result.total_files,
            "total_functions": result.total_functions,
            "average_difficulty": round(result.average_difficulty, 3),
            "top_regions": top_regions
        }, indent=2)
    
    async def _arun(
        self,
        repo_path: str,
        top_k: int = 20,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Async run - delegates to sync for now."""
        return self._run(repo_path, top_k, run_manager)


class GADEGetScoreTool(BaseTool if HAS_LANGCHAIN else object):
    """
    LangChain tool to get difficulty score for a specific file.
    """
    
    name: str = "gade_get_score"
    description: str = (
        "Get the difficulty score for a specific file or function. "
        "Returns score (0-1), tier, and individual signal values."
    )
    args_schema: Type[BaseModel] = GetScoreInput if HAS_LANGCHAIN else None
    
    def _run(
        self,
        file_path: str,
        function_name: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Get difficulty score."""
        _check_langchain()
        
        from ..config import GADEConfig
        from ..analyzer import analyze_repository
        import json
        
        path = Path(file_path)
        if not path.exists():
            return f"Error: File not found: {file_path}"
        
        config = GADEConfig()
        result = analyze_repository(path.parent, config)
        
        for node in result.nodes:
            if function_name:
                if node.node_name == function_name:
                    return json.dumps({
                        "name": node.node_name,
                        "score": round(node.difficulty_score, 3),
                        "tier": node.difficulty_tier,
                        "type": node.node_type,
                    })
            else:
                if node.file_path == path and node.node_type == "file":
                    return json.dumps({
                        "file": str(path.name),
                        "score": round(node.difficulty_score, 3),
                        "tier": node.difficulty_tier,
                    })
        
        return "Error: Target not found in analysis"
    
    async def _arun(self, *args, **kwargs) -> str:
        return self._run(*args, **kwargs)


class GADERefactorTool(BaseTool if HAS_LANGCHAIN else object):
    """
    LangChain tool to get refactoring suggestions for difficult code.
    """
    
    name: str = "gade_refactor"
    description: str = (
        "Get AI-powered refactoring suggestions for difficult code. "
        "Uses difficulty-aware reasoning strategies."
    )
    args_schema: Type[BaseModel] = RefactorInput if HAS_LANGCHAIN else None
    
    def _run(
        self,
        file_path: str,
        budget: int = 4000,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Get refactor suggestions."""
        _check_langchain()
        
        path = Path(file_path)
        if not path.exists():
            return f"Error: File not found: {file_path}"
        
        # Would integrate with LLM client for actual suggestions
        return (
            f"To refactor {path.name}, set an LLM API key. "
            f"Budget: {budget} tokens."
        )
    
    async def _arun(self, *args, **kwargs) -> str:
        return self._run(*args, **kwargs)


def get_gade_tools() -> list:
    """
    Get all GADE LangChain tools.
    
    Returns:
        List of LangChain tool instances
    """
    _check_langchain()
    return [
        GADEAnalyzeTool(),
        GADEGetScoreTool(),
        GADERefactorTool(),
    ]


# For direct agent integration
def create_gade_agent(llm: Any):
    """
    Create a LangChain agent with GADE tools.
    
    Args:
        llm: LangChain LLM instance
    
    Returns:
        Agent executor
    """
    _check_langchain()
    
    from langchain.agents import AgentExecutor, create_tool_calling_agent
    from langchain_core.prompts import ChatPromptTemplate
    
    tools = get_gade_tools()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a code analysis assistant powered by GADE. "
            "You help developers identify difficult code regions and suggest improvements. "
            "Use the GADE tools to analyze repositories and provide insights."
        )),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)
