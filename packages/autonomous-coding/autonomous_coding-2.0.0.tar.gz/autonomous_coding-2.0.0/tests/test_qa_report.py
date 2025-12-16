"""
Tests for QA Report Generation
==============================

Tests for T062: Report generation with mixed failures
Tests for T063: Dev Agent can read and parse qa-report.json
"""

import json
import tempfile
from pathlib import Path

import pytest

from quality.qa_agent import QAAgent, validate_qa_report


class TestQAReportValidation:
    """Tests for QA report schema validation."""

    def test_valid_passing_report(self):
        """Test that a valid passing report passes validation."""
        report = {
            "feature_id": 1,
            "timestamp": "2025-12-09T10:00:00Z",
            "overall_status": "PASSED",
            "gates": {
                "lint": {"passed": True, "duration_seconds": 1.0, "errors": []},
                "type_check": {"passed": True, "duration_seconds": 2.0, "errors": []},
                "unit_tests": {"passed": True, "duration_seconds": 3.0, "errors": []},
                "browser_automation": {"passed": True, "duration_seconds": 4.0, "errors": []},
                "story_validation": {"passed": True, "duration_seconds": 5.0, "errors": []},
            },
            "summary": {
                "gates_passed": 5,
                "gates_failed": 0,
                "gates_total": 5,
                "total_duration_seconds": 15.0,
            },
            "priority_fixes": [],
        }
        assert validate_qa_report(report) is True

    def test_valid_failing_report(self):
        """Test that a valid failing report passes validation."""
        report = {
            "feature_id": 2,
            "timestamp": "2025-12-09T10:00:00Z",
            "overall_status": "FAILED",
            "gates": {
                "lint": {
                    "passed": False,
                    "duration_seconds": 1.0,
                    "errors": [{"file": "test.py", "line": 10, "message": "syntax error"}],
                },
                "type_check": {"passed": True, "duration_seconds": 2.0, "errors": []},
                "unit_tests": {"passed": True, "duration_seconds": 3.0, "errors": []},
                "browser_automation": {"passed": True, "duration_seconds": 4.0, "errors": []},
                "story_validation": {"passed": True, "duration_seconds": 5.0, "errors": []},
            },
            "summary": {
                "gates_passed": 4,
                "gates_failed": 1,
                "gates_total": 5,
                "total_duration_seconds": 15.0,
            },
            "priority_fixes": [{"priority": 1, "gate": "lint", "message": "Fix lint error"}],
        }
        assert validate_qa_report(report) is True

    def test_missing_required_field(self):
        """Test that missing required fields raise ValueError."""
        report = {
            "feature_id": 1,
            # Missing timestamp, overall_status, gates, summary
        }
        with pytest.raises(ValueError, match="Missing required fields"):
            validate_qa_report(report)

    def test_invalid_overall_status(self):
        """Test that invalid overall_status raises ValueError."""
        report = {
            "feature_id": 1,
            "timestamp": "2025-12-09T10:00:00Z",
            "overall_status": "INVALID",
            "gates": {},
            "summary": {},
        }
        with pytest.raises(ValueError, match="Invalid overall_status"):
            validate_qa_report(report)

    def test_missing_gate(self):
        """Test that missing gate raises ValueError."""
        report = {
            "feature_id": 1,
            "timestamp": "2025-12-09T10:00:00Z",
            "overall_status": "PASSED",
            "gates": {
                "lint": {"passed": True, "duration_seconds": 1.0},
                # Missing other gates
            },
            "summary": {"gates_passed": 1, "gates_failed": 0, "gates_total": 1},
        }
        with pytest.raises(ValueError, match="Missing required gates"):
            validate_qa_report(report)

    def test_inconsistent_status(self):
        """Test that PASSED status with failing gates raises ValueError."""
        report = {
            "feature_id": 1,
            "timestamp": "2025-12-09T10:00:00Z",
            "overall_status": "PASSED",
            "gates": {
                "lint": {"passed": False, "duration_seconds": 1.0},  # Failing gate
                "type_check": {"passed": True, "duration_seconds": 2.0},
                "unit_tests": {"passed": True, "duration_seconds": 3.0},
                "browser_automation": {"passed": True, "duration_seconds": 4.0},
                "story_validation": {"passed": True, "duration_seconds": 5.0},
            },
            "summary": {"gates_passed": 4, "gates_failed": 1, "gates_total": 5},
        }
        with pytest.raises(ValueError, match="PASSED but not all gates passed"):
            validate_qa_report(report)

    def test_failed_without_priority_fixes(self):
        """Test that FAILED status without priority_fixes raises ValueError."""
        report = {
            "feature_id": 1,
            "timestamp": "2025-12-09T10:00:00Z",
            "overall_status": "FAILED",
            "gates": {
                "lint": {"passed": False, "duration_seconds": 1.0, "errors": []},
                "type_check": {"passed": True, "duration_seconds": 2.0, "errors": []},
                "unit_tests": {"passed": True, "duration_seconds": 3.0, "errors": []},
                "browser_automation": {"passed": True, "duration_seconds": 4.0, "errors": []},
                "story_validation": {"passed": True, "duration_seconds": 5.0, "errors": []},
            },
            "summary": {
                "gates_passed": 4,
                "gates_failed": 1,
                "gates_total": 5,
                "total_duration_seconds": 15.0,
            },
            "priority_fixes": [],  # Empty!
        }
        with pytest.raises(ValueError, match="priority_fixes must be non-empty"):
            validate_qa_report(report)

    def test_summary_consistency(self):
        """Test that summary gate counts are consistent."""
        report = {
            "feature_id": 1,
            "timestamp": "2025-12-09T10:00:00Z",
            "overall_status": "PASSED",
            "gates": {
                "lint": {"passed": True, "duration_seconds": 1.0},
                "type_check": {"passed": True, "duration_seconds": 2.0},
                "unit_tests": {"passed": True, "duration_seconds": 3.0},
                "browser_automation": {"passed": True, "duration_seconds": 4.0},
                "story_validation": {"passed": True, "duration_seconds": 5.0},
            },
            "summary": {
                "gates_passed": 3,  # Wrong!
                "gates_failed": 1,  # Wrong!
                "gates_total": 5,
                "total_duration_seconds": 15.0,
            },
        }
        with pytest.raises(ValueError, match="gates_passed \\+ gates_failed != gates_total"):
            validate_qa_report(report)


class TestPriorityFixes:
    """Tests for priority fix generation."""

    def test_priority_ordering(self):
        """Test that priority fixes are ordered correctly (lint > type > test)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)

            # Create minimal project files
            (project_dir / "requirements.txt").write_text("pytest")

            agent = QAAgent(project_dir)

            gate_results = {
                "lint": {
                    "passed": False,
                    "duration_seconds": 1.0,
                    "errors": [{"file": "a.py", "line": 10, "message": "lint error"}],
                },
                "type_check": {
                    "passed": False,
                    "duration_seconds": 2.0,
                    "errors": [{"file": "b.py", "line": 20, "message": "type error"}],
                },
                "unit_tests": {
                    "passed": False,
                    "duration_seconds": 3.0,
                    "errors": [{"file": "c.py", "line": 30, "message": "test failed"}],
                },
                "browser_automation": {"passed": True, "duration_seconds": 0},
                "story_validation": {"passed": True, "duration_seconds": 0},
            }

            fixes = agent._generate_priority_fixes(gate_results)

            # Verify priority ordering
            assert len(fixes) == 3
            assert fixes[0]["gate"] == "lint"
            assert fixes[0]["priority"] == 1
            assert fixes[1]["gate"] == "type_check"
            assert fixes[1]["priority"] == 2
            assert fixes[2]["gate"] == "unit_tests"
            assert fixes[2]["priority"] == 3

    def test_file_sorting_within_priority(self):
        """Test that errors within same priority are sorted by file:line."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            (project_dir / "requirements.txt").write_text("pytest")

            agent = QAAgent(project_dir)

            gate_results = {
                "lint": {
                    "passed": False,
                    "duration_seconds": 1.0,
                    "errors": [
                        {"file": "b.py", "line": 20, "message": "error 1"},
                        {"file": "a.py", "line": 10, "message": "error 2"},
                        {"file": "a.py", "line": 5, "message": "error 3"},
                    ],
                },
                "type_check": {"passed": True, "duration_seconds": 0, "errors": []},
                "unit_tests": {"passed": True, "duration_seconds": 0, "errors": []},
                "browser_automation": {"passed": True, "duration_seconds": 0, "errors": []},
                "story_validation": {"passed": True, "duration_seconds": 0, "errors": []},
            }

            fixes = agent._generate_priority_fixes(gate_results)

            # Verify sorting: a.py:5, a.py:10, b.py:20
            assert len(fixes) == 3
            assert fixes[0]["file"] == "a.py"
            assert fixes[0]["line"] == 5
            assert fixes[1]["file"] == "a.py"
            assert fixes[1]["line"] == 10
            assert fixes[2]["file"] == "b.py"
            assert fixes[2]["line"] == 20


class TestErrorGrouping:
    """Tests for error grouping by file."""

    def test_group_errors_by_file(self):
        """Test that errors are grouped by file correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            (project_dir / "requirements.txt").write_text("pytest")

            agent = QAAgent(project_dir)

            gate_results = {
                "lint": {
                    "passed": False,
                    "errors": [
                        {"file": "src/main.py", "line": 10, "message": "lint1"},
                        {"file": "src/main.py", "line": 20, "message": "lint2"},
                    ],
                },
                "type_check": {
                    "passed": False,
                    "errors": [
                        {"file": "src/main.py", "line": 15, "message": "type1"},
                        {"file": "src/utils.py", "line": 5, "message": "type2"},
                    ],
                },
            }

            grouped = agent._group_errors_by_file(gate_results)

            # src/main.py should have 3 errors (sorted by line)
            assert "src/main.py" in grouped
            assert len(grouped["src/main.py"]) == 3
            assert grouped["src/main.py"][0]["line"] == 10
            assert grouped["src/main.py"][1]["line"] == 15
            assert grouped["src/main.py"][2]["line"] == 20

            # src/utils.py should have 1 error
            assert "src/utils.py" in grouped
            assert len(grouped["src/utils.py"]) == 1


class TestSummaryStatistics:
    """Tests for summary statistics computation."""

    def test_compute_summary_statistics(self):
        """Test that summary statistics are computed correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            (project_dir / "requirements.txt").write_text("pytest")

            agent = QAAgent(project_dir)

            gate_results = {
                "lint": {
                    "passed": False,
                    "duration_seconds": 1.5,
                    "errors": [
                        {"file": "a.py", "line": 1, "message": "e1"},
                        {"file": "a.py", "line": 2, "message": "e2"},
                    ],
                    "warnings": [{"message": "w1"}],
                },
                "type_check": {
                    "passed": True,
                    "duration_seconds": 2.5,
                    "errors": [],
                },
                "unit_tests": {
                    "passed": True,
                    "duration_seconds": 5.0,
                    "tests_run": 10,
                    "tests_passed": 10,
                    "tests_failed": 0,
                    "errors": [],
                },
                "browser_automation": {
                    "passed": True,
                    "duration_seconds": 10.0,
                    "errors": [],
                },
                "story_validation": {
                    "passed": True,
                    "duration_seconds": 1.0,
                    "errors": [],
                },
            }

            summary = agent._compute_summary_statistics(gate_results)

            assert summary["gates_passed"] == 4
            assert summary["gates_failed"] == 1
            assert summary["gates_total"] == 5
            assert summary["total_duration_seconds"] == 20.0
            assert summary["total_errors"] == 2
            assert summary["total_warnings"] == 1
            assert summary["files_with_errors"] == 1
            assert summary["tests_run"] == 10
            assert summary["tests_passed"] == 10
            assert summary["tests_failed"] == 0
            assert summary["errors_by_gate"] == {"lint": 2}


class TestDevAgentParsing:
    """Tests for T063: Verify Dev Agent can read and parse qa-report.json."""

    def test_dev_agent_can_parse_report(self):
        """Test that a saved qa-report.json can be loaded and parsed."""
        report = {
            "$schema": "qa-report-schema-v1.json",
            "feature_id": 42,
            "feature_description": "User authentication",
            "timestamp": "2025-12-09T10:00:00Z",
            "overall_status": "FAILED",
            "gates": {
                "lint": {
                    "passed": False,
                    "duration_seconds": 1.0,
                    "tool": "ruff",
                    "tool_version": "ruff=0.1.0",
                    "errors": [
                        {
                            "file": "src/auth.py",
                            "line": 42,
                            "column": 10,
                            "message": "E501: Line too long",
                            "rule": "E501",
                            "severity": "error",
                        }
                    ],
                },
                "type_check": {"passed": True, "duration_seconds": 2.0, "errors": []},
                "unit_tests": {
                    "passed": False,
                    "duration_seconds": 5.0,
                    "tests_run": 10,
                    "tests_passed": 9,
                    "tests_failed": 1,
                    "errors": [
                        {
                            "file": "tests/test_auth.py",
                            "line": 25,
                            "test_name": "test_login_invalid_password",
                            "message": "AssertionError: expected 401, got 500",
                        }
                    ],
                },
                "browser_automation": {"passed": True, "duration_seconds": 10.0, "errors": []},
                "story_validation": {"passed": True, "duration_seconds": 1.0, "errors": []},
            },
            "summary": {
                "gates_passed": 3,
                "gates_failed": 2,
                "gates_total": 5,
                "total_duration_seconds": 19.0,
                "total_errors": 2,
                "errors_by_gate": {"lint": 1, "unit_tests": 1},
                "files_with_errors": 2,
            },
            "errors_by_file": {
                "src/auth.py": [{"gate": "lint", "line": 42, "message": "E501: Line too long"}],
                "tests/test_auth.py": [
                    {"gate": "unit_tests", "line": 25, "message": "AssertionError"}
                ],
            },
            "priority_fixes": [
                {
                    "priority": 1,
                    "gate": "lint",
                    "message": "Fix lint error in src/auth.py:42:10 [E501]: E501: Line too long",
                    "file": "src/auth.py",
                    "line": 42,
                    "column": 10,
                    "rule": "E501",
                },
                {
                    "priority": 3,
                    "gate": "unit_tests",
                    "message": "Fix failing test 'test_login_invalid_password' in tests/test_auth.py:25",
                    "file": "tests/test_auth.py",
                    "line": 25,
                },
            ],
            "qa_agent_version": "1.0.0",
            "retry_count": 0,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            # Save report
            report_path = Path(tmpdir) / "qa-report.json"
            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)

            # Load and parse like Dev Agent would
            with open(report_path) as f:
                loaded_report = json.load(f)

            # Verify key fields Dev Agent needs
            assert loaded_report["overall_status"] == "FAILED"
            assert loaded_report["feature_id"] == 42

            # Dev Agent should be able to iterate priority_fixes
            priority_fixes = loaded_report["priority_fixes"]
            assert len(priority_fixes) == 2

            # First fix should be lint (highest priority)
            first_fix = priority_fixes[0]
            assert first_fix["priority"] == 1
            assert first_fix["gate"] == "lint"
            assert first_fix["file"] == "src/auth.py"
            assert first_fix["line"] == 42

            # Dev Agent should be able to access errors_by_file for efficient review
            errors_by_file = loaded_report["errors_by_file"]
            assert "src/auth.py" in errors_by_file
            assert "tests/test_auth.py" in errors_by_file

            # Dev Agent should be able to access gate-specific details
            lint_gate = loaded_report["gates"]["lint"]
            assert lint_gate["tool"] == "ruff"
            assert len(lint_gate["errors"]) == 1
            lint_error = lint_gate["errors"][0]
            assert lint_error["rule"] == "E501"

    def test_report_file_naming(self):
        """Test that report files are named correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            (project_dir / "requirements.txt").write_text("pytest")

            agent = QAAgent(project_dir)

            # Mock a minimal report
            report = {
                "$schema": "qa-report-schema-v1.json",
                "feature_id": 42,
                "feature_description": "Test feature",
                "timestamp": "2025-12-09T10:00:00Z",
                "overall_status": "PASSED",
                "gates": {
                    "lint": {"passed": True, "duration_seconds": 1.0, "errors": []},
                    "type_check": {"passed": True, "duration_seconds": 1.0, "errors": []},
                    "unit_tests": {"passed": True, "duration_seconds": 1.0, "errors": []},
                    "browser_automation": {"passed": True, "duration_seconds": 1.0, "errors": []},
                    "story_validation": {"passed": True, "duration_seconds": 1.0, "errors": []},
                },
                "summary": {
                    "gates_passed": 5,
                    "gates_failed": 0,
                    "gates_total": 5,
                    "total_duration_seconds": 5.0,
                },
                "priority_fixes": [],
            }

            report_path = agent.save_report(report)

            # Verify path format
            assert report_path.parent.name == "qa-reports"
            assert report_path.name.startswith("feature-42-")
            assert report_path.suffix == ".json"

            # Verify file exists and is valid JSON
            assert report_path.exists()
            with open(report_path) as f:
                loaded = json.load(f)
            assert loaded["feature_id"] == 42


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
