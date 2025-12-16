"""Tests for DeepResearcher class."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from deep_research import DeepResearcher, SearchQuery


class TestDeepResearcherInit:
    def test_default_models(self):
        with patch("deep_research.researcher.genai.Client"):
            researcher = DeepResearcher()
            assert researcher.thinking_model == "gemini-2.5-pro"
            assert researcher.task_model == "gemini-2.5-flash"

    def test_custom_models(self):
        with patch("deep_research.researcher.genai.Client"):
            researcher = DeepResearcher(
                thinking_model="custom-thinking",
                task_model="custom-task",
            )
            assert researcher.thinking_model == "custom-thinking"
            assert researcher.task_model == "custom-task"

    def test_with_api_key(self):
        with patch("deep_research.researcher.genai.Client") as mock_client:
            DeepResearcher(api_key="test-key")
            mock_client.assert_called_once_with(api_key="test-key")

    def test_without_api_key(self):
        with patch("deep_research.researcher.genai.Client") as mock_client:
            DeepResearcher()
            mock_client.assert_called_once_with()


class TestDeepResearcherGenerate:
    @pytest.fixture
    def researcher(self):
        with patch("deep_research.researcher.genai.Client") as mock_client:
            mock_response = Mock()
            mock_response.text = "Generated text"
            mock_client.return_value.models.generate_content.return_value = mock_response
            r = DeepResearcher()
            yield r

    def test_generate_without_search(self, researcher):
        result = researcher._generate("test prompt", model="test-model")
        assert result == "Generated text"

    def test_generate_with_search(self, researcher):
        result = researcher._generate("test prompt", model="test-model", use_search=True)
        assert result == "Generated text"


class TestDeepResearcherWritePlan:
    def test_write_plan_calls_generate(self):
        with patch("deep_research.researcher.genai.Client"):
            researcher = DeepResearcher()
            researcher._generate = Mock(return_value="Test plan")

            result = researcher.write_plan("test query")

            assert result == "Test plan"
            researcher._generate.assert_called_once()
            call_args = researcher._generate.call_args
            assert "test query" in call_args[0][0]
            assert call_args[1]["model"] == "gemini-2.5-pro"


class TestDeepResearcherSearchAndLearn:
    def test_search_and_learn_uses_task_model(self):
        with patch("deep_research.researcher.genai.Client"):
            researcher = DeepResearcher()
            researcher._generate = Mock(return_value="Learnings")

            result = researcher.search_and_learn("query", "goal")

            assert result == "Learnings"
            call_args = researcher._generate.call_args
            assert call_args[1]["model"] == "gemini-2.5-flash"
            assert call_args[1]["use_search"] is True


class TestDeepResearcherWriteReport:
    def test_write_report_formats_learnings(self):
        with patch("deep_research.researcher.genai.Client"):
            researcher = DeepResearcher()
            researcher._generate = Mock(return_value="Final report")

            result = researcher.write_report("plan", ["learning1", "learning2"])

            assert result == "Final report"
            call_args = researcher._generate.call_args
            assert "<learning>" in call_args[0][0]
            assert "learning1" in call_args[0][0]
            assert "learning2" in call_args[0][0]


class TestDeepResearcherResearch:
    def test_full_research_flow(self):
        with patch("deep_research.researcher.genai.Client"):
            researcher = DeepResearcher()
            researcher.write_plan = Mock(return_value="Plan")
            researcher.generate_search_queries = Mock(return_value=[
                SearchQuery(query="q1", research_goal="g1"),
                SearchQuery(query="q2", research_goal="g2"),
            ])
            researcher.search_and_learn = Mock(side_effect=["L1", "L2"])
            researcher.write_report = Mock(return_value="Report")

            result = researcher.research("test query")

            assert result.query == "test query"
            assert result.plan == "Plan"
            assert result.learnings == ["L1", "L2"]
            assert result.report == "Report"

            researcher.write_plan.assert_called_once_with("test query")
            researcher.generate_search_queries.assert_called_once_with("Plan")
            assert researcher.search_and_learn.call_count == 2
            researcher.write_report.assert_called_once_with("Plan", ["L1", "L2"])
