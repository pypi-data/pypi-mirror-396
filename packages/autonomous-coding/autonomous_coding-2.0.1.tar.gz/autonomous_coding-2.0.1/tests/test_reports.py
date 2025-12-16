"""
Tests for Test Reports
======================

Tests for Phase 10 (T133-T139): Summary Reports
"""

import pytest

from core.orchestrator import atomic_write_json
from quality.qa_agent import QAAgent


class TestGenerateSummaryReport:
    """Tests for T133: Summary report generation."""

    @pytest.fixture
    def qa_agent(self, tmp_path):
        """Create QA agent with temporary directory."""
        return QAAgent(tmp_path)

    def test_generate_summary_no_features(self, qa_agent):
        """Test report generation with no feature_list.json."""
        result = qa_agent.generate_summary_report()

        assert "error" in result
        assert "feature_list.json not found" in result["error"]

    def test_generate_summary_basic(self, qa_agent, tmp_path):
        """Test basic summary report generation."""
        features = [
            {"id": 1, "description": "Feature 1", "passes": True, "qa_validated": True},
            {"id": 2, "description": "Feature 2", "passes": False, "qa_validated": True},
            {"id": 3, "description": "Feature 3", "passes": True, "qa_validated": False},
        ]
        atomic_write_json(tmp_path / "feature_list.json", features)

        result = qa_agent.generate_summary_report()

        assert result["features"]["total"] == 3
        assert result["features"]["passing"] == 2
        assert result["features"]["failing"] == 1
        assert result["features"]["qa_validated"] == 2

    def test_generate_summary_creates_files(self, qa_agent, tmp_path):
        """Test that report files are created."""
        features = [{"id": 1, "description": "Test", "passes": True}]
        atomic_write_json(tmp_path / "feature_list.json", features)

        qa_agent.generate_summary_report()

        reports_dir = tmp_path / "qa-reports"
        json_files = list(reports_dir.glob("summary-*.json"))
        md_files = list(reports_dir.glob("summary-*.md"))

        assert len(json_files) == 1
        assert len(md_files) == 1


class TestAggregateCategoryStats:
    """Tests for T134: Category statistics aggregation."""

    @pytest.fixture
    def qa_agent(self, tmp_path):
        """Create QA agent with temporary directory."""
        return QAAgent(tmp_path)

    def test_aggregate_no_reports(self, qa_agent):
        """Test aggregation when no reports exist."""
        features = [{"id": 1, "description": "Test", "passes": True}]

        stats = qa_agent._aggregate_category_stats(features)

        # All gates should have 0 counts
        for gate in ["lint", "type_check", "unit_tests", "browser_automation", "story_validation"]:
            assert stats[gate]["passed"] == 0
            assert stats[gate]["failed"] == 0

    def test_aggregate_with_reports(self, qa_agent, tmp_path):
        """Test aggregation with existing reports."""
        features = [{"id": 1, "description": "Test"}]
        atomic_write_json(tmp_path / "feature_list.json", features)

        # Create a report with mixed gate results
        reports_dir = tmp_path / "qa-reports"
        reports_dir.mkdir()
        report = {
            "feature_id": 1,
            "gates": {
                "lint": {"passed": True, "errors": []},
                "type_check": {"passed": False, "errors": [{"message": "error"}]},
                "unit_tests": {"passed": True, "errors": []},
                "browser_automation": {"passed": True, "errors": []},
                "story_validation": {"passed": False, "errors": [{"message": "fail"}]},
            },
        }
        atomic_write_json(reports_dir / "feature-1-2024-01-01.json", report)

        stats = qa_agent._aggregate_category_stats(features)

        assert stats["lint"]["passed"] == 1
        assert stats["type_check"]["failed"] == 1
        assert stats["type_check"]["total_errors"] == 1


class TestCalculateCoverageMetrics:
    """Tests for T135: Coverage metrics calculation."""

    @pytest.fixture
    def qa_agent(self, tmp_path):
        """Create QA agent with temporary directory."""
        return QAAgent(tmp_path)

    def test_coverage_empty_features(self, qa_agent):
        """Test coverage with no features."""
        coverage = qa_agent._calculate_coverage_metrics([])

        assert coverage["overall_pass_rate"] == 0.0
        assert coverage["validation_rate"] == 0.0

    def test_coverage_all_passing(self, qa_agent):
        """Test coverage when all features pass."""
        features = [
            {"id": 1, "passes": True, "qa_validated": True},
            {"id": 2, "passes": True, "qa_validated": True},
        ]

        coverage = qa_agent._calculate_coverage_metrics(features)

        assert coverage["overall_pass_rate"] == 100.0
        assert coverage["validation_rate"] == 100.0

    def test_coverage_mixed(self, qa_agent):
        """Test coverage with mixed results."""
        features = [
            {"id": 1, "passes": True, "qa_validated": True},
            {"id": 2, "passes": False, "qa_validated": True},
            {"id": 3, "passes": False, "qa_validated": False},
            {"id": 4, "passes": True, "qa_validated": False},
        ]

        coverage = qa_agent._calculate_coverage_metrics(features)

        assert coverage["overall_pass_rate"] == 50.0
        assert coverage["validation_rate"] == 50.0
        assert coverage["features_passing"] == 2
        assert coverage["features_validated"] == 2


class TestGetHistoricalTrends:
    """Tests for T136: Historical trend tracking."""

    @pytest.fixture
    def qa_agent(self, tmp_path):
        """Create QA agent with temporary directory."""
        return QAAgent(tmp_path)

    def test_trends_no_history(self, qa_agent):
        """Test trends when no history exists."""
        trends = qa_agent._get_historical_trends()

        assert trends["history"] == []
        assert trends["trend"] == "unknown"

    def test_trends_improving(self, qa_agent, tmp_path):
        """Test detecting improving trend."""
        reports_dir = tmp_path / "qa-reports"
        reports_dir.mkdir()

        # Create older report with lower pass rate
        import time

        older = {
            "timestamp": "2024-01-01T00:00:00Z",
            "coverage": {"overall_pass_rate": 50.0},
            "features": {"passing": 5, "total": 10},
        }
        atomic_write_json(reports_dir / "summary-2024-01-01.json", older)
        time.sleep(0.01)

        # Create newer report with higher pass rate
        newer = {
            "timestamp": "2024-01-02T00:00:00Z",
            "coverage": {"overall_pass_rate": 80.0},
            "features": {"passing": 8, "total": 10},
        }
        atomic_write_json(reports_dir / "summary-2024-01-02.json", newer)

        trends = qa_agent._get_historical_trends()

        assert len(trends["history"]) == 2
        assert trends["trend"] == "improving"

    def test_trends_declining(self, qa_agent, tmp_path):
        """Test detecting declining trend."""
        reports_dir = tmp_path / "qa-reports"
        reports_dir.mkdir()

        import time

        older = {
            "timestamp": "2024-01-01T00:00:00Z",
            "coverage": {"overall_pass_rate": 90.0},
            "features": {"passing": 9, "total": 10},
        }
        atomic_write_json(reports_dir / "summary-2024-01-01.json", older)
        time.sleep(0.01)

        newer = {
            "timestamp": "2024-01-02T00:00:00Z",
            "coverage": {"overall_pass_rate": 60.0},
            "features": {"passing": 6, "total": 10},
        }
        atomic_write_json(reports_dir / "summary-2024-01-02.json", newer)

        trends = qa_agent._get_historical_trends()

        assert trends["trend"] == "declining"


class TestGenerateMarkdownReport:
    """Tests for T137: Markdown report generation."""

    @pytest.fixture
    def qa_agent(self, tmp_path):
        """Create QA agent with temporary directory."""
        return QAAgent(tmp_path)

    def test_markdown_basic_structure(self, qa_agent):
        """Test Markdown report has basic structure."""
        summary = {
            "timestamp": "2024-01-01T00:00:00Z",
            "qa_agent_version": "1.0.0",
            "features": {"total": 5, "passing": 3, "failing": 2, "qa_validated": 4},
            "coverage": {"overall_pass_rate": 60.0, "validation_rate": 80.0},
            "category_stats": {},
            "trends": {},
            "feature_details": [],
        }

        markdown = qa_agent._generate_markdown_report(summary)

        assert "# QA Summary Report" in markdown
        assert "## Overview" in markdown
        assert "## Coverage Metrics" in markdown
        assert "60.0%" in markdown

    def test_markdown_feature_table(self, qa_agent):
        """Test Markdown report includes feature table."""
        summary = {
            "timestamp": "2024-01-01T00:00:00Z",
            "qa_agent_version": "1.0.0",
            "features": {"total": 1, "passing": 1, "failing": 0, "qa_validated": 1},
            "coverage": {"overall_pass_rate": 100.0},
            "category_stats": {},
            "trends": {},
            "feature_details": [
                {
                    "id": 1,
                    "description": "Test feature",
                    "passes": True,
                    "qa_validated": True,
                    "last_qa_run": "2024-01-01T00:00:00Z",
                }
            ],
        }

        markdown = qa_agent._generate_markdown_report(summary)

        assert "| ID | Description" in markdown
        assert "| 1 |" in markdown
        assert "PASS" in markdown


class TestAsciiVisualizations:
    """Tests for T138: ASCII visualizations."""

    @pytest.fixture
    def qa_agent(self, tmp_path):
        """Create QA agent with temporary directory."""
        return QAAgent(tmp_path)

    def test_progress_bar_full(self, qa_agent):
        """Test progress bar at 100%."""
        bar = qa_agent._generate_ascii_progress_bar(100.0)

        assert "100.0%" in bar
        assert "█" * 40 in bar
        assert "░" not in bar

    def test_progress_bar_empty(self, qa_agent):
        """Test progress bar at 0%."""
        bar = qa_agent._generate_ascii_progress_bar(0.0)

        assert "0.0%" in bar
        assert "░" * 40 in bar

    def test_progress_bar_partial(self, qa_agent):
        """Test progress bar at 50%."""
        bar = qa_agent._generate_ascii_progress_bar(50.0)

        assert "50.0%" in bar
        assert "█" in bar
        assert "░" in bar

    def test_trend_chart_empty(self, qa_agent):
        """Test trend chart with no data."""
        chart = qa_agent._generate_ascii_trend_chart([])

        assert "No historical data" in chart

    def test_trend_chart_with_data(self, qa_agent):
        """Test trend chart with data."""
        history = [
            {"pass_rate": 50},
            {"pass_rate": 60},
            {"pass_rate": 80},
        ]

        chart = qa_agent._generate_ascii_trend_chart(history)

        assert "%" in chart
        assert "█" in chart


class TestReportIntegration:
    """Integration tests for T139: Report generation with features."""

    @pytest.fixture
    def qa_agent(self, tmp_path):
        """Create QA agent with temporary directory."""
        return QAAgent(tmp_path)

    def test_report_with_multiple_features(self, qa_agent, tmp_path):
        """Test report generation with multiple features."""
        # Create features
        features = [
            {"id": i, "description": f"Feature {i}", "passes": i % 2 == 0, "qa_validated": True}
            for i in range(1, 11)
        ]
        atomic_write_json(tmp_path / "feature_list.json", features)

        # Create QA reports for each feature
        reports_dir = tmp_path / "qa-reports"
        reports_dir.mkdir()

        for feature in features:
            report = {
                "feature_id": feature["id"],
                "overall_status": "PASSED" if feature["passes"] else "FAILED",
                "gates": {
                    "lint": {"passed": feature["passes"], "errors": []},
                    "type_check": {"passed": True, "errors": []},
                    "unit_tests": {"passed": feature["passes"], "errors": []},
                    "browser_automation": {"passed": True, "errors": []},
                    "story_validation": {"passed": True, "errors": []},
                },
            }
            atomic_write_json(reports_dir / f"feature-{feature['id']}-2024-01-01.json", report)

        # Generate summary report
        result = qa_agent.generate_summary_report()

        # Verify summary
        assert result["features"]["total"] == 10
        assert result["features"]["passing"] == 5  # Even IDs pass
        assert result["coverage"]["overall_pass_rate"] == 50.0

        # Verify files created
        summary_json = list(reports_dir.glob("summary-*.json"))
        summary_md = list(reports_dir.glob("summary-*.md"))
        assert len(summary_json) >= 1
        assert len(summary_md) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
