"""
Orchestrator Agent
==================

Manages workflow coordination and state transitions between agents
(Initializer, Dev, QA) using signal file polling and workflow state machine.

Features:
- Signal file polling for agent completion detection
- Workflow state machine with transition validation
- Sequential execution enforcement (one agent at a time)
- Feature-based timeout tracking
- Graceful shutdown handling
"""

import json
import logging
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class WorkflowState(Enum):
    """Workflow states for the autonomous coding system."""

    START = "START"
    INITIALIZER = "INITIALIZER"
    SPEC_VALIDATION = "SPEC_VALIDATION"  # New: Validate spec before dev
    SPEC_VALIDATED = "SPEC_VALIDATED"  # New: Spec passed validation
    DEV_READY = "DEV_READY"
    DEV = "DEV"
    QA_READY = "QA_READY"
    QA = "QA"
    QA_PASSED = "QA_PASSED"
    DEV_FEEDBACK = "DEV_FEEDBACK"
    COMPLETE = "COMPLETE"


def atomic_write_json(file_path: Path, data: dict[str, Any]) -> None:
    """
    Write JSON atomically via temp file + rename.

    Args:
        file_path: Path to the target JSON file
        data: Dictionary to write as JSON
    """
    temp_path = file_path.with_suffix(".tmp")
    with open(temp_path, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(temp_path, file_path)  # Atomic on POSIX


# JSON Schema for workflow state validation
WORKFLOW_STATE_SCHEMA = {
    "type": "object",
    "required": ["current_state", "timestamp"],
    "properties": {
        "current_state": {
            "type": "string",
            "enum": [state.value for state in WorkflowState],
        },
        "next_agent": {"type": ["string", "null"]},
        "previous_state": {"type": ["string", "null"]},
        "timestamp": {"type": "string"},  # ISO 8601 format
        "feature_id": {"type": ["integer", "null"]},
        "transition_history": {"type": "array"},
    },
}


# JSON Schema for agent completion signal validation
AGENT_SIGNAL_SCHEMA = {
    "type": "object",
    "required": ["agent_type", "session_id", "timestamp", "status", "next_state"],
    "properties": {
        "agent_type": {"type": "string", "enum": ["INITIALIZER", "SPEC_VALIDATOR", "DEV", "QA"]},
        "session_id": {"type": "string"},
        "timestamp": {"type": "string"},
        "status": {"type": "string", "enum": ["COMPLETE", "ERROR", "TIMEOUT"]},
        "next_state": {"type": "string"},
        "feature_id": {"type": ["integer", "null"]},
        "artifacts_created": {"type": "array"},
        "exit_code": {"type": "integer"},
        "error_message": {"type": ["string", "null"]},
    },
}


def validate_workflow_state(data: dict[str, Any]) -> bool:
    """
    Validate workflow state data against schema.

    Args:
        data: Workflow state dictionary

    Returns:
        True if valid

    Raises:
        ValueError: If validation fails
    """
    # Basic required field validation
    if "current_state" not in data or "timestamp" not in data:
        raise ValueError("Missing required fields: current_state and timestamp")

    # Validate current_state enum
    valid_states = [state.value for state in WorkflowState]
    if data["current_state"] not in valid_states:
        raise ValueError(
            f"Invalid current_state: {data['current_state']}. Must be one of: {valid_states}"
        )

    return True


def validate_agent_signal(data: dict[str, Any]) -> bool:
    """
    Validate agent completion signal against schema.

    Args:
        data: Agent signal dictionary

    Returns:
        True if valid

    Raises:
        ValueError: If validation fails
    """
    # Basic required field validation
    required_fields = ["agent_type", "session_id", "timestamp", "status", "next_state"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    # Validate agent_type enum
    valid_agents = ["INITIALIZER", "SPEC_VALIDATOR", "DEV", "QA"]
    if data["agent_type"] not in valid_agents:
        raise ValueError(
            f"Invalid agent_type: {data['agent_type']}. Must be one of: {valid_agents}"
        )

    # Validate status enum
    valid_statuses = ["COMPLETE", "ERROR", "TIMEOUT"]
    if data["status"] not in valid_statuses:
        raise ValueError(f"Invalid status: {data['status']}. Must be one of: {valid_statuses}")

    return True


# Valid state transitions
VALID_TRANSITIONS = {
    WorkflowState.START: [WorkflowState.INITIALIZER],
    WorkflowState.INITIALIZER: [WorkflowState.SPEC_VALIDATION],  # Go to spec validation
    WorkflowState.SPEC_VALIDATION: [
        WorkflowState.SPEC_VALIDATED,
        WorkflowState.INITIALIZER,
    ],  # Pass or revise
    WorkflowState.SPEC_VALIDATED: [WorkflowState.DEV_READY],  # Proceed to dev
    WorkflowState.DEV_READY: [WorkflowState.DEV],
    WorkflowState.DEV: [WorkflowState.QA_READY],
    WorkflowState.QA_READY: [WorkflowState.QA],
    WorkflowState.QA: [WorkflowState.QA_PASSED, WorkflowState.DEV_FEEDBACK],
    WorkflowState.QA_PASSED: [WorkflowState.DEV, WorkflowState.COMPLETE],
    WorkflowState.DEV_FEEDBACK: [WorkflowState.DEV],
    WorkflowState.COMPLETE: [],  # Terminal state
}


# Agent to next state mapping
AGENT_NEXT_STATE = {
    "INITIALIZER": WorkflowState.SPEC_VALIDATION,  # Now goes to spec validation
    "SPEC_VALIDATOR": WorkflowState.SPEC_VALIDATED,  # Then to validated state
    "DEV": WorkflowState.QA_READY,
    "QA": None,  # Depends on pass/fail
}


class Orchestrator:
    """
    Orchestrator for managing workflow transitions between agents.

    Implements:
    - Signal file polling (T100-T103)
    - State machine transitions (T104-T107)
    - Agent spawning and timeout tracking (T110-T115)
    - Graceful shutdown (T116)
    """

    VERSION = "2.0.0"
    POLL_INTERVAL = 5  # seconds
    DEFAULT_TIMEOUT_SIMPLE = 10 * 60  # 10 minutes
    DEFAULT_TIMEOUT_COMPLEX = 30 * 60  # 30 minutes

    def __init__(self, project_dir: Path):
        """
        Initialize Orchestrator.

        Args:
            project_dir: Project directory path
        """
        self.project_dir = Path(project_dir)
        self.signals_dir = self.project_dir / ".agent-signals"
        self.processed_dir = self.signals_dir / "processed"
        self.workflow_state_path = self.project_dir / "workflow-state.json"
        self.log_path = self.project_dir / "orchestrator.log"

        # Create directories
        self.signals_dir.mkdir(exist_ok=True)
        self.processed_dir.mkdir(exist_ok=True)

        # State tracking
        self.running = False
        self.current_agent_pid: int | None = None
        self.agent_start_time: float | None = None

        # Setup logging
        self._setup_logging()

        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()

    def _setup_logging(self) -> None:
        """Setup logging to file and console."""
        self.logger = logging.getLogger("orchestrator")
        self.logger.setLevel(logging.DEBUG)

        # Clear existing handlers
        self.logger.handlers = []

        # File handler
        file_handler = logging.FileHandler(self.log_path)
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%dT%H:%M:%SZ"
        )
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter("[%(levelname)s] %(message)s")
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)

    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown (T116)."""
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

    def _handle_shutdown(self, signum, _frame) -> None:  # noqa: ARG002
        """Handle shutdown signals gracefully."""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False

    # =========================================================================
    # Workflow State Management (T104-T109)
    # =========================================================================

    def load_workflow_state(self) -> dict[str, Any]:
        """
        Load workflow state from file (T106).

        Returns:
            Workflow state dictionary
        """
        if not self.workflow_state_path.exists():
            # Initialize default state
            return self._create_initial_state()

        try:
            with open(self.workflow_state_path) as f:
                data = json.load(f)
            validate_workflow_state(data)
            return data
        except (json.JSONDecodeError, ValueError) as e:
            self.logger.error(f"Invalid workflow state file: {e}")
            return self._create_initial_state()

    def _create_initial_state(self) -> dict[str, Any]:
        """Create initial workflow state."""
        return {
            "current_state": WorkflowState.START.value,
            "next_agent": "INITIALIZER",
            "previous_state": None,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "feature_id": None,
            "transition_history": [],
        }

    def save_workflow_state(self, state: dict[str, Any]) -> None:
        """
        Save workflow state atomically (T106).

        Args:
            state: Workflow state dictionary
        """
        state["timestamp"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        atomic_write_json(self.workflow_state_path, state)
        self.logger.debug(f"Saved workflow state: {state['current_state']}")

    def transition_state(
        self,
        current_state: dict[str, Any],
        new_state: WorkflowState,
        triggered_by: str = "orchestrator",
    ) -> dict[str, Any]:
        """
        Transition to a new workflow state (T104-T105).

        Args:
            current_state: Current workflow state dict
            new_state: Target workflow state
            triggered_by: Who triggered the transition

        Returns:
            Updated workflow state

        Raises:
            ValueError: If transition is invalid
        """
        current = WorkflowState(current_state["current_state"])

        # Validate transition (T105)
        if new_state not in VALID_TRANSITIONS.get(current, []):
            raise ValueError(
                f"Invalid transition: {current.value} → {new_state.value}. "
                f"Valid transitions: {[s.value for s in VALID_TRANSITIONS.get(current, [])]}"
            )

        # Build transition record (T109)
        transition_record = {
            "from_state": current.value,
            "to_state": new_state.value,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "triggered_by": triggered_by,
        }

        # Update state
        current_state["previous_state"] = current.value
        current_state["current_state"] = new_state.value
        current_state["next_agent"] = self._determine_next_agent(new_state)

        # Add to history
        if "transition_history" not in current_state:
            current_state["transition_history"] = []
        current_state["transition_history"].append(transition_record)

        self.logger.info(f"State transition: {current.value} → {new_state.value}")

        return current_state

    def _determine_next_agent(self, state: WorkflowState) -> str | None:
        """
        Determine the next agent to run (T107).

        Args:
            state: Current workflow state

        Returns:
            Agent type string or None
        """
        agent_map = {
            WorkflowState.START: "INITIALIZER",
            WorkflowState.INITIALIZER: None,  # Wait for completion
            WorkflowState.SPEC_VALIDATION: "SPEC_VALIDATOR",  # Spawn spec validator
            WorkflowState.SPEC_VALIDATED: "DEV",  # Spec passed, ready for dev
            WorkflowState.DEV_READY: "DEV",
            WorkflowState.DEV: None,  # Wait for completion
            WorkflowState.QA_READY: "QA",
            WorkflowState.QA: None,  # Wait for completion
            WorkflowState.QA_PASSED: "DEV",  # Or COMPLETE if all features done
            WorkflowState.DEV_FEEDBACK: "DEV",
            WorkflowState.COMPLETE: None,
        }
        return agent_map.get(state)

    # =========================================================================
    # Signal File Processing (T100-T103, T108)
    # =========================================================================

    def poll_signals(self) -> list[dict[str, Any]]:
        """
        Poll for agent completion signals (T101).

        Returns:
            List of valid signal dicts, sorted chronologically
        """
        signals = []

        # Find all signal files
        signal_files = list(self.signals_dir.glob("*.json"))

        # Sort by modification time (T103)
        signal_files.sort(key=lambda p: p.stat().st_mtime)

        for signal_file in signal_files:
            try:
                with open(signal_file) as f:
                    data = json.load(f)

                # Validate signal (T102)
                validate_agent_signal(data)
                data["_file_path"] = str(signal_file)
                signals.append(data)

            except (json.JSONDecodeError, ValueError) as e:
                self.logger.warning(f"Invalid signal file {signal_file}: {e}")

        return signals

    def archive_signal(self, signal_path: str) -> None:
        """
        Archive a processed signal file (T108).

        Args:
            signal_path: Path to the signal file
        """
        source = Path(signal_path)
        if source.exists():
            dest = self.processed_dir / source.name
            source.rename(dest)
            self.logger.debug(f"Archived signal: {source.name}")

    def process_signal(
        self, signal_data: dict[str, Any], workflow_state: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Process an agent completion signal.

        Args:
            signal_data: Signal data dict
            workflow_state: Current workflow state

        Returns:
            Updated workflow state
        """
        agent_type = signal_data["agent_type"]
        status = signal_data["status"]
        next_state_str = signal_data["next_state"]

        self.logger.info(
            f"Processing signal: agent={agent_type}, status={status}, next={next_state_str}"
        )

        # Clear current agent tracking
        self.current_agent_pid = None
        self.agent_start_time = None

        if status == "ERROR":
            self.logger.error(f"Agent {agent_type} failed: {signal_data.get('error_message')}")
            # Don't transition on error - stay in current state
            return workflow_state

        if status == "TIMEOUT":
            self.logger.error(f"Agent {agent_type} timed out")
            return workflow_state

        # Transition to next state
        try:
            next_state = WorkflowState(next_state_str)
            workflow_state = self.transition_state(
                workflow_state,
                next_state,
                triggered_by=f"{agent_type}_signal",
            )

            # Update feature_id if provided
            if signal_data.get("feature_id") is not None:
                workflow_state["feature_id"] = signal_data["feature_id"]

        except ValueError as e:
            self.logger.error(f"Invalid state transition: {e}")

        # Archive the signal
        self.archive_signal(signal_data.get("_file_path", ""))

        return workflow_state

    # =========================================================================
    # Agent Spawning (T110-T115)
    # =========================================================================

    def spawn_agent(self, agent_type: str, workflow_state: dict[str, Any]) -> bool:
        """
        Spawn an agent subprocess (T110).

        Args:
            agent_type: Type of agent to spawn
            workflow_state: Current workflow state

        Returns:
            True if agent was spawned successfully
        """
        # Check for duplicate agent (T115)
        if self.current_agent_pid is not None:
            self.logger.warning(f"Agent already running (PID {self.current_agent_pid})")
            return False

        # Determine agent command - use the CLI entry point
        agent_commands = {
            "INITIALIZER": [sys.executable, "-m", "autonomous_coding", "--agent", "initializer"],
            "SPEC_VALIDATOR": [
                sys.executable,
                "-m",
                "autonomous_coding",
                "--agent",
                "spec_validator",
            ],
            "DEV": [sys.executable, "-m", "autonomous_coding", "--agent", "dev"],
            "QA": [sys.executable, "-m", "autonomous_coding", "--agent", "qa"],
        }

        cmd = agent_commands.get(agent_type)
        if not cmd:
            self.logger.error(f"Unknown agent type: {agent_type}")
            return False

        try:
            # Set environment variables
            env = os.environ.copy()
            env["AGENT_TYPE"] = agent_type
            if workflow_state.get("feature_id"):
                env["FEATURE_ID"] = str(workflow_state["feature_id"])

            # Spawn process
            process = subprocess.Popen(
                cmd,
                cwd=str(self.project_dir),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self.current_agent_pid = process.pid
            self.agent_start_time = time.time()

            self.logger.info(f"Spawned {agent_type} agent (PID {process.pid})")
            return True

        except Exception as e:
            self.logger.error(f"Failed to spawn {agent_type} agent: {e}")
            return False

    def check_agent_timeout(self, workflow_state: dict[str, Any]) -> bool:
        """
        Check if current agent has timed out (T112-T113).

        Args:
            workflow_state: Current workflow state

        Returns:
            True if timed out
        """
        if self.agent_start_time is None:
            return False

        # Get timeout from feature or use default
        timeout = self.DEFAULT_TIMEOUT_SIMPLE
        if workflow_state.get("feature_id"):
            # Could look up timeout_minutes from feature_list.json here
            pass

        elapsed = time.time() - self.agent_start_time
        if elapsed > timeout:
            self.logger.error(f"Agent timeout after {elapsed:.0f}s (limit: {timeout}s)")
            return True

        return False

    # =========================================================================
    # Main Loop (T100)
    # =========================================================================

    def run(self) -> None:
        """
        Main orchestrator loop (T100).

        Continuously polls for signals and manages workflow transitions.
        """
        self.running = True
        self.logger.info(f"Orchestrator v{self.VERSION} starting...")
        self.logger.info(f"Project directory: {self.project_dir}")
        self.logger.info(f"Signals directory: {self.signals_dir}")

        # Load initial state
        workflow_state = self.load_workflow_state()
        self.logger.info(f"Initial state: {workflow_state['current_state']}")

        while self.running:
            try:
                # Check for signals
                signals = self.poll_signals()

                # Process signals
                for signal_data in signals:
                    workflow_state = self.process_signal(signal_data, workflow_state)
                    self.save_workflow_state(workflow_state)

                # Check for timeout
                if self.check_agent_timeout(workflow_state):
                    self.current_agent_pid = None
                    self.agent_start_time = None

                # Spawn next agent if needed
                next_agent = workflow_state.get("next_agent")
                if next_agent and self.current_agent_pid is None:
                    current = WorkflowState(workflow_state["current_state"])

                    # Auto-transition from *_READY and *_VALIDATED states
                    if current == WorkflowState.DEV_READY:
                        workflow_state = self.transition_state(workflow_state, WorkflowState.DEV)
                        self.save_workflow_state(workflow_state)
                        self.spawn_agent("DEV", workflow_state)

                    elif current == WorkflowState.SPEC_VALIDATED:
                        # Spec validation passed, transition to DEV_READY then DEV
                        workflow_state = self.transition_state(
                            workflow_state, WorkflowState.DEV_READY
                        )
                        self.save_workflow_state(workflow_state)
                        # Then immediately transition to DEV
                        workflow_state = self.transition_state(workflow_state, WorkflowState.DEV)
                        self.save_workflow_state(workflow_state)
                        self.spawn_agent("DEV", workflow_state)

                    elif current == WorkflowState.QA_READY:
                        workflow_state = self.transition_state(workflow_state, WorkflowState.QA)
                        self.save_workflow_state(workflow_state)
                        self.spawn_agent("QA", workflow_state)

                    elif current == WorkflowState.SPEC_VALIDATION:
                        # Spawn spec validator agent
                        self.spawn_agent("SPEC_VALIDATOR", workflow_state)

                    elif current == WorkflowState.START:
                        workflow_state = self.transition_state(
                            workflow_state, WorkflowState.INITIALIZER
                        )
                        self.save_workflow_state(workflow_state)
                        self.spawn_agent("INITIALIZER", workflow_state)

                # Sleep before next poll
                time.sleep(self.POLL_INTERVAL)

            except Exception as e:
                self.logger.exception(f"Error in main loop: {e}")
                time.sleep(self.POLL_INTERVAL)

        self.logger.info("Orchestrator shutdown complete")

    def run_once(self) -> dict[str, Any]:
        """
        Run a single iteration of the orchestrator loop.

        Useful for testing.

        Returns:
            Current workflow state
        """
        workflow_state = self.load_workflow_state()

        # Process any pending signals
        signals = self.poll_signals()
        for signal_data in signals:
            workflow_state = self.process_signal(signal_data, workflow_state)
            self.save_workflow_state(workflow_state)

        return workflow_state


def write_agent_completion_signal(
    project_dir: Path,
    agent_type: str,
    session_id: str,
    status: str,
    next_state: str,
    feature_id: int | None = None,
    artifacts: list[str] | None = None,
    exit_code: int = 0,
    error_message: str | None = None,
) -> Path:
    """
    Write an agent completion signal file (T111).

    Args:
        project_dir: Project directory
        agent_type: Type of agent (INITIALIZER, DEV, QA)
        session_id: Unique session identifier
        status: Completion status (COMPLETE, ERROR, TIMEOUT)
        next_state: Next workflow state
        feature_id: Feature ID if applicable
        artifacts: List of created artifacts
        exit_code: Exit code (0 for success)
        error_message: Error message if status is ERROR

    Returns:
        Path to the created signal file
    """
    signals_dir = Path(project_dir) / ".agent-signals"
    signals_dir.mkdir(exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H-%M-%S")
    signal_file = signals_dir / f"{agent_type.lower()}-{timestamp}.json"

    signal_data = {
        "agent_type": agent_type,
        "session_id": session_id,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": status,
        "next_state": next_state,
        "feature_id": feature_id,
        "artifacts_created": artifacts or [],
        "exit_code": exit_code,
        "error_message": error_message,
    }

    atomic_write_json(signal_file, signal_data)
    return signal_file


def main():
    """Main entry point for the orchestrator."""
    import argparse

    parser = argparse.ArgumentParser(description="Orchestrator Agent")
    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path.cwd(),
        help="Project directory path",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit (for testing)",
    )

    args = parser.parse_args()

    orchestrator = Orchestrator(args.project_dir)

    if args.once:
        state = orchestrator.run_once()
        print(json.dumps(state, indent=2))
    else:
        orchestrator.run()


if __name__ == "__main__":
    main()
