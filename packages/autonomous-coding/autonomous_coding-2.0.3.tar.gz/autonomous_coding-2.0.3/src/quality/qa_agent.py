"""
QA Agent
========

Provides independent quality validation through 5 quality gates:
1. Lint
2. Type Check
3. Unit Tests
4. Browser Automation
5. Story Validation

Generates structured feedback reports (qa-report.json) and enforces RBAC.
"""

import json
import subprocess
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.orchestrator import atomic_write_json
from quality.gates import (
    BrowserAutomationGate,
    LintGate,
    StoryValidationGate,
    TypeCheckGate,
    UnitTestGate,
)

# JSON Schema for QA report validation
QA_REPORT_SCHEMA = {
    "type": "object",
    "required": ["feature_id", "timestamp", "overall_status", "gates", "summary"],
    "properties": {
        "feature_id": {"type": "integer"},
        "feature_description": {"type": "string"},
        "timestamp": {"type": "string"},
        "overall_status": {"type": "string", "enum": ["PASSED", "FAILED"]},
        "gates": {
            "type": "object",
            "required": [
                "lint",
                "type_check",
                "unit_tests",
                "browser_automation",
                "story_validation",
            ],
        },
        "summary": {
            "type": "object",
            "required": [
                "gates_passed",
                "gates_failed",
                "gates_total",
                "total_duration_seconds",
            ],
        },
        "priority_fixes": {"type": "array"},
        "qa_agent_version": {"type": "string"},
        "retry_count": {"type": "integer"},
    },
}


def validate_qa_report(data: dict[str, Any]) -> bool:
    """
    Validate QA report data against schema.

    Args:
        data: QA report dictionary

    Returns:
        True if valid

    Raises:
        ValueError: If validation fails
    """
    required_fields = ["feature_id", "timestamp", "overall_status", "gates", "summary"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    valid_statuses = ["PASSED", "FAILED"]
    if data["overall_status"] not in valid_statuses:
        raise ValueError(
            f"Invalid overall_status: {data['overall_status']}. Must be one of: {valid_statuses}"
        )

    required_gates = [
        "lint",
        "type_check",
        "unit_tests",
        "browser_automation",
        "story_validation",
    ]
    gates = data.get("gates", {})
    missing_gates = [g for g in required_gates if g not in gates]
    if missing_gates:
        raise ValueError(f"Missing required gates: {', '.join(missing_gates)}")

    for gate_name in required_gates:
        gate_result = gates.get(gate_name, {})
        if "passed" not in gate_result:
            raise ValueError(f"Gate '{gate_name}' missing 'passed' field")
        if "duration_seconds" not in gate_result:
            raise ValueError(f"Gate '{gate_name}' missing 'duration_seconds' field")

    all_gates_passed = all(gates[gate].get("passed", False) for gate in required_gates)
    if data["overall_status"] == "PASSED" and not all_gates_passed:
        raise ValueError("overall_status is PASSED but not all gates passed")

    if data["overall_status"] == "FAILED" and ("priority_fixes" not in data or len(data["priority_fixes"]) == 0):
            raise ValueError("priority_fixes must be non-empty when overall_status is FAILED")

    summary = data.get("summary", {})
    required_summary_fields = [
        "gates_passed",
        "gates_failed",
        "gates_total",
        "total_duration_seconds",
    ]
    missing_summary = [f for f in required_summary_fields if f not in summary]
    if missing_summary:
        raise ValueError(f"Summary missing required fields: {', '.join(missing_summary)}")

    if summary.get("gates_passed", 0) + summary.get("gates_failed", 0) != summary.get(
        "gates_total", 0
    ):
        raise ValueError("Summary gates_passed + gates_failed != gates_total")

    return True


class QAAgent:
    """QA Agent for independent quality validation."""

    VERSION = "2.0.0"
    MAX_RETRIES = 3

    def __init__(self, project_dir: Path, app_url: str = "http://localhost:3000"):
        """
        Initialize QA Agent.

        Args:
            project_dir: Project directory path
            app_url: Application URL for browser testing
        """
        self.project_dir = Path(project_dir)
        self.app_url = app_url

    def _create_gates(self, feature_id: int = 0) -> list:
        """Create quality gates with feature-specific configuration."""
        return [
            LintGate(self.project_dir),
            TypeCheckGate(self.project_dir),
            UnitTestGate(self.project_dir),
            BrowserAutomationGate(self.project_dir),
            StoryValidationGate(self.project_dir, feature_id=feature_id, app_url=self.app_url),
        ]

    def run_quality_gates(self, feature_id: int, feature_description: str) -> dict[str, Any]:
        """Execute all quality gates for a feature."""
        print(f"\n{'=' * 70}")
        print(f"QA Validation - Feature #{feature_id}")
        print(f"{'=' * 70}\n")

        gate_results: dict[str, Any] = {}
        retry_count = 0
        gates = self._create_gates(feature_id=feature_id)

        for gate in gates:
            gate_name = gate.name
            print(f"Running {gate_name} gate...", flush=True)

            result = None
            for attempt in range(self.MAX_RETRIES):
                try:
                    result = gate.run()
                    if result["passed"]:
                        print(f"  ✓ {gate_name} PASSED ({result['duration_seconds']}s)")
                        break
                    else:
                        error_count = len(result.get("errors", []))
                        print(
                            f"  ✗ {gate_name} FAILED: {error_count} error(s) "
                            f"({result['duration_seconds']}s)"
                        )
                        if gate_name in ["unit_tests", "browser_automation"] and attempt < self.MAX_RETRIES - 1:
                                print(f"    Retrying {gate_name} (attempt {attempt + 2})...")
                                retry_count += 1
                                time.sleep(2)
                                continue
                        break
                except TimeoutError as e:
                    print(f"  ✗ {gate_name} TIMEOUT: {e}")
                    result = {
                        "passed": False,
                        "duration_seconds": 0,
                        "tool": gate_name,
                        "errors": [{"message": f"Gate timed out: {e}"}],
                    }
                    break
                except Exception as e:
                    print(f"  ✗ {gate_name} ERROR: {e}")
                    result = {
                        "passed": False,
                        "duration_seconds": 0,
                        "tool": gate_name,
                        "errors": [{"message": f"Gate crashed: {e}"}],
                    }
                    break

            gate_results[gate_name] = result

        overall_passed = all(result["passed"] for result in gate_results.values())
        summary = self._compute_summary_statistics(gate_results)
        errors_by_file = self._group_errors_by_file(gate_results)

        report: dict[str, Any] = {
            "$schema": "qa-report-schema-v1.json",
            "feature_id": feature_id,
            "feature_description": feature_description,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "overall_status": "PASSED" if overall_passed else "FAILED",
            "gates": gate_results,
            "summary": summary,
            "errors_by_file": errors_by_file,
            "priority_fixes": self._generate_priority_fixes(gate_results),
            "qa_agent_version": self.VERSION,
            "retry_count": retry_count,
        }

        validate_qa_report(report)

        print(f"\n{'=' * 70}")
        print(f"QA Summary: {summary['gates_passed']}/{summary['gates_total']} gates passed")
        if summary["total_errors"] > 0:
            print(
                f"Total Errors: {summary['total_errors']} in {summary['files_with_errors']} file(s)"
            )
            if summary["errors_by_gate"]:
                print(f"Errors by gate: {summary['errors_by_gate']}")
        if summary["tests_run"] > 0:
            print(f"Tests: {summary['tests_passed']}/{summary['tests_run']} passed")
        print(f"Duration: {summary['total_duration_seconds']}s")
        print(f"Overall: {'✓ PASSED' if overall_passed else '✗ FAILED'}")
        print(f"{'=' * 70}\n")

        return report

    def _generate_priority_fixes(self, gate_results: dict[str, Any]) -> list[dict[str, Any]]:
        """Generate prioritized list of fixes from gate results."""
        priority_fixes: list[dict[str, Any]] = []
        gate_priorities = {
            "lint": 1,
            "type_check": 2,
            "unit_tests": 3,
            "browser_automation": 4,
            "story_validation": 5,
        }

        all_errors: list[dict[str, Any]] = []
        for gate_name, priority in gate_priorities.items():
            gate_result = gate_results.get(gate_name, {})
            errors = gate_result.get("errors", [])
            for error in errors:
                all_errors.append(
                    {
                        "priority": priority,
                        "gate": gate_name,
                        "file": error.get("file", ""),
                        "line": error.get("line", 0),
                        "column": error.get("column", 0),
                        "message": error.get("message", "Unknown error"),
                        "rule": error.get("rule", ""),
                        "test_name": error.get("test_name", ""),
                        "severity": error.get("severity", "error"),
                    }
                )

        all_errors.sort(key=lambda x: (x["priority"], x["file"], x["line"], x["column"]))

        for _i, error in enumerate(all_errors, 1):
            gate = error["gate"]
            file_path = error["file"]
            line = error["line"]
            column = error["column"]
            message = error["message"]
            rule = error.get("rule", "")
            test_name = error.get("test_name", "")

            location = file_path
            if line > 0:
                location += f":{line}"
                if column > 0:
                    location += f":{column}"

            if gate == "lint":
                fix_msg = f"Fix lint error in {location}"
                if rule:
                    fix_msg += f" [{rule}]"
                fix_msg += f": {message}"
            elif gate == "type_check":
                fix_msg = f"Fix type error in {location}"
                if rule:
                    fix_msg += f" [{rule}]"
                fix_msg += f": {message}"
            elif gate == "unit_tests":
                fix_msg = "Fix failing test"
                if test_name:
                    fix_msg += f" '{test_name}'"
                if file_path:
                    fix_msg += f" in {location}"
                fix_msg += f": {message[:200]}"
            elif gate == "browser_automation":
                fix_msg = "Fix browser test failure"
                if test_name:
                    fix_msg += f" '{test_name}'"
                if file_path:
                    fix_msg += f" in {location}"
                fix_msg += f": {message[:200]}"
            elif gate == "story_validation":
                fix_msg = f"Fix story validation failure: {message}"
            else:
                fix_msg = f"Fix {gate} issue in {location}: {message}"

            priority_fixes.append(
                {
                    "priority": error["priority"],
                    "gate": gate,
                    "message": fix_msg,
                    "file": file_path,
                    "line": line,
                    "column": column,
                    "rule": rule,
                }
            )

        return priority_fixes

    def _group_errors_by_file(
        self, gate_results: dict[str, Any]
    ) -> dict[str, list[dict[str, Any]]]:
        """Group all errors by file for efficient review."""
        errors_by_file: dict[str, list[dict[str, Any]]] = defaultdict(list)

        for gate_name, gate_result in gate_results.items():
            for error in gate_result.get("errors", []):
                file_path = error.get("file", "unknown")
                errors_by_file[file_path].append(
                    {
                        "gate": gate_name,
                        "line": error.get("line", 0),
                        "column": error.get("column", 0),
                        "message": error.get("message", ""),
                        "rule": error.get("rule", ""),
                        "severity": error.get("severity", "error"),
                    }
                )

        for file_path in errors_by_file:
            errors_by_file[file_path].sort(key=lambda e: (e["line"], e["column"]))

        return dict(errors_by_file)

    def _compute_summary_statistics(self, gate_results: dict[str, Any]) -> dict[str, Any]:
        """Compute comprehensive summary statistics for the QA report."""
        gates_passed = sum(1 for r in gate_results.values() if r.get("passed", False))
        gates_failed = len(gate_results) - gates_passed
        total_duration = sum(r.get("duration_seconds", 0) for r in gate_results.values())
        total_errors = sum(len(r.get("errors", [])) for r in gate_results.values())
        total_warnings = sum(len(r.get("warnings", [])) for r in gate_results.values())

        tests_run = 0
        tests_passed = 0
        tests_failed = 0
        for gate_result in gate_results.values():
            tests_run += gate_result.get("tests_run", 0)
            tests_passed += gate_result.get("tests_passed", 0)
            tests_failed += gate_result.get("tests_failed", 0)

        errors_by_gate: dict[str, int] = {}
        for gate_name, gate_result in gate_results.items():
            error_count = len(gate_result.get("errors", []))
            if error_count > 0:
                errors_by_gate[gate_name] = error_count

        files_with_errors: set = set()
        for gate_result in gate_results.values():
            for error in gate_result.get("errors", []):
                file_path = error.get("file")
                if file_path:
                    files_with_errors.add(file_path)

        return {
            "gates_passed": gates_passed,
            "gates_failed": gates_failed,
            "gates_total": len(gate_results),
            "total_duration_seconds": round(total_duration, 2),
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "errors_by_gate": errors_by_gate,
            "files_with_errors": len(files_with_errors),
            "tests_run": tests_run,
            "tests_passed": tests_passed,
            "tests_failed": tests_failed,
        }

    def update_feature_status(self, feature_id: int, passed: bool, qa_report_path: str) -> None:
        """Update feature status in feature_list.json with QA metadata."""
        feature_list_path = self.project_dir / "feature_list.json"

        if not feature_list_path.exists():
            print(f"Warning: feature_list.json not found at {feature_list_path}")
            return

        with open(feature_list_path) as f:
            features = json.load(f)

        feature_found = False
        for feature in features:
            if feature.get("id") == feature_id:
                feature["passes"] = passed
                feature["qa_validated"] = True
                feature["last_qa_run"] = (
                    datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                )
                feature["qa_notes"] = "All gates passed" if passed else "One or more gates failed"
                feature["qa_report_path"] = qa_report_path
                feature_found = True
                break

        if not feature_found:
            print(f"Warning: Feature #{feature_id} not found in feature_list.json")
            return

        atomic_write_json(feature_list_path, features)
        print(f"Updated feature #{feature_id} status: passes={passed}")

    def save_report(self, report: dict[str, Any]) -> Path:
        """Save QA report to file."""
        reports_dir = self.project_dir / "qa-reports"
        reports_dir.mkdir(exist_ok=True)

        feature_id = report["feature_id"]
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H-%M-%S")
        report_path = reports_dir / f"feature-{feature_id}-{timestamp}.json"

        atomic_write_json(report_path, report)
        print(f"QA report saved: {report_path}")

        return report_path

    def get_passing_features(self) -> list[dict[str, Any]]:
        """Query feature_list.json for all features with passes: true."""
        feature_list_path = self.project_dir / "feature_list.json"

        if not feature_list_path.exists():
            print(f"Warning: feature_list.json not found at {feature_list_path}")
            return []

        with open(feature_list_path) as f:
            features = json.load(f)

        return [f for f in features if f.get("passes", False)]

    def get_previous_report(self, feature_id: int) -> dict[str, Any] | None:
        """Get the most recent QA report for a feature."""
        reports_dir = self.project_dir / "qa-reports"
        if not reports_dir.exists():
            return None

        report_files = sorted(
            reports_dir.glob(f"feature-{feature_id}-*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        if not report_files:
            return None

        with open(report_files[0]) as f:
            return json.load(f)

    def detect_regressions(
        self,
        current_report: dict[str, Any],
        previous_report: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Compare current results with previous report to detect regressions."""
        if previous_report is None:
            return {
                "is_regression": False,
                "reason": "No previous report to compare",
                "new_failures": [],
                "fixed_issues": [],
            }

        prev_status = previous_report.get("overall_status", "FAILED")
        curr_status = current_report.get("overall_status", "FAILED")
        is_regression = prev_status == "PASSED" and curr_status == "FAILED"

        new_failures: list[dict[str, Any]] = []
        fixed_issues: list[dict[str, Any]] = []

        prev_gates = previous_report.get("gates", {})
        curr_gates = current_report.get("gates", {})

        for gate_name in curr_gates:
            prev_gate = prev_gates.get(gate_name, {})
            curr_gate = curr_gates.get(gate_name, {})
            prev_passed = prev_gate.get("passed", False)
            curr_passed = curr_gate.get("passed", False)

            if prev_passed and not curr_passed:
                new_failures.append(
                    {
                        "gate": gate_name,
                        "previous_status": "PASSED",
                        "current_status": "FAILED",
                        "errors": curr_gate.get("errors", []),
                    }
                )
            elif not prev_passed and curr_passed:
                fixed_issues.append(
                    {
                        "gate": gate_name,
                        "previous_status": "FAILED",
                        "current_status": "PASSED",
                    }
                )

        return {
            "is_regression": is_regression,
            "reason": "Previously passing feature now fails" if is_regression else None,
            "new_failures": new_failures,
            "fixed_issues": fixed_issues,
            "previous_report_timestamp": previous_report.get("timestamp"),
            "current_report_timestamp": current_report.get("timestamp"),
        }

    def run_git_blame(self, file_path: str, line_number: int) -> dict[str, str] | None:
        """Run git blame to identify which commit introduced a change."""
        try:
            result = subprocess.run(
                [
                    "git",
                    "blame",
                    "-L",
                    f"{line_number},{line_number}",
                    "--porcelain",
                    file_path,
                ],
                cwd=str(self.project_dir),
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                return None

            lines = result.stdout.strip().split("\n")
            if not lines:
                return None

            blame_info: dict[str, str] = {}
            commit_hash = None

            for line in lines:
                if not line:
                    continue
                if commit_hash is None and len(line) >= 40:
                    parts = line.split()
                    if parts:
                        commit_hash = parts[0][:8]
                        blame_info["commit"] = commit_hash
                elif line.startswith("author "):
                    blame_info["author"] = line[7:]
                elif line.startswith("author-mail "):
                    blame_info["author_email"] = line[12:].strip("<>")
                elif line.startswith("author-time "):
                    blame_info["author_time"] = line[12:]
                elif line.startswith("summary "):
                    blame_info["summary"] = line[8:]

            return blame_info if blame_info else None

        except (subprocess.TimeoutExpired, FileNotFoundError):
            return None

    def run_regression_suite(self) -> dict[str, Any]:
        """Run regression tests on all passing features."""
        print(f"\n{'=' * 70}")
        print("REGRESSION TEST SUITE")
        print(f"{'=' * 70}\n")

        passing_features = self.get_passing_features()

        if not passing_features:
            print("No passing features found to test for regressions.")
            return {
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "features_tested": 0,
                "regressions_found": 0,
                "features": [],
            }

        print(f"Testing {len(passing_features)} passing feature(s) for regressions...\n")

        results: list[dict[str, Any]] = []
        regressions_found = 0

        for feature in passing_features:
            feature_id = feature.get("id")
            feature_desc = feature.get("description", "")

            print(f"\n--- Testing Feature #{feature_id}: {feature_desc[:50]}...")

            previous_report = self.get_previous_report(feature_id)
            current_report = self.run_quality_gates(feature_id, feature_desc)
            regression_analysis = self.detect_regressions(current_report, previous_report)

            if regression_analysis["is_regression"]:
                regressions_found += 1
                print(f"\n  ⚠️  REGRESSION DETECTED in Feature #{feature_id}!")

                for failure in regression_analysis["new_failures"]:
                    for error in failure.get("errors", []):
                        file_path = error.get("file")
                        line_number = error.get("line", 0)
                        if file_path and line_number > 0:
                            blame_info = self.run_git_blame(file_path, line_number)
                            if blame_info:
                                error["git_blame"] = blame_info
                                print(
                                    f"    Blame: {blame_info.get('commit', 'unknown')} "
                                    f"by {blame_info.get('author', 'unknown')} - "
                                    f"{blame_info.get('summary', '')[:50]}"
                                )

                report_path = self.save_report(current_report)
                self.update_feature_status(
                    feature_id, passed=False, qa_report_path=str(report_path)
                )
            else:
                print(f"  ✓ Feature #{feature_id} still passes")

            results.append(
                {
                    "feature_id": feature_id,
                    "feature_description": feature_desc,
                    "regression_analysis": regression_analysis,
                    "current_report": current_report,
                }
            )

        suite_report = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "features_tested": len(passing_features),
            "regressions_found": regressions_found,
            "features": results,
        }

        print(f"\n{'=' * 70}")
        print("REGRESSION SUITE SUMMARY")
        print(f"{'=' * 70}")
        print(f"Features tested: {len(passing_features)}")
        print(f"Regressions found: {regressions_found}")

        if regressions_found > 0:
            print("\nRegressed features:")
            for result in results:
                if result["regression_analysis"]["is_regression"]:
                    print(
                        f"  - Feature #{result['feature_id']}: {result['feature_description'][:50]}"
                    )

        print(f"{'=' * 70}\n")

        reports_dir = self.project_dir / "qa-reports"
        reports_dir.mkdir(exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H-%M-%S")
        suite_report_path = reports_dir / f"regression-suite-{timestamp}.json"
        atomic_write_json(suite_report_path, suite_report)
        print(f"Regression suite report saved: {suite_report_path}")

        return suite_report

    def generate_summary_report(self) -> dict[str, Any]:
        """Generate a summary report across all features."""
        print(f"\n{'=' * 70}")
        print("GENERATING SUMMARY REPORT")
        print(f"{'=' * 70}\n")

        feature_list_path = self.project_dir / "feature_list.json"
        if not feature_list_path.exists():
            return {
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "error": "feature_list.json not found",
            }

        with open(feature_list_path) as f:
            features = json.load(f)

        category_stats = self._aggregate_category_stats(features)
        coverage = self._calculate_coverage_metrics(features)
        trends = self._get_historical_trends()

        summary_report: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "qa_agent_version": self.VERSION,
            "features": {
                "total": len(features),
                "passing": sum(1 for f in features if f.get("passes", False)),
                "failing": sum(1 for f in features if not f.get("passes", False)),
                "qa_validated": sum(1 for f in features if f.get("qa_validated", False)),
                "not_validated": sum(1 for f in features if not f.get("qa_validated", False)),
            },
            "category_stats": category_stats,
            "coverage": coverage,
            "trends": trends,
            "feature_details": [
                {
                    "id": f.get("id"),
                    "description": f.get("description", "")[:100],
                    "passes": f.get("passes", False),
                    "qa_validated": f.get("qa_validated", False),
                    "last_qa_run": f.get("last_qa_run"),
                }
                for f in features
            ],
        }

        markdown_report = self._generate_markdown_report(summary_report)

        reports_dir = self.project_dir / "qa-reports"
        reports_dir.mkdir(exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H-%M-%S")

        json_path = reports_dir / f"summary-{timestamp}.json"
        atomic_write_json(json_path, summary_report)
        print(f"Summary report (JSON) saved: {json_path}")

        md_path = reports_dir / f"summary-{timestamp}.md"
        with open(md_path, "w") as f:
            f.write(markdown_report)
        print(f"Summary report (Markdown) saved: {md_path}")

        return summary_report

    def _aggregate_category_stats(self, features: list[dict[str, Any]]) -> dict[str, Any]:
        """Aggregate pass/fail counts by category."""
        stats: dict[str, dict[str, int]] = {
            "lint": {"passed": 0, "failed": 0, "total_errors": 0},
            "type_check": {"passed": 0, "failed": 0, "total_errors": 0},
            "unit_tests": {"passed": 0, "failed": 0, "total_errors": 0},
            "browser_automation": {"passed": 0, "failed": 0, "total_errors": 0},
            "story_validation": {"passed": 0, "failed": 0, "total_errors": 0},
        }

        reports_dir = self.project_dir / "qa-reports"
        if not reports_dir.exists():
            return stats

        for feature in features:
            feature_id = feature.get("id")
            if feature_id is None:
                continue

            report = self.get_previous_report(feature_id)
            if report is None:
                continue

            gates = report.get("gates", {})
            for gate_name in stats:
                gate_result = gates.get(gate_name, {})
                if gate_result.get("passed", False):
                    stats[gate_name]["passed"] += 1
                else:
                    stats[gate_name]["failed"] += 1
                    stats[gate_name]["total_errors"] += len(gate_result.get("errors", []))

        return stats

    def _calculate_coverage_metrics(self, features: list[dict[str, Any]]) -> dict[str, Any]:
        """Calculate test coverage metrics."""
        total = len(features)
        if total == 0:
            return {
                "overall_pass_rate": 0.0,
                "validation_rate": 0.0,
                "features_passing": 0,
                "features_validated": 0,
            }

        passing = sum(1 for f in features if f.get("passes", False))
        validated = sum(1 for f in features if f.get("qa_validated", False))

        return {
            "overall_pass_rate": round((passing / total) * 100, 1),
            "validation_rate": round((validated / total) * 100, 1),
            "features_passing": passing,
            "features_validated": validated,
            "features_total": total,
        }

    def _get_historical_trends(self) -> dict[str, Any]:
        """Get historical trend data from previous reports."""
        reports_dir = self.project_dir / "qa-reports"
        if not reports_dir.exists():
            return {"history": [], "trend": "unknown"}

        summary_files = sorted(
            reports_dir.glob("summary-*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        history: list[dict[str, Any]] = []
        for summary_file in summary_files[:10]:
            try:
                with open(summary_file) as f:
                    data = json.load(f)
                history.append(
                    {
                        "timestamp": data.get("timestamp"),
                        "pass_rate": data.get("coverage", {}).get("overall_pass_rate", 0),
                        "features_passing": data.get("features", {}).get("passing", 0),
                        "features_total": data.get("features", {}).get("total", 0),
                    }
                )
            except (json.JSONDecodeError, KeyError):
                continue

        trend = "stable"
        if len(history) >= 2:
            recent_rate = history[0].get("pass_rate", 0)
            older_rate = history[-1].get("pass_rate", 0)
            if recent_rate > older_rate:
                trend = "improving"
            elif recent_rate < older_rate:
                trend = "declining"

        return {
            "history": history,
            "trend": trend,
            "reports_analyzed": len(history),
        }

    def _generate_markdown_report(self, summary: dict[str, Any]) -> str:
        """Generate a Markdown summary report."""
        lines: list[str] = []
        lines.append("# QA Summary Report")
        lines.append("")
        lines.append(f"**Generated:** {summary.get('timestamp', 'Unknown')}")
        lines.append(f"**QA Agent Version:** {summary.get('qa_agent_version', 'Unknown')}")
        lines.append("")

        lines.append("## Overview")
        lines.append("")
        features = summary.get("features", {})
        lines.append(f"- **Total Features:** {features.get('total', 0)}")
        lines.append(f"- **Passing:** {features.get('passing', 0)}")
        lines.append(f"- **Failing:** {features.get('failing', 0)}")
        lines.append(f"- **QA Validated:** {features.get('qa_validated', 0)}")
        lines.append("")

        coverage = summary.get("coverage", {})
        lines.append("## Coverage Metrics")
        lines.append("")
        lines.append(f"- **Pass Rate:** {coverage.get('overall_pass_rate', 0)}%")
        lines.append(f"- **Validation Rate:** {coverage.get('validation_rate', 0)}%")
        lines.append("")

        pass_rate = coverage.get("overall_pass_rate", 0)
        lines.append("### Pass Rate Progress")
        lines.append("")
        lines.append(self._generate_ascii_progress_bar(pass_rate))
        lines.append("")

        lines.append("## Gate Statistics")
        lines.append("")
        lines.append("| Gate | Passed | Failed | Errors |")
        lines.append("|------|--------|--------|--------|")
        for gate_name, stats in summary.get("category_stats", {}).items():
            lines.append(
                f"| {gate_name} | {stats.get('passed', 0)} | "
                f"{stats.get('failed', 0)} | {stats.get('total_errors', 0)} |"
            )
        lines.append("")

        trends = summary.get("trends", {})
        if trends.get("history"):
            lines.append("## Quality Trends")
            lines.append("")
            lines.append(f"**Trend:** {trends.get('trend', 'unknown').upper()}")
            lines.append("")
            lines.append("### Historical Pass Rates")
            lines.append("")
            lines.append(self._generate_ascii_trend_chart(trends.get("history", [])))
            lines.append("")

        lines.append("## Feature Details")
        lines.append("")
        lines.append("| ID | Description | Status | QA Validated | Last Run |")
        lines.append("|----|-------------|--------|--------------|----------|")
        for detail in summary.get("feature_details", []):
            status = "PASS" if detail.get("passes") else "FAIL"
            validated = "Yes" if detail.get("qa_validated") else "No"
            last_run = detail.get("last_qa_run", "Never")
            if last_run and len(last_run) > 10:
                last_run = last_run[:10]
            lines.append(
                f"| {detail.get('id', '?')} | {detail.get('description', '')[:40]} | "
                f"{status} | {validated} | {last_run} |"
            )
        lines.append("")

        lines.append("---")
        lines.append("")
        lines.append("*Report generated by QA Agent*")

        return "\n".join(lines)

    def _generate_ascii_progress_bar(self, percentage: float, width: int = 40) -> str:
        """Generate an ASCII progress bar."""
        filled = int(width * percentage / 100)
        empty = width - filled
        bar = "█" * filled + "░" * empty
        return f"```\n[{bar}] {percentage}%\n```"

    def _generate_ascii_trend_chart(self, history: list[dict[str, Any]], height: int = 10) -> str:
        """Generate an ASCII trend chart for pass rates."""
        if not history:
            return "No historical data available."

        rates = [h.get("pass_rate", 0) for h in reversed(history)]

        if not rates:
            return "No pass rate data available."

        max_rate = max(rates) if rates else 100
        min_rate = min(rates) if rates else 0
        rate_range = max(max_rate - min_rate, 1)

        lines = ["```"]

        for row in range(height, 0, -1):
            threshold = min_rate + (rate_range * row / height)
            line = f"{int(threshold):3d}% |"
            for rate in rates:
                if rate >= threshold:
                    line += "█"
                else:
                    line += " "
            lines.append(line)

        lines.append("     +" + "-" * len(rates))
        lines.append("      " + "".join(str(i % 10) for i in range(len(rates))))
        lines.append("```")

        return "\n".join(lines)


__all__ = ["QAAgent", "validate_qa_report"]
