"""
API Token Consumption Tracker
=============================

Tracks API token usage per project and generates consumption reports.
Helps monitor costs and usage patterns across different API endpoints.
"""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class APICallRecord:
    """Record of a single API call."""

    timestamp: str
    endpoint: str
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    session_id: int
    duration_seconds: float = 0.0
    success: bool = True
    error: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SessionStats:
    """Statistics for a single session."""

    session_id: int
    start_time: str
    end_time: str | None = None
    endpoint: str = ""
    model: str = ""
    total_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    duration_seconds: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ProjectTokenReport:
    """Complete token consumption report for a project."""

    project_name: str
    project_dir: str
    report_generated: str
    total_sessions: int = 0
    total_api_calls: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_tokens: int = 0
    total_duration_seconds: float = 0.0
    sessions: list[SessionStats] = field(default_factory=list)
    calls: list[APICallRecord] = field(default_factory=list)
    endpoint_breakdown: dict[str, dict] = field(default_factory=dict)

    # Cost estimation (approximate, based on Claude pricing)
    estimated_cost_usd: float = 0.0

    def to_dict(self) -> dict:
        return {
            "project_name": self.project_name,
            "project_dir": self.project_dir,
            "report_generated": self.report_generated,
            "summary": {
                "total_sessions": self.total_sessions,
                "total_api_calls": self.total_api_calls,
                "total_input_tokens": self.total_input_tokens,
                "total_output_tokens": self.total_output_tokens,
                "total_tokens": self.total_tokens,
                "total_duration_seconds": self.total_duration_seconds,
                "estimated_cost_usd": self.estimated_cost_usd,
            },
            "endpoint_breakdown": self.endpoint_breakdown,
            "sessions": [s.to_dict() for s in self.sessions],
            "calls": [c.to_dict() for c in self.calls[-100:]],  # Keep last 100 calls
        }


class TokenTracker:
    """
    Tracks API token consumption for a project.

    Usage:
        tracker = TokenTracker(project_dir)
        tracker.start_session(endpoint, model)
        tracker.record_call(input_tokens, output_tokens)
        tracker.end_session()
        tracker.save_report()
    """

    # Approximate pricing per 1M tokens (Claude Sonnet)
    INPUT_COST_PER_1M = 3.00  # $3 per 1M input tokens
    OUTPUT_COST_PER_1M = 15.00  # $15 per 1M output tokens

    def __init__(self, project_dir: Path):
        """
        Initialize token tracker for a project.

        Args:
            project_dir: Project directory path
        """
        self.project_dir = Path(project_dir)
        self.project_name = self.project_dir.name
        self.report_file = self.project_dir / "token-consumption-report.json"
        self.log_file = self.project_dir / "logs" / "token-usage.log"

        # Current session
        self.current_session: SessionStats | None = None
        self.session_counter = 0

        # Load existing report if available
        self.report = self._load_existing_report()

    def _load_existing_report(self) -> ProjectTokenReport:
        """Load existing report or create new one."""
        if self.report_file.exists():
            try:
                with open(self.report_file) as f:
                    data = json.load(f)

                report = ProjectTokenReport(
                    project_name=data.get("project_name", self.project_name),
                    project_dir=str(self.project_dir),
                    report_generated=data.get("report_generated", ""),
                    total_sessions=data.get("summary", {}).get("total_sessions", 0),
                    total_api_calls=data.get("summary", {}).get("total_api_calls", 0),
                    total_input_tokens=data.get("summary", {}).get("total_input_tokens", 0),
                    total_output_tokens=data.get("summary", {}).get("total_output_tokens", 0),
                    total_tokens=data.get("summary", {}).get("total_tokens", 0),
                    total_duration_seconds=data.get("summary", {}).get(
                        "total_duration_seconds", 0.0
                    ),
                    estimated_cost_usd=data.get("summary", {}).get("estimated_cost_usd", 0.0),
                    endpoint_breakdown=data.get("endpoint_breakdown", {}),
                )

                # Restore session counter
                self.session_counter = report.total_sessions

                return report
            except (json.JSONDecodeError, KeyError):
                pass

        return ProjectTokenReport(
            project_name=self.project_name,
            project_dir=str(self.project_dir),
            report_generated=datetime.now(timezone.utc).isoformat(),
        )

    def start_session(self, endpoint: str, model: str) -> int:
        """
        Start tracking a new session.

        Args:
            endpoint: API endpoint URL
            model: Model name

        Returns:
            Session ID
        """
        self.session_counter += 1

        self.current_session = SessionStats(
            session_id=self.session_counter,
            start_time=datetime.now(timezone.utc).isoformat(),
            endpoint=endpoint,
            model=model,
        )

        self._log(f"Session {self.session_counter} started - {endpoint}")

        return self.session_counter

    def record_call(
        self,
        input_tokens: int,
        output_tokens: int,
        duration_seconds: float = 0.0,
        success: bool = True,
        error: str | None = None,
    ) -> None:
        """
        Record an API call.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            duration_seconds: Call duration
            success: Whether call succeeded
            error: Error message if failed
        """
        if self.current_session is None:
            return

        total_tokens = input_tokens + output_tokens

        # Create call record
        record = APICallRecord(
            timestamp=datetime.now(timezone.utc).isoformat(),
            endpoint=self.current_session.endpoint,
            model=self.current_session.model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            session_id=self.current_session.session_id,
            duration_seconds=duration_seconds,
            success=success,
            error=error,
        )

        # Update session stats
        self.current_session.total_calls += 1
        self.current_session.input_tokens += input_tokens
        self.current_session.output_tokens += output_tokens
        self.current_session.total_tokens += total_tokens
        self.current_session.duration_seconds += duration_seconds

        if success:
            self.current_session.successful_calls += 1
        else:
            self.current_session.failed_calls += 1

        # Update report totals
        self.report.total_api_calls += 1
        self.report.total_input_tokens += input_tokens
        self.report.total_output_tokens += output_tokens
        self.report.total_tokens += total_tokens
        self.report.total_duration_seconds += duration_seconds

        # Update endpoint breakdown
        endpoint = self.current_session.endpoint
        if endpoint not in self.report.endpoint_breakdown:
            self.report.endpoint_breakdown[endpoint] = {
                "calls": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "estimated_cost_usd": 0.0,
            }

        self.report.endpoint_breakdown[endpoint]["calls"] += 1
        self.report.endpoint_breakdown[endpoint]["input_tokens"] += input_tokens
        self.report.endpoint_breakdown[endpoint]["output_tokens"] += output_tokens
        self.report.endpoint_breakdown[endpoint]["total_tokens"] += total_tokens

        # Calculate cost for this endpoint
        ep_input = self.report.endpoint_breakdown[endpoint]["input_tokens"]
        ep_output = self.report.endpoint_breakdown[endpoint]["output_tokens"]
        self.report.endpoint_breakdown[endpoint]["estimated_cost_usd"] = (
            ep_input / 1_000_000
        ) * self.INPUT_COST_PER_1M + (ep_output / 1_000_000) * self.OUTPUT_COST_PER_1M

        # Add to calls list (keep last 100)
        self.report.calls.append(record)
        if len(self.report.calls) > 100:
            self.report.calls = self.report.calls[-100:]

        # Calculate total estimated cost
        self.report.estimated_cost_usd = (
            self.report.total_input_tokens / 1_000_000
        ) * self.INPUT_COST_PER_1M + (
            self.report.total_output_tokens / 1_000_000
        ) * self.OUTPUT_COST_PER_1M

        self._log(
            f"Call: +{input_tokens} in, +{output_tokens} out = {total_tokens} tokens "
            f"(session total: {self.current_session.total_tokens})"
        )

    def end_session(self) -> SessionStats | None:
        """
        End the current session and add to report.

        Returns:
            Session statistics
        """
        if self.current_session is None:
            return None

        self.current_session.end_time = datetime.now(timezone.utc).isoformat()

        # Add to sessions list
        self.report.sessions.append(self.current_session)
        self.report.total_sessions += 1

        self._log(
            f"Session {self.current_session.session_id} ended - "
            f"{self.current_session.total_tokens} tokens, "
            f"{self.current_session.total_calls} calls"
        )

        session = self.current_session
        self.current_session = None

        return session

    def save_report(self) -> Path:
        """
        Save the consumption report to file.

        Returns:
            Path to the saved report
        """
        self.report.report_generated = datetime.now(timezone.utc).isoformat()

        # Ensure directory exists
        self.project_dir.mkdir(parents=True, exist_ok=True)

        with open(self.report_file, "w") as f:
            json.dump(self.report.to_dict(), f, indent=2)

        self._log(f"Report saved to {self.report_file}")

        return self.report_file

    def get_summary(self) -> str:
        """
        Get a human-readable summary of token consumption.

        Returns:
            Summary string
        """
        lines = [
            "",
            "=" * 60,
            "  API TOKEN CONSUMPTION REPORT",
            "=" * 60,
            f"  Project: {self.project_name}",
            f"  Sessions: {self.report.total_sessions}",
            f"  API Calls: {self.report.total_api_calls}",
            "",
            "  Token Usage:",
            f"    Input:  {self.report.total_input_tokens:,} tokens",
            f"    Output: {self.report.total_output_tokens:,} tokens",
            f"    Total:  {self.report.total_tokens:,} tokens",
            "",
            f"  Estimated Cost: ${self.report.estimated_cost_usd:.4f} USD",
            "",
        ]

        if self.report.endpoint_breakdown:
            lines.append("  Breakdown by Endpoint:")
            for endpoint, stats in self.report.endpoint_breakdown.items():
                # Shorten endpoint URL
                short_endpoint = endpoint.split("/")[-1] if "/" in endpoint else endpoint
                if len(short_endpoint) > 30:
                    short_endpoint = short_endpoint[:27] + "..."
                lines.append(
                    f"    {short_endpoint}: "
                    f"{stats['total_tokens']:,} tokens, "
                    f"${stats['estimated_cost_usd']:.4f}"
                )

        lines.extend(
            [
                "",
                f"  Report: {self.report_file}",
                "=" * 60,
                "",
            ]
        )

        return "\n".join(lines)

    def _log(self, message: str) -> None:
        """Log a message to the token usage log file."""
        try:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            with open(self.log_file, "a") as f:
                f.write(f"[{timestamp}] {message}\n")
        except Exception:
            pass  # Don't fail on logging errors


def create_tracker(project_dir: Path) -> TokenTracker:
    """
    Create a token tracker for a project.

    Args:
        project_dir: Project directory path

    Returns:
        TokenTracker instance
    """
    return TokenTracker(project_dir)
