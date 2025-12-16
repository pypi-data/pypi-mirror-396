"""
Progress Tracking Utilities
===========================

Functions for tracking and displaying progress of the autonomous coding agent.
"""

import json
from datetime import datetime
from pathlib import Path


class ProgressTracker:
    """Track progress of feature implementation."""

    def __init__(self, project_dir: Path):
        """
        Initialize progress tracker.

        Args:
            project_dir: Directory containing feature_list.json
        """
        self.project_dir = Path(project_dir)
        self.feature_list_path = self.project_dir / "feature_list.json"

    def count_passing_tests(self) -> tuple[int, int]:
        """
        Count passing and total tests in feature_list.json.

        Returns:
            (passing_count, total_count)
        """
        return count_passing_tests(self.project_dir)

    def get_progress_percentage(self) -> float:
        """
        Get progress as a percentage.

        Returns:
            Percentage of passing tests (0-100)
        """
        passing, total = self.count_passing_tests()
        if total == 0:
            return 0.0
        return (passing / total) * 100

    def print_summary(self) -> None:
        """Print a summary of current progress."""
        print_progress_summary(self.project_dir)


def count_passing_tests(project_dir: Path) -> tuple[int, int]:
    """
    Count passing and total tests in feature_list.json.

    Args:
        project_dir: Directory containing feature_list.json

    Returns:
        (passing_count, total_count)
    """
    tests_file = Path(project_dir) / "feature_list.json"

    if not tests_file.exists():
        return 0, 0

    try:
        with open(tests_file) as f:
            tests = json.load(f)

        total = len(tests)
        passing = sum(1 for test in tests if test.get("passes", False))

        return passing, total
    except (OSError, json.JSONDecodeError):
        return 0, 0


def _get_timestamp() -> str:
    """Get dev-friendly timestamp: YYYY-MM-DD HH:MM:SS"""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def print_session_header(session_num: int, is_initializer: bool) -> None:
    """Print a formatted header for the session."""
    session_type = "INITIALIZER" if is_initializer else "CODING AGENT"
    timestamp = _get_timestamp()

    print(f"\n{timestamp} " + "=" * 60)
    print(f"{timestamp}   SESSION {session_num}: {session_type}")
    print(f"{timestamp} " + "=" * 60)
    print()


def print_progress_summary(project_dir: Path) -> None:
    """Print a summary of current progress."""
    passing, total = count_passing_tests(project_dir)
    timestamp = _get_timestamp()

    if total > 0:
        percentage = (passing / total) * 100
        print(f"{timestamp} ℹ️  [Progress] {passing}/{total} tests passing ({percentage:.1f}%)")
    else:
        print(f"{timestamp} ℹ️  [Progress] feature_list.json not yet created")
