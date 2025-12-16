"""
Spec Validator
==============

Validates application specifications using Claude before development begins.
This is a "shift-left" approach to catch issues early when they're cheap to fix.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.orchestrator import atomic_write_json


class SpecValidator:
    """
    Validates app_spec.txt and feature_list.json using Claude.

    This runs AFTER the Initializer creates the project structure
    but BEFORE the Dev agent starts coding.
    """

    def __init__(self, project_dir: Path):
        """
        Initialize the spec validator.

        Args:
            project_dir: Path to the project directory
        """
        self.project_dir = Path(project_dir)
        self.reports_dir = self.project_dir / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def load_spec(self) -> str | None:
        """Load the app_spec.txt file."""
        spec_path = self.project_dir / "app_spec.txt"
        if not spec_path.exists():
            return None
        return spec_path.read_text()

    def load_feature_list(self) -> dict[str, Any] | None:
        """Load the feature_list.json file."""
        feature_path = self.project_dir / "feature_list.json"
        if not feature_path.exists():
            return None
        try:
            with open(feature_path) as f:
                return json.load(f)
        except json.JSONDecodeError:
            return None

    def validate_spec_structure(self, spec_content: str) -> list[dict[str, Any]]:
        """
        Perform basic structural validation of the spec.

        Returns list of issues found.
        """
        issues = []

        # Check for required sections
        required_sections = [
            "app_name",
            "technology_stack",
            "features",
        ]

        for section in required_sections:
            if f"<{section}>" not in spec_content.lower():
                issues.append(
                    {
                        "severity": "major",
                        "category": "completeness",
                        "description": f"Missing required section: {section}",
                        "location": "app_spec.txt",
                        "suggestion": f"Add a <{section}> section to the specification",
                    }
                )

        # Check for empty sections
        if "<features>" in spec_content and "</features>" in spec_content:
            features_start = spec_content.find("<features>")
            features_end = spec_content.find("</features>")
            features_content = spec_content[features_start:features_end]
            if len(features_content.strip()) < 50:
                issues.append(
                    {
                        "severity": "critical",
                        "category": "completeness",
                        "description": "Features section appears to be empty or very short",
                        "location": "app_spec.txt <features>",
                        "suggestion": "Add detailed feature descriptions",
                    }
                )

        return issues

    def validate_feature_list(self, feature_list: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Validate the feature_list.json structure and content.

        Returns list of issues found.
        """
        issues = []

        features = feature_list.get("features", [])

        if not features:
            issues.append(
                {
                    "severity": "critical",
                    "category": "completeness",
                    "description": "No features defined in feature_list.json",
                    "location": "feature_list.json",
                    "suggestion": "Add features with id, description, and test_cases",
                }
            )
            return issues

        for idx, feature in enumerate(features):
            feature_id = feature.get("id", idx + 1)

            # Check for required fields
            if not feature.get("description"):
                issues.append(
                    {
                        "severity": "major",
                        "category": "clarity",
                        "description": f"Feature {feature_id} missing description",
                        "location": f"feature_list.json feature #{feature_id}",
                        "suggestion": "Add a clear description of what this feature does",
                    }
                )

            # Check for test cases
            test_cases = feature.get("test_cases", [])
            if not test_cases:
                issues.append(
                    {
                        "severity": "major",
                        "category": "testability",
                        "description": f"Feature {feature_id} has no test cases",
                        "location": f"feature_list.json feature #{feature_id}",
                        "suggestion": "Add at least one test case with expected outcomes",
                    }
                )

            # Check for acceptance criteria
            if not feature.get("acceptance_criteria") and not feature.get("steps"):
                issues.append(
                    {
                        "severity": "minor",
                        "category": "testability",
                        "description": f"Feature {feature_id} missing acceptance criteria",
                        "location": f"feature_list.json feature #{feature_id}",
                        "suggestion": "Add acceptance_criteria or steps to verify completion",
                    }
                )

        return issues

    def calculate_completeness_score(
        self, spec_issues: list[dict], feature_issues: list[dict]
    ) -> float:
        """Calculate overall completeness score (0.0-1.0)."""
        all_issues = spec_issues + feature_issues

        if not all_issues:
            return 1.0

        # Weight issues by severity
        severity_weights = {
            "critical": 0.3,
            "major": 0.15,
            "minor": 0.05,
        }

        penalty = sum(
            severity_weights.get(issue.get("severity", "minor"), 0.05) for issue in all_issues
        )

        return max(0.0, 1.0 - penalty)

    def determine_status(self, completeness_score: float, issues: list[dict]) -> str:
        """
        Determine overall validation status.

        Returns: PASSED, NEEDS_REVISION, or BLOCKED
        """
        critical_issues = [i for i in issues if i.get("severity") == "critical"]
        major_issues = [i for i in issues if i.get("severity") == "major"]

        if critical_issues:
            return "BLOCKED"

        if completeness_score < 0.6 or len(major_issues) > 3:
            return "NEEDS_REVISION"

        if completeness_score >= 0.8:
            return "PASSED"

        return "NEEDS_REVISION"

    def run_validation(self) -> dict[str, Any]:
        """
        Run the full spec validation.

        Returns:
            Validation report dictionary
        """
        # Load files
        spec_content = self.load_spec()
        feature_list = self.load_feature_list()

        # Initialize report
        report = {
            "validation_timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_status": "BLOCKED",
            "confidence_score": 0.0,
            "summary": "",
            "spec_review": {
                "completeness_score": 0.0,
                "issues": [],
            },
            "feature_review": {
                "total_features": 0,
                "well_defined": 0,
                "needs_clarification": 0,
                "feature_issues": [],
            },
            "recommendations": [],
            "ready_for_development": False,
            "blocking_issues": [],
        }

        # Check if files exist
        if not spec_content:
            report["blocking_issues"].append("app_spec.txt not found")
            report["summary"] = "Cannot validate: app_spec.txt not found"
            return report

        if not feature_list:
            report["blocking_issues"].append("feature_list.json not found or invalid")
            report["summary"] = "Cannot validate: feature_list.json not found"
            return report

        # Run validations
        spec_issues = self.validate_spec_structure(spec_content)
        feature_issues = self.validate_feature_list(feature_list)

        all_issues = spec_issues + feature_issues
        completeness_score = self.calculate_completeness_score(spec_issues, feature_issues)
        status = self.determine_status(completeness_score, all_issues)

        # Count feature stats
        features = feature_list.get("features", [])
        features_with_issues = set()
        for issue in feature_issues:
            loc = issue.get("location", "")
            if "feature #" in loc:
                try:
                    fid = int(loc.split("feature #")[1].split()[0])
                    features_with_issues.add(fid)
                except (ValueError, IndexError):
                    pass

        well_defined = len(features) - len(features_with_issues)

        # Build report
        report["overall_status"] = status
        report["confidence_score"] = completeness_score
        report["spec_review"]["completeness_score"] = completeness_score
        report["spec_review"]["issues"] = spec_issues
        report["feature_review"]["total_features"] = len(features)
        report["feature_review"]["well_defined"] = well_defined
        report["feature_review"]["needs_clarification"] = len(features_with_issues)
        report["feature_review"]["feature_issues"] = feature_issues
        report["ready_for_development"] = status in ("PASSED", "NEEDS_REVISION")

        # Add blocking issues
        critical_issues = [i for i in all_issues if i.get("severity") == "critical"]
        report["blocking_issues"] = [i["description"] for i in critical_issues]

        # Generate recommendations
        if spec_issues:
            report["recommendations"].append(
                {
                    "priority": 1,
                    "action": "Address spec structure issues",
                    "reason": "Core specification needs to be complete for accurate implementation",
                }
            )

        if feature_issues:
            report["recommendations"].append(
                {
                    "priority": 2,
                    "action": "Add test cases to features without them",
                    "reason": "Test cases are essential for QA validation",
                }
            )

        # Summary
        if status == "PASSED":
            report["summary"] = (
                f"Specification is ready for development. {len(features)} features defined with {completeness_score:.0%} completeness."
            )
        elif status == "NEEDS_REVISION":
            report["summary"] = (
                f"Specification can proceed but has {len(all_issues)} issues to address. Review recommendations."
            )
        else:
            report["summary"] = (
                f"Specification blocked by {len(critical_issues)} critical issues. Must be fixed before development."
            )

        return report

    def save_report(self, report: dict[str, Any]) -> Path:
        """
        Save the validation report to the reports directory.

        Returns:
            Path to the saved report
        """
        report_path = self.reports_dir / "spec-validation-report.json"
        atomic_write_json(report_path, report)
        return report_path

    def print_report_summary(self, report: dict[str, Any]) -> None:
        """Print a human-readable summary of the validation report."""
        status = report["overall_status"]
        status_emoji = {"PASSED": "✅", "NEEDS_REVISION": "⚠️", "BLOCKED": "❌"}.get(status, "❓")

        print("\n" + "=" * 60)
        print(f"SPEC VALIDATION REPORT {status_emoji}")
        print("=" * 60)
        print(f"\nStatus: {status}")
        print(f"Completeness: {report['confidence_score']:.0%}")
        print(f"Summary: {report['summary']}")

        if report["blocking_issues"]:
            print(f"\n🚫 BLOCKING ISSUES ({len(report['blocking_issues'])}):")
            for issue in report["blocking_issues"]:
                print(f"   - {issue}")

        spec_issues = report["spec_review"]["issues"]
        feature_issues = report["feature_review"]["feature_issues"]

        if spec_issues:
            print(f"\n📄 Spec Issues ({len(spec_issues)}):")
            for issue in spec_issues[:5]:  # Show top 5
                print(f"   [{issue['severity'].upper()}] {issue['description']}")

        if feature_issues:
            print(f"\n📋 Feature Issues ({len(feature_issues)}):")
            for issue in feature_issues[:5]:  # Show top 5
                print(f"   [{issue['severity'].upper()}] {issue['description']}")

        if report["recommendations"]:
            print("\n💡 Recommendations:")
            for rec in report["recommendations"]:
                print(f"   {rec['priority']}. {rec['action']}")
                print(f"      Reason: {rec['reason']}")

        print(f"\nReady for development: {'Yes' if report['ready_for_development'] else 'No'}")
        print("=" * 60)


async def run_spec_validator(project_dir: Path) -> tuple[str, dict[str, Any]]:
    """
    Run the spec validator and return results.

    Args:
        project_dir: Project directory path

    Returns:
        Tuple of (next_state, report)
        next_state is "SPEC_VALIDATED" if passed, "INITIALIZER" if blocked
    """
    validator = SpecValidator(project_dir)
    report = validator.run_validation()
    report_path = validator.save_report(report)
    validator.print_report_summary(report)

    print(f"\nFull report saved to: {report_path}")

    # Determine next state
    if report["ready_for_development"]:
        next_state = "SPEC_VALIDATED"
        print("\n✅ Spec validation PASSED - proceeding to development")
    else:
        next_state = "INITIALIZER"  # Go back to revise
        print("\n❌ Spec validation FAILED - needs revision")

    return next_state, report
