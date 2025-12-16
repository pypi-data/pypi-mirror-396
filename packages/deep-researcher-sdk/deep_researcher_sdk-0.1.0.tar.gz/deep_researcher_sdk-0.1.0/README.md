# deep-research-sdk

A Python SDK for conducting deep research using Google's Gemini models with built-in search grounding. No external search APIs required.

## Installation

```bash
pip install deep-researcher-sdk
```

Or with uv:

```bash
uv add deep-researcher-sdk
```

## Quick Start

```python
from deep_research import research

result = research("What are the top trends in B2B SaaS marketing in 2025?")
print(result.report)
```

## Configuration

Set your Gemini API key as an environment variable:

```bash
export GEMINI_API_KEY="your-api-key"
```

Get a free API key from [Google AI Studio](https://aistudio.google.com/apikey).

## Usage

### Simple Usage

```python
from deep_research import research

result = research("Your research query here")

# Access the results
print(result.plan)       # Research plan
print(result.learnings)  # List of learnings from searches
print(result.report)     # Final synthesized report
```

### Save Output to Files

```python
from deep_research import research

result = research(
    "Your research query here",
    output_dir="./research_output"
)
# Saves: plan.md, learning_1.md, ..., learnings.md, report.md
```

### Custom Models

```python
from deep_research import research

result = research(
    "Your research query here",
    thinking_model="gemini-2.5-pro",  # For planning and synthesis
    task_model="gemini-2.5-flash",     # For search tasks
)
```

### Class-Based Usage

```python
from deep_research import DeepResearcher

researcher = DeepResearcher(
    thinking_model="gemini-2.5-pro",
    task_model="gemini-2.5-flash",
    api_key="your-api-key",  # Optional, defaults to GEMINI_API_KEY env var
)

# Run full research
result = researcher.research("Your query", output_dir="./output")

# Or run individual steps
plan = researcher.write_plan("Your query")
queries = researcher.generate_search_queries(plan)
learnings = [researcher.search_and_learn(q.query, q.research_goal) for q in queries]
report = researcher.write_report(plan, learnings)
```

## How It Works

The SDK orchestrates a multi-step research flow:

1. **Plan Generation** - Uses the thinking model to create a structured research plan
2. **Query Generation** - Generates 3-5 targeted search queries based on the plan
3. **Search & Learn** - Executes each query using Gemini's built-in search grounding, extracting key learnings
4. **Report Synthesis** - Combines all learnings into a comprehensive final report

## Dual Model Architecture

The SDK uses two models optimized for different tasks:

- **Thinking Model** (`gemini-2.5-pro`): Used for planning, query generation, and final report synthesis. Optimized for reasoning and complex synthesis.
- **Task Model** (`gemini-2.5-flash`): Used for search tasks with grounding enabled. Optimized for speed and web search integration.

## Output Structure

When using `output_dir`, the SDK saves:

```
output_dir/
├── plan.md           # Research plan
├── learning_1.md     # First search result
├── learning_2.md     # Second search result
├── ...
├── learnings.md      # All learnings combined
└── report.md         # Final synthesized report
```

## Adding to Letta Agents

### 1. Add dependency to your Letta Dockerfile

```dockerfile
FROM letta/letta:latest

RUN /app/.venv/bin/python3 -m pip install deep-researcher-sdk
```

Make sure `GEMINI_API_KEY` is set in your Letta environment.

### 2. Create a tool file (e.g., `deep_research_tool.py`)

```python
def deep_research(query: str) -> str:
    """
    Conduct deep research on a topic and return a comprehensive report.

    Use this tool when you need to research a topic thoroughly before
    making recommendations or answering complex questions. The query
    should be specific and well-defined.

    Args:
        query (str): The research topic or question to investigate

    Returns:
        str: A comprehensive markdown report with findings and sources
    """
    from deep_research import research
    result = research(query)
    return result.report
```

### 3. Register and attach to your agent

```python
from letta_client import Letta

client = Letta(base_url="http://localhost:8283")

# Create tool from file
tool = client.tools.create_from_file(filepath="deep_research_tool.py")

# Attach to agent
client.tools.attach_to_agent(agent_id="your-agent-id", tool_id=tool.id)
```

## Requirements

- Python 3.12+
- Google Gemini API key

## License

MIT
