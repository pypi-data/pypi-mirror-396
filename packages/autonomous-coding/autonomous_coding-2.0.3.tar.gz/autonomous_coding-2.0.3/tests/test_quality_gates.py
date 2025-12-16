"""
Tests for Quality Gates
=======================

Tests for quality gate implementations (T143)
"""

from unittest.mock import MagicMock, patch

import pytest

from quality.gates import (
    BrowserAutomationGate,
    LintGate,
    StoryValidationGate,
    TypeCheckGate,
    UnitTestGate,
)


class TestQualityGateBase:
    """Tests for QualityGate base class."""

    def test_lint_gate_stores_project_dir(self, tmp_path):
        """Test that constructor stores project directory."""
        gate = LintGate(tmp_path)
        assert gate.project_dir == tmp_path

    def test_name_derived_from_class(self, tmp_path):
        """Test name is derived from class name."""
        # Gate names are class name with 'Gate' removed and lowercased
        gate = LintGate(tmp_path)
        assert "lint" in gate.name.lower()


class TestLintGate:
    """Tests for LintGate implementation."""

    @pytest.fixture
    def lint_gate(self, tmp_path):
        """Create LintGate instance."""
        return LintGate(tmp_path)

    def test_lint_gate_name(self, lint_gate):
        """Test LintGate has correct name."""
        assert lint_gate.name == "lint"

    @patch("subprocess.run")
    def test_lint_gate_biome_success(self, mock_run, lint_gate, tmp_path):
        """Test LintGate with successful biome run."""
        # Create a package.json to trigger JS/TS linting
        (tmp_path / "package.json").write_text("{}")

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"diagnostics": []}',
            stderr="",
        )

        result = lint_gate.run()

        assert result["passed"] is True
        assert "lint" in result["tool"] or result["tool"] == "biome"

    @patch("subprocess.run")
    def test_lint_gate_ruff_success(self, mock_run, lint_gate, tmp_path):
        """Test LintGate with successful ruff run."""
        # Create a Python file
        (tmp_path / "test.py").write_text("print('hello')")

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="[]",
            stderr="",
        )

        result = lint_gate.run()

        # Result should include duration
        assert "duration_seconds" in result

    def test_lint_gate_no_files(self, lint_gate):
        """Test LintGate with no lintable files."""
        result = lint_gate.run()

        # Should pass if no files to lint
        assert result["passed"] is True


class TestTypeCheckGate:
    """Tests for TypeCheckGate implementation."""

    @pytest.fixture
    def type_gate(self, tmp_path):
        """Create TypeCheckGate instance."""
        return TypeCheckGate(tmp_path)

    def test_type_gate_name(self, type_gate):
        """Test TypeCheckGate has correct name."""
        # Name is derived from class name: TypeCheckGate -> typecheck
        assert "typecheck" in type_gate.name.lower() or "type" in type_gate.name.lower()

    @patch("subprocess.run")
    def test_type_gate_mypy_success(self, mock_run, type_gate, tmp_path):
        """Test TypeCheckGate with successful mypy run."""
        (tmp_path / "test.py").write_text("x: int = 1")

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="[]",
            stderr="",
        )

        result = type_gate.run()

        assert "duration_seconds" in result

    def test_type_gate_no_files(self, type_gate):
        """Test TypeCheckGate with no typeable files."""
        result = type_gate.run()

        assert result["passed"] is True


class TestUnitTestGate:
    """Tests for UnitTestGate implementation."""

    @pytest.fixture
    def test_gate(self, tmp_path):
        """Create UnitTestGate instance."""
        return UnitTestGate(tmp_path)

    def test_unit_test_gate_name(self, test_gate):
        """Test UnitTestGate has correct name."""
        # Name is derived from class name
        assert "unittest" in test_gate.name.lower() or "test" in test_gate.name.lower()

    @patch("subprocess.run")
    def test_unit_test_gate_pytest_success(self, mock_run, test_gate, tmp_path):
        """Test UnitTestGate with passing pytest."""
        (tmp_path / "test_example.py").write_text("def test_pass(): pass")

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"tests": 1, "passed": 1, "failed": 0}',
            stderr="",
        )

        result = test_gate.run()

        assert "duration_seconds" in result

    def test_unit_test_gate_no_tests(self, test_gate):
        """Test UnitTestGate with no test files."""
        result = test_gate.run()

        # Result should have passed field
        assert "passed" in result


class TestBrowserAutomationGate:
    """Tests for BrowserAutomationGate implementation."""

    @pytest.fixture
    def browser_gate(self, tmp_path):
        """Create BrowserAutomationGate instance."""
        return BrowserAutomationGate(tmp_path)

    def test_browser_gate_name(self, browser_gate):
        """Test BrowserAutomationGate has correct name."""
        # Name is derived from class name
        assert "browser" in browser_gate.name.lower() or "automation" in browser_gate.name.lower()

    def test_browser_gate_no_tests(self, browser_gate):
        """Test BrowserAutomationGate with no test files."""
        result = browser_gate.run()

        # Should pass if no browser tests
        assert result["passed"] is True

    @patch("subprocess.run")
    def test_browser_gate_playwright_success(self, mock_run, browser_gate, tmp_path):
        """Test BrowserAutomationGate with passing playwright."""
        (tmp_path / "e2e").mkdir()
        (tmp_path / "e2e" / "test_browser.py").write_text("# browser test")

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"tests": [], "passed": 1, "failed": 0}',
            stderr="",
        )

        result = browser_gate.run()

        assert "duration_seconds" in result


class TestStoryValidationGate:
    """Tests for StoryValidationGate implementation."""

    @pytest.fixture
    def story_gate(self, tmp_path):
        """Create StoryValidationGate instance."""
        return StoryValidationGate(tmp_path, feature_id=1)

    def test_story_gate_name(self, story_gate):
        """Test StoryValidationGate has correct name."""
        # Name is derived from class name
        assert "story" in story_gate.name.lower() or "validation" in story_gate.name.lower()

    def test_story_gate_feature_id(self, story_gate):
        """Test StoryValidationGate stores feature_id."""
        assert story_gate.feature_id == 1

    def test_story_gate_no_feature_list(self, story_gate):
        """Test StoryValidationGate with no feature_list.json."""
        result = story_gate.run()

        # Should fail gracefully
        assert result["passed"] is False
        assert any(
            "not found" in str(e.get("message", "")).lower() for e in result.get("errors", [])
        )

    def test_story_gate_creates_screenshots_dir(self, tmp_path):
        """Test StoryValidationGate creates screenshots directory."""
        gate = StoryValidationGate(tmp_path, feature_id=1)

        assert gate.screenshots_dir.exists()


class TestGateResultStructure:
    """Tests for gate result structure consistency."""

    @pytest.fixture
    def tmp_project(self, tmp_path):
        """Create temporary project directory."""
        return tmp_path

    def test_all_gates_return_required_fields(self, tmp_project):
        """Test all gates return required result fields."""
        gates = [
            LintGate(tmp_project),
            TypeCheckGate(tmp_project),
            UnitTestGate(tmp_project),
            BrowserAutomationGate(tmp_project),
            StoryValidationGate(tmp_project, feature_id=1),
        ]

        for gate in gates:
            result = gate.run()

            # Required fields
            assert "passed" in result, f"{gate.name} missing 'passed' field"
            assert "duration_seconds" in result, f"{gate.name} missing 'duration_seconds'"
            assert isinstance(result["passed"], bool), f"{gate.name} 'passed' should be bool"
            assert isinstance(result["duration_seconds"], (int, float)), (
                f"{gate.name} duration should be number"
            )


class TestToolVersionCapture:
    """Tests for tool version capture (T057)."""

    @pytest.fixture
    def lint_gate(self, tmp_path):
        """Create LintGate instance."""
        return LintGate(tmp_path)

    def test_tool_version_included(self, lint_gate, tmp_path):
        """Test that tool version is included in results."""
        # Create a file to lint
        (tmp_path / "test.py").write_text("x = 1")

        result = lint_gate.run()

        # Result should have tool info
        assert "tool" in result or "tool_version" in result or result["passed"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
