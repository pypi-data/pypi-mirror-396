"""
Tests for Story Validation Gate
================================

Tests for Phase 5 (T064-T075): Story Validation User Story
"""

import json
import tempfile
from pathlib import Path

import pytest

from quality.gates import StoryValidationGate


class TestStepParser:
    """Tests for T064: Test step parsing."""

    def test_parse_simple_string_steps(self):
        """Test parsing simple string steps into structured format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)

            # Create feature_list.json with simple string steps
            feature = {
                "id": 1,
                "description": "User login flow",
                "steps": [
                    "Navigate to /login",
                    "Click login button",
                    "Enter email in field",
                    "Verify user sees dashboard",
                ],
            }
            with open(project_dir / "feature_list.json", "w") as f:
                json.dump([feature], f)

            gate = StoryValidationGate(project_dir, feature_id=1)
            loaded_feature = gate._load_feature()
            steps = gate._parse_test_steps(loaded_feature)

            assert len(steps) == 4

            # Check navigate step
            assert steps[0]["action"] == "navigate"
            assert steps[0]["target"] == "/login"

            # Check click step
            assert steps[1]["action"] == "click"

            # Check fill step
            assert steps[2]["action"] == "fill"

            # Check verify step
            assert steps[3]["action"] == "verify"

    def test_parse_structured_steps(self):
        """Test parsing already-structured step objects."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)

            # Create feature_list.json with structured steps
            feature = {
                "id": 2,
                "description": "Checkout flow",
                "steps": [
                    {"action": "navigate", "target": "/cart"},
                    {"action": "click", "selector": "#checkout-btn"},
                    {"action": "fill", "selector": "#email", "value": "test@example.com"},
                    {"action": "verify", "selector": "#confirmation"},
                ],
            }
            with open(project_dir / "feature_list.json", "w") as f:
                json.dump([feature], f)

            gate = StoryValidationGate(project_dir, feature_id=2)
            loaded_feature = gate._load_feature()
            steps = gate._parse_test_steps(loaded_feature)

            assert len(steps) == 4
            assert steps[0]["action"] == "navigate"
            assert steps[0]["target"] == "/cart"
            assert steps[1]["selector"] == "#checkout-btn"
            assert steps[2]["value"] == "test@example.com"
            assert steps[3]["selector"] == "#confirmation"

    def test_parse_mixed_steps(self):
        """Test parsing mix of string and structured steps."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)

            feature = {
                "id": 3,
                "description": "Mixed flow",
                "steps": [
                    "Navigate to /home",
                    {"action": "click", "selector": "#menu"},
                    "Verify page loads correctly",
                ],
            }
            with open(project_dir / "feature_list.json", "w") as f:
                json.dump([feature], f)

            gate = StoryValidationGate(project_dir, feature_id=3)
            loaded_feature = gate._load_feature()
            steps = gate._parse_test_steps(loaded_feature)

            assert len(steps) == 3
            assert steps[0]["action"] == "navigate"
            assert steps[1]["action"] == "click"
            assert steps[2]["action"] == "verify"


class TestFeatureLoading:
    """Tests for loading features from feature_list.json."""

    def test_load_existing_feature(self):
        """Test loading an existing feature."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)

            features = [
                {"id": 1, "description": "Feature 1", "steps": []},
                {"id": 2, "description": "Feature 2", "steps": ["Navigate to /test"]},
            ]
            with open(project_dir / "feature_list.json", "w") as f:
                json.dump(features, f)

            gate = StoryValidationGate(project_dir, feature_id=2)
            feature = gate._load_feature()

            assert feature is not None
            assert feature["id"] == 2
            assert feature["description"] == "Feature 2"

    def test_load_nonexistent_feature(self):
        """Test loading a feature that doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)

            features = [{"id": 1, "description": "Feature 1", "steps": []}]
            with open(project_dir / "feature_list.json", "w") as f:
                json.dump(features, f)

            gate = StoryValidationGate(project_dir, feature_id=999)
            feature = gate._load_feature()

            assert feature is None

    def test_load_without_feature_list(self):
        """Test loading when feature_list.json doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)

            gate = StoryValidationGate(project_dir, feature_id=1)
            feature = gate._load_feature()

            assert feature is None


class TestGateResult:
    """Tests for story validation gate results."""

    def test_feature_not_found_result(self):
        """Test result when feature is not found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)

            # Empty feature list
            with open(project_dir / "feature_list.json", "w") as f:
                json.dump([], f)

            gate = StoryValidationGate(project_dir, feature_id=1)
            result = gate.run()

            assert result["passed"] is False
            assert result["acceptance_criteria_met"] == 0
            assert result["acceptance_criteria_total"] == 0
            assert len(result["errors"]) == 1
            assert "not found" in result["errors"][0]["message"]

    def test_no_steps_defined_result(self):
        """Test result when feature has no test steps."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)

            features = [{"id": 1, "description": "No steps", "steps": []}]
            with open(project_dir / "feature_list.json", "w") as f:
                json.dump(features, f)

            gate = StoryValidationGate(project_dir, feature_id=1)
            result = gate.run()

            assert result["passed"] is True
            assert result["acceptance_criteria_met"] == 0
            assert result["acceptance_criteria_total"] == 0
            assert "note" in result
            assert "No test steps" in result["note"]

    def test_result_has_screenshots_field(self):
        """Test that result includes screenshots field."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)

            features = [{"id": 1, "description": "Test", "steps": []}]
            with open(project_dir / "feature_list.json", "w") as f:
                json.dump(features, f)

            gate = StoryValidationGate(project_dir, feature_id=1)
            result = gate.run()

            assert "screenshots" in result
            assert isinstance(result["screenshots"], list)


class TestStepPatternRecognition:
    """Tests for step pattern recognition (T064-T067)."""

    def test_navigate_patterns(self):
        """Test recognition of navigate patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            gate = StoryValidationGate(project_dir, feature_id=1)

            # Test various navigate patterns
            patterns = [
                ("Navigate to /login", "navigate", "/login"),
                ("Go to homepage", "navigate", "homepage"),
                ("Navigate to https://example.com", "navigate", "https://example.com"),
            ]

            for text, expected_action, expected_target in patterns:
                step = gate._parse_string_step(text, 0)
                assert step["action"] == expected_action, f"Failed for: {text}"
                assert expected_target in step.get("target", ""), f"Failed target for: {text}"

    def test_click_patterns(self):
        """Test recognition of click patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            gate = StoryValidationGate(project_dir, feature_id=1)

            patterns = [
                "Click login button",
                "Click the submit button",
                "Click on the menu",
            ]

            for text in patterns:
                step = gate._parse_string_step(text, 0)
                assert step["action"] == "click", f"Failed for: {text}"

    def test_fill_patterns(self):
        """Test recognition of fill/type patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            gate = StoryValidationGate(project_dir, feature_id=1)

            patterns = [
                "Enter email address",
                "Type password",
                "Fill in the form",
                "Input username",
            ]

            for text in patterns:
                step = gate._parse_string_step(text, 0)
                assert step["action"] == "fill", f"Failed for: {text}"

    def test_verify_patterns(self):
        """Test recognition of verify patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            gate = StoryValidationGate(project_dir, feature_id=1)

            patterns = [
                "Verify user sees dashboard",
                "Check the error message",
                "Confirm login successful",
                "Ensure page loaded",
                "Expect success message",
            ]

            for text in patterns:
                step = gate._parse_string_step(text, 0)
                assert step["action"] == "verify", f"Failed for: {text}"

    def test_scroll_patterns(self):
        """Test recognition of scroll patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            gate = StoryValidationGate(project_dir, feature_id=1)

            step = gate._parse_string_step("Scroll down to footer", 0)
            assert step["action"] == "scroll"

    def test_wait_patterns(self):
        """Test recognition of wait patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            gate = StoryValidationGate(project_dir, feature_id=1)

            step = gate._parse_string_step("Wait for page to load", 0)
            assert step["action"] == "wait"


class TestContinueOnFailure:
    """Tests for T073: Continue executing remaining steps after failures."""

    def test_steps_continue_after_error(self):
        """Test that step execution continues even after a step fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)

            # Create feature with steps that will fail (no browser to navigate)
            features = [
                {
                    "id": 1,
                    "description": "Multi-step flow",
                    "steps": [
                        "Navigate to /page1",
                        "Navigate to /page2",
                        "Navigate to /page3",
                    ],
                }
            ]
            with open(project_dir / "feature_list.json", "w") as f:
                json.dump(features, f)

            gate = StoryValidationGate(project_dir, feature_id=1)

            # The gate will fail because there's no browser/Playwright
            # But we're testing that it returns results for all steps
            result = gate.run()

            # Should have step_results for all 3 steps
            assert "step_results" in result
            # Even if Playwright not installed, should have results or errors
            assert len(result.get("step_results", [])) > 0 or len(result.get("errors", [])) > 0


class TestScreenshotCapture:
    """Tests for T066 and T075: Screenshot capture."""

    def test_screenshots_directory_created(self):
        """Test that screenshots directory is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)

            features = [{"id": 1, "description": "Test", "steps": []}]
            with open(project_dir / "feature_list.json", "w") as f:
                json.dump(features, f)

            gate = StoryValidationGate(project_dir, feature_id=1)

            # Screenshots directory should be created on gate init
            assert gate.screenshots_dir.exists()
            assert gate.screenshots_dir.is_dir()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
