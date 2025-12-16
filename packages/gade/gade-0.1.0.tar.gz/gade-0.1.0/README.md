# GADE - Gradient-Aware Development Environment

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

**Allocate AI compute dynamically based on code difficulty.**

GADE measures difficulty across your codebase and focuses 80% of tokens on the 20% hardest regions.

## Quick Start

```bash
pip install gade

# Analyze a repository
gade analyze ./my-project --top 20

# View heatmap
gade heatmap ./my-project

# Start API server
gade serve --port 8000
```

## Features

- **5 Difficulty Signals**: Edit churn, complexity, errors, uncertainty, gradient
- **80/20 Allocation**: Smart token distribution by difficulty
- **Multi-LLM Support**: OpenAI, Anthropic, Google, Ollama, Azure, Bedrock
- **Agentic AI Ready**: MCP server, OpenAI tools, LangChain integration
- **REST API**: FastAPI endpoints at `/analyze`, `/score`, `/regions`

## Installation

```bash
# Core
pip install gade

# With all integrations
pip install gade[all]

# Specific features
pip install gade[llm]        # LLM support
pip install gade[api]        # REST API
pip install gade[mcp]        # Claude Desktop
pip install gade[langchain]  # LangChain tools
```

## Python SDK

```python
from gade import analyze, get_difficulty

result = analyze("./my-project")
for node in result.get_top_k(10):
    print(f"{node.name}: {node.difficulty_score:.2f}")
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `gade analyze <path>` | Rank code by difficulty |
| `gade heatmap <path>` | Terminal visualization |
| `gade refactor <path>` | AI-assisted refactoring |
| `gade serve` | Start REST API |
| `gade serve-mcp` | Start MCP server |

## Difficulty Tiers

| Score | Tier | AI Strategy |
|-------|------|-------------|
| < 0.2 | compress | Summarize |
| 0.2-0.5 | standard | Single-pass |
| 0.5-0.8 | deep | Multi-step + tools |
| ≥ 0.8 | debate | Multi-pass synthesis |

## License

MIT
