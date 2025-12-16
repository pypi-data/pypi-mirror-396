"""
Tests for Regression Detection
==============================

Tests for Phase 9 (T126-T132): Regression Detection
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from core.orchestrator import atomic_write_json
from quality.qa_agent import QAAgent


class TestGetPassingFeatures:
    """Tests for T127: Query passing features."""

    @pytest.fixture
    def qa_agent(self, tmp_path):
        """Create QA agent with temporary directory."""
        return QAAgent(tmp_path)

    def test_get_passing_features_all_passing(self, qa_agent, tmp_path):
        """Test querying features when all are passing."""
        features = [
            {"id": 1, "description": "Feature 1", "passes": True},
            {"id": 2, "description": "Feature 2", "passes": True},
            {"id": 3, "description": "Feature 3", "passes": True},
        ]
        atomic_write_json(tmp_path / "feature_list.json", features)

        result = qa_agent.get_passing_features()

        assert len(result) == 3
        assert all(f["passes"] for f in result)

    def test_get_passing_features_mixed(self, qa_agent, tmp_path):
        """Test querying features with mixed status."""
        features = [
            {"id": 1, "description": "Feature 1", "passes": True},
            {"id": 2, "description": "Feature 2", "passes": False},
            {"id": 3, "description": "Feature 3", "passes": True},
        ]
        atomic_write_json(tmp_path / "feature_list.json", features)

        result = qa_agent.get_passing_features()

        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["id"] == 3

    def test_get_passing_features_none_passing(self, qa_agent, tmp_path):
        """Test querying features when none are passing."""
        features = [
            {"id": 1, "description": "Feature 1", "passes": False},
            {"id": 2, "description": "Feature 2", "passes": False},
        ]
        atomic_write_json(tmp_path / "feature_list.json", features)

        result = qa_agent.get_passing_features()

        assert len(result) == 0

    def test_get_passing_features_missing_file(self, qa_agent):
        """Test querying features when file doesn't exist."""
        result = qa_agent.get_passing_features()
        assert result == []

    def test_get_passing_features_missing_passes_field(self, qa_agent, tmp_path):
        """Test features without passes field are treated as failing."""
        features = [
            {"id": 1, "description": "Feature 1"},  # No passes field
            {"id": 2, "description": "Feature 2", "passes": True},
        ]
        atomic_write_json(tmp_path / "feature_list.json", features)

        result = qa_agent.get_passing_features()

        assert len(result) == 1
        assert result[0]["id"] == 2


class TestGetPreviousReport:
    """Tests for T129: Get previous QA report."""

    @pytest.fixture
    def qa_agent(self, tmp_path):
        """Create QA agent with temporary directory."""
        return QAAgent(tmp_path)

    def test_get_previous_report_exists(self, qa_agent, tmp_path):
        """Test getting previous report when it exists."""
        # Create qa-reports directory and a report
        reports_dir = tmp_path / "qa-reports"
        reports_dir.mkdir()

        report = {
            "feature_id": 1,
            "timestamp": "2024-01-01T00:00:00Z",
            "overall_status": "PASSED",
            "gates": {},
            "summary": {},
        }
        atomic_write_json(reports_dir / "feature-1-2024-01-01-00-00-00.json", report)

        result = qa_agent.get_previous_report(1)

        assert result is not None
        assert result["feature_id"] == 1
        assert result["overall_status"] == "PASSED"

    def test_get_previous_report_multiple(self, qa_agent, tmp_path):
        """Test getting most recent report when multiple exist."""
        reports_dir = tmp_path / "qa-reports"
        reports_dir.mkdir()

        # Create older report
        older = {
            "feature_id": 1,
            "timestamp": "2024-01-01T00:00:00Z",
            "overall_status": "FAILED",
        }
        atomic_write_json(reports_dir / "feature-1-2024-01-01-00-00-00.json", older)

        # Create newer report (with small delay to ensure different mtime)
        import time

        time.sleep(0.01)

        newer = {
            "feature_id": 1,
            "timestamp": "2024-01-02T00:00:00Z",
            "overall_status": "PASSED",
        }
        atomic_write_json(reports_dir / "feature-1-2024-01-02-00-00-00.json", newer)

        result = qa_agent.get_previous_report(1)

        assert result is not None
        assert result["overall_status"] == "PASSED"  # Should get newer

    def test_get_previous_report_not_found(self, qa_agent, tmp_path):
        """Test getting report when none exists for feature."""
        reports_dir = tmp_path / "qa-reports"
        reports_dir.mkdir()

        # Create report for different feature
        report = {"feature_id": 99, "overall_status": "PASSED"}
        atomic_write_json(reports_dir / "feature-99-2024-01-01.json", report)

        result = qa_agent.get_previous_report(1)

        assert result is None

    def test_get_previous_report_no_directory(self, qa_agent):
        """Test getting report when qa-reports doesn't exist."""
        result = qa_agent.get_previous_report(1)
        assert result is None


class TestDetectRegressions:
    """Tests for T129-T130: Regression detection."""

    @pytest.fixture
    def qa_agent(self, tmp_path):
        """Create QA agent with temporary directory."""
        return QAAgent(tmp_path)

    def test_detect_regression_found(self, qa_agent):
        """Test detecting a regression (was passing, now failing)."""
        previous = {
            "feature_id": 1,
            "overall_status": "PASSED",
            "timestamp": "2024-01-01T00:00:00Z",
            "gates": {
                "lint": {"passed": True},
                "type_check": {"passed": True},
            },
        }
        current = {
            "feature_id": 1,
            "overall_status": "FAILED",
            "timestamp": "2024-01-02T00:00:00Z",
            "gates": {
                "lint": {"passed": False, "errors": [{"message": "error"}]},
                "type_check": {"passed": True},
            },
        }

        result = qa_agent.detect_regressions(current, previous)

        assert result["is_regression"] is True
        assert len(result["new_failures"]) == 1
        assert result["new_failures"][0]["gate"] == "lint"
        assert result["reason"] == "Previously passing feature now fails"

    def test_detect_no_regression(self, qa_agent):
        """Test no regression when both passing."""
        previous = {
            "feature_id": 1,
            "overall_status": "PASSED",
            "timestamp": "2024-01-01T00:00:00Z",
            "gates": {
                "lint": {"passed": True},
            },
        }
        current = {
            "feature_id": 1,
            "overall_status": "PASSED",
            "timestamp": "2024-01-02T00:00:00Z",
            "gates": {
                "lint": {"passed": True},
            },
        }

        result = qa_agent.detect_regressions(current, previous)

        assert result["is_regression"] is False
        assert len(result["new_failures"]) == 0

    def test_detect_fixed_issues(self, qa_agent):
        """Test detecting fixed issues (was failing, now passing)."""
        previous = {
            "feature_id": 1,
            "overall_status": "FAILED",
            "timestamp": "2024-01-01T00:00:00Z",
            "gates": {
                "lint": {"passed": False},
                "type_check": {"passed": True},
            },
        }
        current = {
            "feature_id": 1,
            "overall_status": "PASSED",
            "timestamp": "2024-01-02T00:00:00Z",
            "gates": {
                "lint": {"passed": True},
                "type_check": {"passed": True},
            },
        }

        result = qa_agent.detect_regressions(current, previous)

        assert result["is_regression"] is False
        assert len(result["fixed_issues"]) == 1
        assert result["fixed_issues"][0]["gate"] == "lint"

    def test_detect_no_previous_report(self, qa_agent):
        """Test detection when no previous report exists."""
        current = {
            "feature_id": 1,
            "overall_status": "FAILED",
            "timestamp": "2024-01-02T00:00:00Z",
            "gates": {
                "lint": {"passed": False},
            },
        }

        result = qa_agent.detect_regressions(current, None)

        assert result["is_regression"] is False
        assert result["reason"] == "No previous report to compare"

    def test_detect_multiple_changes(self, qa_agent):
        """Test detecting multiple regressions and fixes."""
        previous = {
            "feature_id": 1,
            "overall_status": "PASSED",
            "timestamp": "2024-01-01T00:00:00Z",
            "gates": {
                "lint": {"passed": True},
                "type_check": {"passed": True},
                "unit_tests": {"passed": False},
            },
        }
        current = {
            "feature_id": 1,
            "overall_status": "FAILED",
            "timestamp": "2024-01-02T00:00:00Z",
            "gates": {
                "lint": {"passed": False, "errors": [{"message": "error"}]},
                "type_check": {"passed": False, "errors": [{"message": "type error"}]},
                "unit_tests": {"passed": True},  # Fixed!
            },
        }

        result = qa_agent.detect_regressions(current, previous)

        assert result["is_regression"] is True
        assert len(result["new_failures"]) == 2  # lint and type_check
        assert len(result["fixed_issues"]) == 1  # unit_tests


class TestGitBlame:
    """Tests for T131: Git blame integration."""

    @pytest.fixture
    def qa_agent(self, tmp_path):
        """Create QA agent with temporary directory."""
        return QAAgent(tmp_path)

    @patch("subprocess.run")
    def test_git_blame_success(self, mock_run, qa_agent):
        """Test successful git blame."""
        # Git blame --porcelain output format has 40-char commit hash
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="""abc12345678901234567890123456789012345678 1 1 1
author John Doe
author-mail <john@example.com>
author-time 1704067200
summary Fix bug in feature
filename test.py
\tprint("hello")
""",
        )

        result = qa_agent.run_git_blame("test.py", 1)

        assert result is not None
        assert result["commit"] == "abc12345"  # First 8 chars
        assert result["author"] == "John Doe"
        assert result["summary"] == "Fix bug in feature"

    @patch("subprocess.run")
    def test_git_blame_failure(self, mock_run, qa_agent):
        """Test git blame when command fails."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
        )

        result = qa_agent.run_git_blame("nonexistent.py", 1)

        assert result is None

    @patch("subprocess.run")
    def test_git_blame_timeout(self, mock_run, qa_agent):
        """Test git blame timeout handling."""
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired("git", 30)

        result = qa_agent.run_git_blame("test.py", 1)

        assert result is None


class TestRegressionSuite:
    """Tests for T126, T128: Regression suite execution."""

    @pytest.fixture
    def qa_agent(self, tmp_path):
        """Create QA agent with temporary directory."""
        return QAAgent(tmp_path)

    def test_run_regression_suite_no_passing_features(self, qa_agent, tmp_path):
        """Test regression suite with no passing features."""
        features = [
            {"id": 1, "description": "Feature 1", "passes": False},
        ]
        atomic_write_json(tmp_path / "feature_list.json", features)

        result = qa_agent.run_regression_suite()

        assert result["features_tested"] == 0
        assert result["regressions_found"] == 0
        assert result["features"] == []

    @patch.object(QAAgent, "run_quality_gates")
    def test_run_regression_suite_no_regressions(self, mock_run_gates, qa_agent, tmp_path):
        """Test regression suite when all features still pass."""
        # Setup passing feature
        features = [
            {"id": 1, "description": "Feature 1", "passes": True},
        ]
        atomic_write_json(tmp_path / "feature_list.json", features)

        # Mock quality gates to return passing result
        mock_run_gates.return_value = {
            "feature_id": 1,
            "overall_status": "PASSED",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "gates": {
                "lint": {"passed": True, "duration_seconds": 1, "errors": []},
                "type_check": {"passed": True, "duration_seconds": 1, "errors": []},
                "unit_tests": {"passed": True, "duration_seconds": 1, "errors": []},
                "browser_automation": {"passed": True, "duration_seconds": 1, "errors": []},
                "story_validation": {"passed": True, "duration_seconds": 1, "errors": []},
            },
            "summary": {
                "gates_passed": 5,
                "gates_failed": 0,
                "gates_total": 5,
                "total_duration_seconds": 5,
            },
            "priority_fixes": [],
        }

        result = qa_agent.run_regression_suite()

        assert result["features_tested"] == 1
        assert result["regressions_found"] == 0

    @patch.object(QAAgent, "run_quality_gates")
    @patch.object(QAAgent, "update_feature_status")
    def test_run_regression_suite_with_regression(
        self, mock_update, mock_run_gates, qa_agent, tmp_path
    ):
        """Test regression suite when a feature regresses."""
        # Create qa-reports directory
        reports_dir = tmp_path / "qa-reports"
        reports_dir.mkdir()

        # Setup passing feature
        features = [
            {"id": 1, "description": "Feature 1", "passes": True},
        ]
        atomic_write_json(tmp_path / "feature_list.json", features)

        # Create previous passing report
        previous = {
            "feature_id": 1,
            "overall_status": "PASSED",
            "timestamp": "2024-01-01T00:00:00Z",
            "gates": {
                "lint": {"passed": True},
            },
        }
        atomic_write_json(reports_dir / "feature-1-2024-01-01-00-00-00.json", previous)

        # Mock quality gates to return failing result
        mock_run_gates.return_value = {
            "feature_id": 1,
            "overall_status": "FAILED",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "gates": {
                "lint": {"passed": False, "duration_seconds": 1, "errors": [{"message": "error"}]},
                "type_check": {"passed": True, "duration_seconds": 1, "errors": []},
                "unit_tests": {"passed": True, "duration_seconds": 1, "errors": []},
                "browser_automation": {"passed": True, "duration_seconds": 1, "errors": []},
                "story_validation": {"passed": True, "duration_seconds": 1, "errors": []},
            },
            "summary": {
                "gates_passed": 4,
                "gates_failed": 1,
                "gates_total": 5,
                "total_duration_seconds": 5,
            },
            "priority_fixes": [{"message": "Fix lint"}],
        }

        result = qa_agent.run_regression_suite()

        assert result["features_tested"] == 1
        assert result["regressions_found"] == 1
        assert result["features"][0]["regression_analysis"]["is_regression"] is True

        # Verify feature status was updated
        mock_update.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
