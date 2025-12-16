"""Tests for Pydantic models."""

import pytest
from deep_research import SearchQuery, ResearchResult


class TestSearchQuery:
    def test_valid_search_query(self):
        sq = SearchQuery(query="test query", research_goal="test goal")
        assert sq.query == "test query"
        assert sq.research_goal == "test goal"

    def test_search_query_required_fields(self):
        with pytest.raises(Exception):
            SearchQuery()

    def test_search_query_missing_goal(self):
        with pytest.raises(Exception):
            SearchQuery(query="test")


class TestResearchResult:
    def test_valid_research_result(self):
        result = ResearchResult(
            query="test query",
            plan="test plan",
            learnings=["learning 1", "learning 2"],
            report="test report",
        )
        assert result.query == "test query"
        assert result.plan == "test plan"
        assert len(result.learnings) == 2
        assert result.report == "test report"

    def test_research_result_empty_learnings(self):
        result = ResearchResult(
            query="test",
            plan="plan",
            learnings=[],
            report="report",
        )
        assert result.learnings == []

    def test_research_result_required_fields(self):
        with pytest.raises(Exception):
            ResearchResult()
