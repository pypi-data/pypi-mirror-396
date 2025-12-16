"""Core research logic using Gemini with search grounding."""

import json
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field

from google import genai
from google.genai import types

from .prompts import (
    get_system_prompt,
    REPORT_PLAN_PROMPT,
    SERP_QUERIES_PROMPT,
    SEARCH_RESULT_PROMPT,
    FINAL_REPORT_PROMPT,
)


class SearchQuery(BaseModel):
    """A search query with its research goal."""
    query: str = Field(description="The search query string")
    research_goal: str = Field(description="The goal of this query")


class ResearchResult(BaseModel):
    """The result of a deep research session."""
    query: str
    plan: str
    learnings: list[str]
    report: str


class DeepResearcher:
    """Conducts deep research using Gemini with search grounding."""

    def __init__(
        self,
        thinking_model: str = "gemini-2.5-pro",
        task_model: str = "gemini-2.5-flash",
        api_key: Optional[str] = None,
    ):
        """Initialize the researcher.

        Args:
            thinking_model: Model for planning and synthesis. Default is gemini-2.5-pro.
            task_model: Model for search tasks with grounding. Default is gemini-2.5-flash.
            api_key: Optional API key. If not provided, uses GEMINI_API_KEY env var.
        """
        self.thinking_model = thinking_model
        self.task_model = task_model
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = genai.Client()

    def _generate(self, prompt: str, model: str, use_search: bool = False) -> str:
        """Generate content with optional search grounding.

        Args:
            prompt: The prompt to send to the model.
            model: The model to use.
            use_search: Whether to enable Google Search grounding.

        Returns:
            The generated text response.
        """
        config = types.GenerateContentConfig(
            system_instruction=get_system_prompt(),
        )

        if use_search:
            config.tools = [types.Tool(google_search=types.GoogleSearch())]

        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
            config=config,
        )
        return response.text

    def _generate_search_queries(self, prompt: str, model: str) -> list[SearchQuery]:
        """Generate search queries as structured JSON output.

        Args:
            prompt: The prompt to send to the model.
            model: The model to use.

        Returns:
            List of SearchQuery objects.
        """
        config = types.GenerateContentConfig(
            system_instruction=get_system_prompt(),
            response_mime_type="application/json",
            response_schema=list[SearchQuery],
        )

        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
            config=config,
        )

        data = json.loads(response.text)
        return [SearchQuery(**item) for item in data]

    def write_plan(self, query: str) -> str:
        """Generate a research plan for the query.

        Args:
            query: The research topic/question.

        Returns:
            The research plan as markdown text.
        """
        prompt = REPORT_PLAN_PROMPT.format(query=query)
        return self._generate(prompt, model=self.thinking_model)

    def generate_search_queries(self, plan: str) -> list[SearchQuery]:
        """Generate search queries based on the research plan.

        Args:
            plan: The research plan.

        Returns:
            List of search queries with research goals.
        """
        prompt = SERP_QUERIES_PROMPT.format(plan=plan)
        return self._generate_search_queries(prompt, model=self.thinking_model)

    def search_and_learn(self, query: str, research_goal: str) -> str:
        """Execute a search and extract learnings.

        Args:
            query: The search query.
            research_goal: What we're trying to learn.

        Returns:
            The learnings extracted from search results.
        """
        prompt = SEARCH_RESULT_PROMPT.format(
            query=query,
            research_goal=research_goal,
        )
        return self._generate(prompt, model=self.task_model, use_search=True)

    def write_report(self, plan: str, learnings: list[str]) -> str:
        """Write the final research report.

        Args:
            plan: The research plan.
            learnings: All learnings from the search phase.

        Returns:
            The final report as markdown.
        """
        learnings_text = "\n\n".join(
            f"<learning>\n{learning}\n</learning>"
            for learning in learnings
        )
        prompt = FINAL_REPORT_PROMPT.format(
            plan=plan,
            learnings=learnings_text,
        )
        return self._generate(prompt, model=self.thinking_model)

    def research(
        self,
        query: str,
        output_dir: Optional[str] = None,
    ) -> ResearchResult:
        """Conduct deep research on a topic.

        This is the main entry point that orchestrates the full research flow:
        1. Generate a research plan
        2. Create search queries
        3. Execute searches and extract learnings
        4. Synthesize into a final report

        Args:
            query: The research topic or question.
            output_dir: Optional directory to save intermediate and final outputs.
                        If provided, saves plan.md, learnings.md, and report.md.

        Returns:
            ResearchResult containing the plan, learnings, and final report.
        """
        # Setup output directory if specified
        out_path = None
        if output_dir:
            out_path = Path(output_dir)
            out_path.mkdir(parents=True, exist_ok=True)

        # Step 1: Generate research plan
        plan = self.write_plan(query)
        if out_path:
            (out_path / "plan.md").write_text(plan)

        # Step 2: Generate search queries
        search_queries = self.generate_search_queries(plan)

        # Step 3: Execute searches and collect learnings
        learnings = []
        for i, sq in enumerate(search_queries, 1):
            learning = self.search_and_learn(sq.query, sq.research_goal)
            learnings.append(learning)
            if out_path:
                (out_path / f"learning_{i}.md").write_text(
                    f"# {sq.query}\n\n**Goal:** {sq.research_goal}\n\n---\n\n{learning}"
                )

        # Save combined learnings
        if out_path:
            all_learnings = "\n\n---\n\n".join(
                f"## {sq.query}\n\n{learning}"
                for sq, learning in zip(search_queries, learnings)
            )
            (out_path / "learnings.md").write_text(all_learnings)

        # Step 4: Write final report
        report = self.write_report(plan, learnings)
        if out_path:
            (out_path / "report.md").write_text(report)

        return ResearchResult(
            query=query,
            plan=plan,
            learnings=learnings,
            report=report,
        )


def research(
    query: str,
    thinking_model: str = "gemini-2.5-pro",
    task_model: str = "gemini-2.5-flash",
    api_key: Optional[str] = None,
    output_dir: Optional[str] = None,
) -> ResearchResult:
    """Conduct deep research on a topic.

    This is the convenience function for quick usage.

    Args:
        query: The research topic or question.
        thinking_model: Model for planning and synthesis. Default is gemini-2.5-pro.
        task_model: Model for search tasks with grounding. Default is gemini-2.5-flash.
        api_key: Optional API key. If not provided, uses GEMINI_API_KEY env var.
        output_dir: Optional directory to save intermediate and final outputs.

    Returns:
        ResearchResult containing the plan, learnings, and final report.

    Example:
        >>> from deep_research import research
        >>> result = research("What are the latest trends in B2B SaaS marketing?", output_dir="./output")
        >>> print(result.report)
    """
    researcher = DeepResearcher(
        thinking_model=thinking_model,
        task_model=task_model,
        api_key=api_key,
    )
    return researcher.research(query, output_dir=output_dir)
