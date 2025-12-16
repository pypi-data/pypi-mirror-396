"""Deep Research SDK - Conduct deep research using Gemini with search grounding."""

from .researcher import (
    research,
    DeepResearcher,
    ResearchResult,
    SearchQuery,
)

__all__ = [
    "research",
    "DeepResearcher",
    "ResearchResult",
    "SearchQuery",
]

__version__ = "0.1.0"
