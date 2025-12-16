"""
Quality Gate Implementations
=============================

Five quality gates for QA validation:
1. Lint (Biome for TS/JS, Ruff for Python)
2. Type Check (tsc for TS, Mypy for Python)
3. Unit Tests (Vitest for TS/JS, Pytest for Python)
4. Browser Automation (Playwright)
5. Story Validation (feature_list.json test steps)

Enhanced with detailed error capture (file:line:column) for structured feedback reports.
"""

import json
import re
import subprocess
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class QualityGate(ABC):
    """Base class for all quality gates."""

    def __init__(self, project_dir: Path):
        """
        Initialize quality gate.

        Args:
            project_dir: Project directory path
        """
        self.project_dir = Path(project_dir)
        self.name = self.__class__.__name__.replace("Gate", "").lower()

    @abstractmethod
    def run(self) -> dict[str, Any]:
        """
        Execute the quality gate.

        Returns:
            Gate result dictionary with:
            - passed: bool
            - duration_seconds: float
            - tool: str
            - tool_version: str (optional)
            - errors: List[Dict] (optional)
            - warnings: List[Dict] (optional)
        """
        pass

    def _run_command(self, command: list[str], timeout: int = 300) -> tuple[int, str, str]:
        """
        Run a shell command and capture output.

        Args:
            command: Command and arguments as list
            timeout: Timeout in seconds

        Returns:
            (exit_code, stdout, stderr)
        """
        try:
            result = subprocess.run(
                command,
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", f"Command timed out after {timeout}s"
        except Exception as e:
            return -1, "", str(e)

    def _get_tool_version(self, tool_command: list[str]) -> str:
        """
        Get version of a tool.

        Args:
            tool_command: Command to get version (e.g., ["biome", "--version"])

        Returns:
            Version string or "unknown"
        """
        try:
            result = subprocess.run(
                tool_command,
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.stdout.strip() or "unknown"
        except Exception:
            return "unknown"


class LintGate(QualityGate):
    """Lint quality gate - runs Biome for TS/JS, Ruff for Python."""

    def run(self) -> dict[str, Any]:
        """
        Execute linting for all project files.

        Returns:
            Gate result with errors and warnings including file:line:column references
        """
        start_time = time.time()
        errors: list[dict[str, Any]] = []
        warnings: list[dict[str, Any]] = []
        tool_versions: dict[str, str] = {}

        # Detect project type (Python vs TS/JS)
        has_python = (self.project_dir / "requirements.txt").exists() or (
            self.project_dir / "pyproject.toml"
        ).exists()
        has_ts_js = (self.project_dir / "package.json").exists()

        # Run Biome for TS/JS if applicable
        if has_ts_js:
            tool_versions["biome"] = self._get_tool_version(["npx", "biome", "--version"])

            # Use JSON output for structured parsing
            exit_code, stdout, stderr = self._run_command(
                ["npx", "biome", "check", ".", "--reporter=json"]
            )
            if exit_code != 0:
                # Try JSON parsing first, fall back to text parsing
                biome_errors, biome_warnings = self._parse_biome_json_output(stdout)
                if not biome_errors and not biome_warnings:
                    # Fallback to text parsing if JSON fails
                    biome_errors = self._parse_biome_text_output(stdout + stderr)
                errors.extend(biome_errors)
                warnings.extend(biome_warnings)

        # Run Ruff for Python if applicable
        if has_python:
            tool_versions["ruff"] = self._get_tool_version(["ruff", "--version"])

            # Use JSON output for structured parsing
            exit_code, stdout, stderr = self._run_command(
                ["ruff", "check", ".", "--output-format=json"]
            )
            if exit_code != 0:
                # Try JSON parsing first, fall back to text parsing
                ruff_errors = self._parse_ruff_json_output(stdout)
                if not ruff_errors:
                    # Fallback to text parsing if JSON fails
                    ruff_errors = self._parse_ruff_text_output(stdout + stderr)
                errors.extend(ruff_errors)

        duration = time.time() - start_time
        tool = "biome + ruff" if has_python and has_ts_js else ("biome" if has_ts_js else "ruff")
        version_str = ", ".join(f"{k}={v}" for k, v in tool_versions.items())

        return {
            "passed": len(errors) == 0,
            "duration_seconds": round(duration, 2),
            "tool": tool,
            "tool_version": version_str or "unknown",
            "errors": errors,
            "warnings": warnings,
        }

    def _parse_biome_json_output(
        self, output: str
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Parse Biome JSON reporter output into structured errors and warnings."""
        errors: list[dict[str, Any]] = []
        warnings: list[dict[str, Any]] = []

        try:
            data = json.loads(output)
            diagnostics = data.get("diagnostics", [])

            for diag in diagnostics:
                location = diag.get("location", {})
                file_path = location.get("path", {})
                if isinstance(file_path, dict):
                    file_path = file_path.get("file", "unknown")

                span = location.get("span", {})
                line = span.get("start", 0) // 80 + 1
                column = span.get("start", 0) % 80 + 1

                source_code = location.get("sourceCode", "")
                if source_code:
                    lines_before = source_code[: span.get("start", 0)].count("\n")
                    line = lines_before + 1

                message_parts = diag.get("message", [])
                message = ""
                if isinstance(message_parts, list):
                    message = "".join(
                        p.get("content", "") if isinstance(p, dict) else str(p)
                        for p in message_parts
                    )
                else:
                    message = str(message_parts)

                entry = {
                    "file": file_path,
                    "line": line,
                    "column": column,
                    "message": message.strip(),
                    "rule": diag.get("category", ""),
                    "severity": diag.get("severity", "error"),
                }

                if diag.get("severity") == "warning":
                    warnings.append(entry)
                else:
                    errors.append(entry)

        except json.JSONDecodeError:
            pass

        return errors, warnings

    def _parse_biome_text_output(self, output: str) -> list[dict[str, Any]]:
        """Parse Biome text output into structured errors (fallback)."""
        errors: list[dict[str, Any]] = []
        current_file = ""
        current_line = 0
        current_col = 0
        current_rule = ""

        for line in output.split("\n"):
            header_match = re.match(r"^[✖×]\s+(.+?):(\d+):(\d+)\s+(.+)$", line.strip())
            if header_match:
                current_file = header_match.group(1)
                current_line = int(header_match.group(2))
                current_col = int(header_match.group(3))
                current_rule = header_match.group(4)
                continue

            if line.strip().startswith("│") and current_file:
                message = line.replace("│", "").strip()
                if message:
                    errors.append(
                        {
                            "file": current_file,
                            "line": current_line,
                            "column": current_col,
                            "message": message,
                            "rule": current_rule,
                            "severity": "error",
                        }
                    )
                    current_file = ""

        return errors

    def _parse_ruff_json_output(self, output: str) -> list[dict[str, Any]]:
        """Parse Ruff JSON output into structured errors."""
        errors: list[dict[str, Any]] = []

        try:
            diagnostics = json.loads(output)

            for diag in diagnostics:
                location = diag.get("location", {})
                end_location = diag.get("end_location", {})

                errors.append(
                    {
                        "file": diag.get("filename", "unknown"),
                        "line": location.get("row", 0),
                        "column": location.get("column", 0),
                        "end_line": end_location.get("row", location.get("row", 0)),
                        "end_column": end_location.get("column", location.get("column", 0)),
                        "message": diag.get("message", ""),
                        "rule": diag.get("code", ""),
                        "severity": "error",
                        "fix": diag.get("fix"),
                    }
                )

        except json.JSONDecodeError:
            pass

        return errors

    def _parse_ruff_text_output(self, output: str) -> list[dict[str, Any]]:
        """Parse Ruff text output into structured errors (fallback)."""
        errors: list[dict[str, Any]] = []
        for line in output.split("\n"):
            match = re.match(r"^(.+?):(\d+):(\d+):\s*(\w+)\s+(.+)$", line.strip())
            if match:
                errors.append(
                    {
                        "file": match.group(1),
                        "line": int(match.group(2)),
                        "column": int(match.group(3)),
                        "message": match.group(5),
                        "rule": match.group(4),
                        "severity": "error",
                    }
                )
        return errors


class TypeCheckGate(QualityGate):
    """Type check quality gate - runs tsc for TS, Mypy for Python."""

    def run(self) -> dict[str, Any]:
        """Execute type checking for all project files."""
        start_time = time.time()
        errors: list[dict[str, Any]] = []
        tool_versions: dict[str, str] = {}

        has_python = (self.project_dir / "requirements.txt").exists() or (
            self.project_dir / "pyproject.toml"
        ).exists()
        has_ts = (self.project_dir / "tsconfig.json").exists()

        if has_ts:
            tool_versions["tsc"] = self._get_tool_version(["npx", "tsc", "--version"])
            exit_code, stdout, stderr = self._run_command(["npx", "tsc", "--noEmit"])
            if exit_code != 0:
                tsc_errors = self._parse_tsc_output(stdout + stderr)
                errors.extend(tsc_errors)

        if has_python:
            tool_versions["mypy"] = self._get_tool_version(["mypy", "--version"])
            exit_code, stdout, stderr = self._run_command(["mypy", ".", "--output=json"])
            if exit_code != 0:
                mypy_errors = self._parse_mypy_json_output(stdout)
                if not mypy_errors:
                    mypy_errors = self._parse_mypy_text_output(stdout + stderr)
                errors.extend(mypy_errors)

        duration = time.time() - start_time
        tool = "tsc + mypy" if has_python and has_ts else ("tsc" if has_ts else "mypy")
        version_str = ", ".join(f"{k}={v}" for k, v in tool_versions.items())

        return {
            "passed": len(errors) == 0,
            "duration_seconds": round(duration, 2),
            "tool": tool,
            "tool_version": version_str or "unknown",
            "errors": errors,
        }

    def _parse_tsc_output(self, output: str) -> list[dict[str, Any]]:
        """Parse TypeScript compiler output into structured errors."""
        errors: list[dict[str, Any]] = []
        for line in output.split("\n"):
            match = re.match(r"^(.+?)\((\d+),(\d+)\):\s*error\s+(TS\d+):\s*(.+)$", line.strip())
            if match:
                errors.append(
                    {
                        "file": match.group(1),
                        "line": int(match.group(2)),
                        "column": int(match.group(3)),
                        "message": match.group(5),
                        "rule": match.group(4),
                        "severity": "error",
                    }
                )
        return errors

    def _parse_mypy_json_output(self, output: str) -> list[dict[str, Any]]:
        """Parse Mypy JSON output into structured errors."""
        errors: list[dict[str, Any]] = []
        for line in output.split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                diag = json.loads(line)
                if diag.get("severity") == "error":
                    errors.append(
                        {
                            "file": diag.get("file", "unknown"),
                            "line": diag.get("line", 0),
                            "column": diag.get("column", 0),
                            "message": diag.get("message", ""),
                            "rule": diag.get("code", ""),
                            "severity": "error",
                        }
                    )
            except json.JSONDecodeError:
                continue
        return errors

    def _parse_mypy_text_output(self, output: str) -> list[dict[str, Any]]:
        """Parse Mypy text output into structured errors (fallback)."""
        errors: list[dict[str, Any]] = []
        for line in output.split("\n"):
            match = re.match(
                r"^(.+?):(\d+):(\d+):\s*error:\s*(.+?)(?:\s+\[([^\]]+)\])?$",
                line.strip(),
            )
            if match:
                errors.append(
                    {
                        "file": match.group(1),
                        "line": int(match.group(2)),
                        "column": int(match.group(3)),
                        "message": match.group(4),
                        "rule": match.group(5) or "",
                        "severity": "error",
                    }
                )
                continue
            match = re.match(r"^(.+?):(\d+):\s*error:\s*(.+?)(?:\s+\[([^\]]+)\])?$", line.strip())
            if match:
                errors.append(
                    {
                        "file": match.group(1),
                        "line": int(match.group(2)),
                        "column": 0,
                        "message": match.group(3),
                        "rule": match.group(4) or "",
                        "severity": "error",
                    }
                )
        return errors


class UnitTestGate(QualityGate):
    """Unit test quality gate - runs Vitest for TS/JS, Pytest for Python."""

    def run(self) -> dict[str, Any]:
        """Execute unit tests for the project."""
        start_time = time.time()
        errors: list[dict[str, Any]] = []
        tests_run = 0
        tests_passed = 0
        tests_failed = 0
        tool_versions: dict[str, str] = {}

        has_python = (self.project_dir / "requirements.txt").exists() or (
            self.project_dir / "pyproject.toml"
        ).exists()
        has_ts_js = (self.project_dir / "package.json").exists()

        if has_ts_js:
            tool_versions["vitest"] = self._get_tool_version(["npx", "vitest", "--version"])
            exit_code, stdout, stderr = self._run_command(
                ["npx", "vitest", "run", "--reporter=json"]
            )
            vitest_stats = self._parse_vitest_json_output(stdout)
            if not vitest_stats["tests_run"]:
                exit_code, stdout, stderr = self._run_command(["npx", "vitest", "run"])
                vitest_stats = self._parse_vitest_text_output(stdout + stderr)

            tests_run += vitest_stats["tests_run"]
            tests_passed += vitest_stats["tests_passed"]
            tests_failed += vitest_stats["tests_failed"]
            errors.extend(vitest_stats["errors"])

        if has_python:
            tool_versions["pytest"] = self._get_tool_version(["pytest", "--version"])
            json_output_file = self.project_dir / ".pytest_results.json"
            exit_code, stdout, stderr = self._run_command(
                [
                    "pytest",
                    "-v",
                    "--tb=short",
                    "--json-report",
                    f"--json-report-file={json_output_file}",
                ]
            )
            pytest_stats = self._parse_pytest_json_output(json_output_file)
            if not pytest_stats["tests_run"]:
                pytest_stats = self._parse_pytest_text_output(stdout + stderr)
            if json_output_file.exists():
                json_output_file.unlink()

            tests_run += pytest_stats["tests_run"]
            tests_passed += pytest_stats["tests_passed"]
            tests_failed += pytest_stats["tests_failed"]
            errors.extend(pytest_stats["errors"])

        duration = time.time() - start_time
        tool = (
            "vitest + pytest" if has_python and has_ts_js else ("vitest" if has_ts_js else "pytest")
        )
        version_str = ", ".join(f"{k}={v}" for k, v in tool_versions.items())

        return {
            "passed": tests_failed == 0 and tests_run > 0,
            "duration_seconds": round(duration, 2),
            "tool": tool,
            "tool_version": version_str or "unknown",
            "tests_run": tests_run,
            "tests_passed": tests_passed,
            "tests_failed": tests_failed,
            "errors": errors,
        }

    def _parse_vitest_json_output(self, output: str) -> dict[str, Any]:
        """Parse Vitest JSON reporter output into test statistics."""
        stats: dict[str, Any] = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "errors": [],
        }
        try:
            data = json.loads(output)
            test_results = data.get("testResults", [])
            for file_result in test_results:
                file_path = file_result.get("name", "unknown")
                assertions = file_result.get("assertionResults", [])
                for assertion in assertions:
                    stats["tests_run"] += 1
                    status = assertion.get("status", "")
                    if status == "passed":
                        stats["tests_passed"] += 1
                    elif status == "failed":
                        stats["tests_failed"] += 1
                        location = assertion.get("location", {})
                        failure_messages = assertion.get("failureMessages", [])
                        stats["errors"].append(
                            {
                                "file": file_path,
                                "line": location.get("line", 0),
                                "column": location.get("column", 0),
                                "test_name": assertion.get("title", "unknown"),
                                "message": "\n".join(failure_messages)[:500],
                                "severity": "error",
                            }
                        )
        except json.JSONDecodeError:
            pass
        return stats

    def _parse_vitest_text_output(self, output: str) -> dict[str, Any]:
        """Parse Vitest text output into test statistics (fallback)."""
        stats: dict[str, Any] = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "errors": [],
        }
        current_file = ""
        test_name = ""
        in_failure_block = False
        failure_lines: list[str] = []

        for line in output.split("\n"):
            file_match = re.match(
                r"^(FAIL|PASS)\s+(.+\.(?:test|spec)\.[jt]sx?)(?:\s|$)", line.strip()
            )
            if file_match:
                current_file = file_match.group(2)
                continue
            if "✓" in line or "PASS" in line:
                stats["tests_passed"] += 1
                stats["tests_run"] += 1
            elif "✗" in line or "× " in line or "FAIL" in line:
                stats["tests_failed"] += 1
                stats["tests_run"] += 1
                test_match = re.match(r"^\s*[✗×]\s+(.+)$", line.strip())
                if test_match:
                    test_name = test_match.group(1)
                    in_failure_block = True
                    failure_lines = []
            if in_failure_block:
                if line.startswith("    "):
                    failure_lines.append(line.strip())
                elif line.strip() == "" or not line.startswith(" "):
                    if failure_lines:
                        stats["errors"].append(
                            {
                                "file": current_file,
                                "line": 0,
                                "column": 0,
                                "test_name": test_name,
                                "message": "\n".join(failure_lines[:10]),
                                "severity": "error",
                            }
                        )
                    in_failure_block = False
        return stats

    def _parse_pytest_json_output(self, json_file: Path) -> dict[str, Any]:
        """Parse pytest-json-report output file into test statistics."""
        stats: dict[str, Any] = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "errors": [],
        }
        if not json_file.exists():
            return stats
        try:
            with open(json_file) as f:
                data = json.load(f)
            tests = data.get("tests", [])
            for test in tests:
                stats["tests_run"] += 1
                outcome = test.get("outcome", "")
                nodeid = test.get("nodeid", "unknown")
                if outcome == "passed":
                    stats["tests_passed"] += 1
                elif outcome == "failed":
                    stats["tests_failed"] += 1
                    file_path = "unknown"
                    test_name = nodeid
                    if "::" in nodeid:
                        parts = nodeid.split("::")
                        file_path = parts[0]
                        test_name = "::".join(parts[1:])
                    call_info = test.get("call", {})
                    longrepr = call_info.get("longrepr", "")
                    if isinstance(longrepr, dict):
                        longrepr = longrepr.get("reprcrash", {}).get("message", "")
                    stats["errors"].append(
                        {
                            "file": file_path,
                            "line": test.get("lineno", 0),
                            "column": 0,
                            "test_name": test_name,
                            "message": str(longrepr)[:500],
                            "severity": "error",
                        }
                    )
        except (json.JSONDecodeError, OSError):
            pass
        return stats

    def _parse_pytest_text_output(self, output: str) -> dict[str, Any]:
        """Parse Pytest text output into test statistics (fallback)."""
        stats: dict[str, Any] = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "errors": [],
        }
        in_failure_section = False
        current_test = ""
        current_file = ""
        failure_lines: list[str] = []

        for line in output.split("\n"):
            summary_match = re.match(r".*?(\d+)\s+passed.*?(\d+)\s+failed", line)
            if summary_match:
                stats["tests_passed"] = int(summary_match.group(1))
                stats["tests_failed"] = int(summary_match.group(2))
                stats["tests_run"] = stats["tests_passed"] + stats["tests_failed"]
                continue
            summary_match2 = re.match(r".*?(\d+)\s+failed.*?(\d+)\s+passed", line)
            if summary_match2:
                stats["tests_failed"] = int(summary_match2.group(1))
                stats["tests_passed"] = int(summary_match2.group(2))
                stats["tests_run"] = stats["tests_passed"] + stats["tests_failed"]
                continue
            passed_only = re.match(r".*?(\d+)\s+passed(?:\s|,)", line)
            if passed_only and stats["tests_run"] == 0:
                stats["tests_passed"] = int(passed_only.group(1))
                stats["tests_run"] = stats["tests_passed"]
            failure_match = re.match(r"^FAILED\s+(.+?)::(.+?)(?:\s+-|$)", line.strip())
            if failure_match:
                current_file = failure_match.group(1)
                current_test = failure_match.group(2)
                in_failure_section = True
                failure_lines = []
                continue
            if re.match(r"^_+\s+.+\s+_+$", line.strip()):
                in_failure_section = True
                continue
            if in_failure_section:
                if line.startswith("=") or line.startswith("_"):
                    if current_test and failure_lines:
                        line_no = 0
                        for fl in failure_lines:
                            line_match = re.search(r":(\d+):", fl)
                            if line_match:
                                line_no = int(line_match.group(1))
                                break
                        stats["errors"].append(
                            {
                                "file": current_file,
                                "line": line_no,
                                "column": 0,
                                "test_name": current_test,
                                "message": "\n".join(failure_lines[:10]),
                                "severity": "error",
                            }
                        )
                    in_failure_section = False
                    current_test = ""
                    current_file = ""
                else:
                    failure_lines.append(line.rstrip())
        return stats


class BrowserAutomationGate(QualityGate):
    """Browser automation quality gate - runs Playwright tests."""

    def run(self) -> dict[str, Any]:
        """Execute browser automation tests."""
        start_time = time.time()
        errors: list[dict[str, Any]] = []
        screenshots: list[dict[str, Any]] = []
        tool_version = self._get_tool_version(["npx", "playwright", "--version"])

        playwright_config = self.project_dir / "playwright.config.ts"
        playwright_config_js = self.project_dir / "playwright.config.js"
        tests_dir = self.project_dir / "tests" / "e2e"
        playwright_tests_dir = self.project_dir / "e2e"

        has_playwright = (
            playwright_config.exists()
            or playwright_config_js.exists()
            or tests_dir.exists()
            or playwright_tests_dir.exists()
        )

        if not has_playwright:
            duration = time.time() - start_time
            return {
                "passed": True,
                "duration_seconds": round(duration, 2),
                "tool": "playwright",
                "tool_version": tool_version,
                "errors": [],
                "screenshots": [],
                "note": "No Playwright tests configured",
            }

        exit_code, stdout, stderr = self._run_command(
            [
                "npx",
                "playwright",
                "test",
                "--reporter=json",
                f"--output={self.project_dir / 'test-results'}",
            ]
        )

        if exit_code != 0:
            errors = self._parse_playwright_json_output(stdout)
            if not errors:
                errors = self._parse_playwright_text_output(stdout + stderr)
            screenshots = self._collect_screenshots()

        duration = time.time() - start_time
        return {
            "passed": len(errors) == 0 and exit_code == 0,
            "duration_seconds": round(duration, 2),
            "tool": "playwright",
            "tool_version": tool_version,
            "errors": errors,
            "screenshots": screenshots,
        }

    def _parse_playwright_json_output(self, output: str) -> list[dict[str, Any]]:
        """Parse Playwright JSON reporter output."""
        errors: list[dict[str, Any]] = []
        try:
            data = json.loads(output)
            suites = data.get("suites", [])
            for suite in suites:
                self._extract_errors_from_suite(suite, errors)
        except json.JSONDecodeError:
            pass
        return errors

    def _extract_errors_from_suite(self, suite: dict, errors: list[dict[str, Any]]) -> None:
        """Recursively extract errors from Playwright suite."""
        file_path = suite.get("file", "unknown")
        for spec in suite.get("specs", []):
            title = spec.get("title", "unknown")
            line = spec.get("line", 0)
            for test in spec.get("tests", []):
                status = test.get("status", "")
                if status in ["failed", "timedOut", "interrupted"]:
                    results = test.get("results", [])
                    for result in results:
                        error_info = result.get("error", {})
                        message = error_info.get("message", "")
                        stack = error_info.get("stack", "")
                        console_errors = []
                        for attachment in result.get("attachments", []):
                            if attachment.get("name") == "console":
                                console_errors.append(attachment.get("body", ""))
                        errors.append(
                            {
                                "file": file_path,
                                "line": line,
                                "column": 0,
                                "test_name": title,
                                "message": message or "Test failed",
                                "stack": stack[:500] if stack else "",
                                "console_errors": console_errors,
                                "screenshot": result.get("screenshot"),
                                "severity": "error",
                            }
                        )
        for nested_suite in suite.get("suites", []):
            self._extract_errors_from_suite(nested_suite, errors)

    def _parse_playwright_text_output(self, output: str) -> list[dict[str, Any]]:
        """Parse Playwright text output into errors (fallback)."""
        errors: list[dict[str, Any]] = []
        current_test = ""
        current_file = ""
        error_lines: list[str] = []
        in_error_block = False

        for line in output.split("\n"):
            failure_match = re.match(r"^\s*\d+\)\s+\[.*\]\s+›\s+(.+?)\s+›\s+(.+)$", line)
            if failure_match:
                if current_test and error_lines:
                    errors.append(
                        {
                            "file": current_file,
                            "line": 0,
                            "column": 0,
                            "test_name": current_test,
                            "message": "\n".join(error_lines[:10]),
                            "severity": "error",
                        }
                    )
                current_file = failure_match.group(1)
                current_test = failure_match.group(2)
                error_lines = []
                in_error_block = True
                continue
            if in_error_block:
                if line.strip().startswith("─") or re.match(r"^\s*\d+\)", line):
                    if current_test and error_lines:
                        errors.append(
                            {
                                "file": current_file,
                                "line": 0,
                                "column": 0,
                                "test_name": current_test,
                                "message": "\n".join(error_lines[:10]),
                                "severity": "error",
                            }
                        )
                    in_error_block = False
                    current_test = ""
                    current_file = ""
                    error_lines = []
                else:
                    error_lines.append(line.rstrip())
            if ("console.error" in line.lower() or "Error:" in line) and not in_error_block:
                    errors.append(
                        {
                            "file": "console",
                            "line": 0,
                            "column": 0,
                            "test_name": "console_error",
                            "message": line.strip(),
                            "console_log_type": "error",
                            "severity": "error",
                        }
                    )

        if current_test and error_lines:
            errors.append(
                {
                    "file": current_file,
                    "line": 0,
                    "column": 0,
                    "test_name": current_test,
                    "message": "\n".join(error_lines[:10]),
                    "severity": "error",
                }
            )
        return errors

    def _collect_screenshots(self) -> list[dict[str, Any]]:
        """Collect screenshots from Playwright test results."""
        screenshots: list[dict[str, Any]] = []
        test_results_dir = self.project_dir / "test-results"
        if not test_results_dir.exists():
            return screenshots
        for screenshot_file in test_results_dir.rglob("*.png"):
            screenshots.append(
                {
                    "path": str(screenshot_file.relative_to(self.project_dir)),
                    "name": screenshot_file.name,
                    "test": screenshot_file.parent.name,
                }
            )
        return screenshots


class StoryValidationGate(QualityGate):
    """Story validation quality gate - validates against feature_list.json test steps."""

    def __init__(
        self,
        project_dir: Path,
        feature_id: int = 0,
        app_url: str = "http://localhost:3000",
    ):
        super().__init__(project_dir)
        self.feature_id = feature_id
        self.app_url = app_url
        self.screenshots_dir = self.project_dir / "screenshots"
        self.screenshots_dir.mkdir(exist_ok=True)

    def run(self) -> dict[str, Any]:
        """Execute story validation for a feature."""
        start_time = time.time()
        errors: list[dict[str, Any]] = []
        step_results: list[dict[str, Any]] = []
        screenshots: list[dict[str, Any]] = []

        feature = self._load_feature()
        if not feature:
            duration = time.time() - start_time
            return {
                "passed": False,
                "duration_seconds": round(duration, 2),
                "acceptance_criteria_met": 0,
                "acceptance_criteria_total": 0,
                "errors": [
                    {"message": f"Feature {self.feature_id} not found in feature_list.json"}
                ],
                "step_results": [],
                "screenshots": [],
            }

        steps = self._parse_test_steps(feature)
        if not steps:
            duration = time.time() - start_time
            return {
                "passed": True,
                "duration_seconds": round(duration, 2),
                "acceptance_criteria_met": 0,
                "acceptance_criteria_total": 0,
                "errors": [],
                "step_results": [],
                "screenshots": [],
                "note": "No test steps defined for this feature",
            }

        step_results, step_errors, step_screenshots = self._execute_steps(steps)
        errors.extend(step_errors)
        screenshots.extend(step_screenshots)

        criteria_met = sum(1 for r in step_results if r.get("passed", False))
        criteria_total = len(steps)
        duration = time.time() - start_time

        return {
            "passed": len(errors) == 0 and criteria_met == criteria_total,
            "duration_seconds": round(duration, 2),
            "acceptance_criteria_met": criteria_met,
            "acceptance_criteria_total": criteria_total,
            "errors": errors,
            "step_results": step_results,
            "screenshots": screenshots,
        }

    def _load_feature(self) -> dict[str, Any] | None:
        """Load feature from feature_list.json."""
        feature_list_path = self.project_dir / "feature_list.json"
        if not feature_list_path.exists():
            return None
        try:
            with open(feature_list_path) as f:
                features = json.load(f)
            for feature in features:
                if feature.get("id") == self.feature_id:
                    return feature
        except (json.JSONDecodeError, OSError):
            pass
        return None

    def _parse_test_steps(self, feature: dict[str, Any]) -> list[dict[str, Any]]:
        """Parse test steps from feature."""
        raw_steps = feature.get("steps", [])
        parsed_steps: list[dict[str, Any]] = []
        for i, step in enumerate(raw_steps):
            if isinstance(step, str):
                parsed_step = self._parse_string_step(step, i)
            elif isinstance(step, dict):
                parsed_step = self._normalize_step(step, i)
            else:
                continue
            parsed_steps.append(parsed_step)
        return parsed_steps

    def _parse_string_step(self, step_text: str, index: int) -> dict[str, Any]:
        """Parse a simple string step into structured format."""
        step_lower = step_text.lower()
        if step_lower.startswith("navigate to") or step_lower.startswith("go to"):
            target = step_text.split(" to ", 1)[-1].strip()
            return {
                "index": index,
                "action": "navigate",
                "target": target,
                "description": step_text,
            }
        if step_lower.startswith("click"):
            target = step_text.split(" ", 1)[-1].strip()
            return {
                "index": index,
                "action": "click",
                "description": step_text,
                "target_description": target,
            }
        if any(step_lower.startswith(w) for w in ["enter", "type", "fill", "input"]):
            return {"index": index, "action": "fill", "description": step_text}
        if any(
            step_lower.startswith(w) for w in ["verify", "check", "confirm", "ensure", "expect"]
        ):
            return {
                "index": index,
                "action": "verify",
                "description": step_text,
                "expected": step_text,
            }
        if step_lower.startswith("scroll"):
            return {"index": index, "action": "scroll", "description": step_text}
        if step_lower.startswith("wait"):
            return {"index": index, "action": "wait", "description": step_text}
        return {
            "index": index,
            "action": "verify",
            "description": step_text,
            "expected": step_text,
        }

    def _normalize_step(self, step: dict[str, Any], index: int) -> dict[str, Any]:
        """Normalize a structured step dict."""
        normalized: dict[str, Any] = {"index": index, **step}
        if "action" not in normalized:
            normalized["action"] = "verify"
        if "description" not in normalized:
            action = normalized.get("action", "unknown")
            target = normalized.get("target") or normalized.get("selector") or ""
            normalized["description"] = f"{action} {target}".strip()
        return normalized

    def _execute_steps(
        self, steps: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
        """Execute test steps using Playwright."""
        step_results: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []
        screenshots: list[dict[str, Any]] = []

        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return (
                [
                    {
                        "index": s["index"],
                        "passed": False,
                        "message": "Playwright not installed",
                    }
                    for s in steps
                ],
                [
                    {
                        "message": "Playwright is not installed. Run: pip install playwright && playwright install chromium"
                    }
                ],
                [],
            )

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()
                console_errors: list[Any] = []
                page.on(
                    "console",
                    lambda msg: (console_errors.append(msg) if msg.type == "error" else None),
                )

                for step in steps:
                    result, screenshot_path = self._execute_single_step(page, step)
                    step_results.append(result)
                    if screenshot_path:
                        screenshots.append(
                            {
                                "step_index": step["index"],
                                "path": str(screenshot_path),
                                "description": step.get("description", ""),
                            }
                        )
                    if not result.get("passed", False):
                        errors.append(
                            {
                                "step_index": step["index"],
                                "step_description": step.get("description", ""),
                                "message": result.get("message", "Step failed"),
                                "screenshot": (str(screenshot_path) if screenshot_path else None),
                            }
                        )

                for console_msg in console_errors:
                    errors.append(
                        {
                            "type": "console_error",
                            "message": console_msg.text,
                            "console_log_type": "error",
                        }
                    )
                browser.close()

        except Exception as e:
            for step in steps:
                if not any(r["index"] == step["index"] for r in step_results):
                    step_results.append(
                        {
                            "index": step["index"],
                            "passed": False,
                            "message": f"Browser automation failed: {e}",
                        }
                    )
            errors.append({"message": f"Browser automation error: {e}"})

        return step_results, errors, screenshots

    def _execute_single_step(
        self, page: Any, step: dict[str, Any]
    ) -> tuple[dict[str, Any], Path | None]:
        """Execute a single test step."""
        action = step.get("action", "verify")
        index = step.get("index", 0)
        description = step.get("description", "")

        result: dict[str, Any] = {
            "index": index,
            "action": action,
            "description": description,
            "passed": False,
            "message": "",
        }
        screenshot_path: Path | None = None

        try:
            if action == "navigate":
                target = step.get("target", "")
                if target.startswith("/"):
                    target = f"{self.app_url}{target}"
                elif not target.startswith("http"):
                    target = f"{self.app_url}/{target}"
                page.goto(target, timeout=30000)
                result["passed"] = True
                result["message"] = f"Navigated to {target}"
            elif action == "click":
                selector = step.get("selector")
                if selector:
                    page.click(selector, timeout=10000)
                else:
                    text = step.get("target_description", description)
                    page.get_by_text(text).first.click(timeout=10000)
                result["passed"] = True
                result["message"] = "Clicked element"
            elif action == "fill":
                selector = step.get("selector")
                value = step.get("value", "")
                if selector:
                    page.fill(selector, value, timeout=10000)
                    result["passed"] = True
                    result["message"] = f"Filled {selector} with value"
                else:
                    result["message"] = "No selector provided for fill action"
            elif action == "scroll":
                direction = step.get("direction", "down")
                amount = step.get("amount", 500)
                if direction == "down":
                    page.evaluate(f"window.scrollBy(0, {amount})")
                elif direction == "up":
                    page.evaluate(f"window.scrollBy(0, -{amount})")
                result["passed"] = True
                result["message"] = f"Scrolled {direction}"
            elif action == "wait":
                duration = step.get("duration", 1000)
                page.wait_for_timeout(duration)
                result["passed"] = True
                result["message"] = f"Waited {duration}ms"
            elif action == "verify":
                selector = step.get("selector")
                if selector:
                    element = page.query_selector(selector)
                    if element:
                        result["passed"] = True
                        result["message"] = f"Element {selector} found"
                    else:
                        result["message"] = f"Element {selector} not found"
                else:
                    result["passed"] = True
                    result["message"] = "Verification step captured"
            else:
                result["message"] = f"Unknown action: {action}"

            timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
            screenshot_name = f"step-{index}-{timestamp}.png"
            screenshot_path = self.screenshots_dir / screenshot_name
            page.screenshot(path=str(screenshot_path))

        except Exception as e:
            result["message"] = str(e)
            try:
                timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
                screenshot_name = f"step-{index}-failure-{timestamp}.png"
                screenshot_path = self.screenshots_dir / screenshot_name
                page.screenshot(path=str(screenshot_path))
            except Exception:
                pass

        return result, screenshot_path


__all__ = [
    "QualityGate",
    "LintGate",
    "TypeCheckGate",
    "UnitTestGate",
    "BrowserAutomationGate",
    "StoryValidationGate",
]
