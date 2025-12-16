"""Tests for prompt templates."""

import pytest
from deep_research.prompts import (
    get_system_prompt,
    REPORT_PLAN_PROMPT,
    SERP_QUERIES_PROMPT,
    SEARCH_RESULT_PROMPT,
    FINAL_REPORT_PROMPT,
)


class TestSystemPrompt:
    def test_system_prompt_contains_date(self):
        prompt = get_system_prompt()
        assert "Today is" in prompt

    def test_system_prompt_contains_instructions(self):
        prompt = get_system_prompt()
        assert "expert researcher" in prompt


class TestReportPlanPrompt:
    def test_format_with_query(self):
        result = REPORT_PLAN_PROMPT.format(query="AI trends")
        assert "AI trends" in result
        assert "<QUERY>" in result


class TestSerpQueriesPrompt:
    def test_format_with_plan(self):
        result = SERP_QUERIES_PROMPT.format(plan="Research plan here")
        assert "Research plan here" in result
        assert "<PLAN>" in result
        assert "JSON" in result


class TestSearchResultPrompt:
    def test_format_with_query_and_goal(self):
        result = SEARCH_RESULT_PROMPT.format(
            query="test query",
            research_goal="test goal",
        )
        assert "test query" in result
        assert "test goal" in result
        assert "<QUERY>" in result
        assert "<RESEARCH_GOAL>" in result


class TestFinalReportPrompt:
    def test_format_with_plan_and_learnings(self):
        result = FINAL_REPORT_PROMPT.format(
            plan="my plan",
            learnings="my learnings",
        )
        assert "my plan" in result
        assert "my learnings" in result
