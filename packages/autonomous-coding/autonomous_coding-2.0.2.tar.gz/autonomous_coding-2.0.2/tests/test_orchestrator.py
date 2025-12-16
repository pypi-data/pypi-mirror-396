"""
Tests for Orchestrator Agent
============================

Tests for Phase 8 (T100-T125): Orchestrator workflow management
"""

import json
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from core.orchestrator import (
    VALID_TRANSITIONS,
    Orchestrator,
    WorkflowState,
    atomic_write_json,
    validate_agent_signal,
    validate_workflow_state,
    write_agent_completion_signal,
)


class TestAtomicWriteJson:
    """Tests for atomic JSON writing (T019)."""

    def test_atomic_write_creates_file(self, tmp_path):
        """Test that atomic_write_json creates a new file."""
        file_path = tmp_path / "test.json"
        data = {"key": "value"}

        atomic_write_json(file_path, data)

        assert file_path.exists()
        with open(file_path) as f:
            result = json.load(f)
        assert result == data

    def test_atomic_write_overwrites_file(self, tmp_path):
        """Test that atomic_write_json overwrites existing file."""
        file_path = tmp_path / "test.json"
        file_path.write_text('{"old": "data"}')

        atomic_write_json(file_path, {"new": "data"})

        with open(file_path) as f:
            result = json.load(f)
        assert result == {"new": "data"}

    def test_atomic_write_no_temp_file_left(self, tmp_path):
        """Test that no temporary file is left after write."""
        file_path = tmp_path / "test.json"
        atomic_write_json(file_path, {"test": True})

        temp_file = file_path.with_suffix(".tmp")
        assert not temp_file.exists()


class TestValidateWorkflowState:
    """Tests for workflow state validation (T024)."""

    def test_valid_workflow_state(self):
        """Test validation passes for valid state."""
        state = {
            "current_state": "DEV_READY",
            "timestamp": "2024-01-01T00:00:00Z",
        }
        assert validate_workflow_state(state) is True

    def test_missing_current_state(self):
        """Test validation fails without current_state."""
        state = {"timestamp": "2024-01-01T00:00:00Z"}
        with pytest.raises(ValueError, match="Missing required fields"):
            validate_workflow_state(state)

    def test_missing_timestamp(self):
        """Test validation fails without timestamp."""
        state = {"current_state": "START"}
        with pytest.raises(ValueError, match="Missing required fields"):
            validate_workflow_state(state)

    def test_invalid_state_value(self):
        """Test validation fails for invalid state value."""
        state = {
            "current_state": "INVALID_STATE",
            "timestamp": "2024-01-01T00:00:00Z",
        }
        with pytest.raises(ValueError, match="Invalid current_state"):
            validate_workflow_state(state)

    @pytest.mark.parametrize("state", [s.value for s in WorkflowState])
    def test_all_workflow_states_valid(self, state):
        """Test all WorkflowState enum values are valid."""
        data = {"current_state": state, "timestamp": "2024-01-01T00:00:00Z"}
        assert validate_workflow_state(data) is True


class TestValidateAgentSignal:
    """Tests for agent signal validation (T102)."""

    def test_valid_agent_signal(self):
        """Test validation passes for valid signal."""
        signal = {
            "agent_type": "QA",
            "session_id": "test-123",
            "timestamp": "2024-01-01T00:00:00Z",
            "status": "COMPLETE",
            "next_state": "QA_PASSED",
        }
        assert validate_agent_signal(signal) is True

    def test_missing_required_field(self):
        """Test validation fails for missing required field."""
        signal = {
            "agent_type": "QA",
            "session_id": "test-123",
            "timestamp": "2024-01-01T00:00:00Z",
            # missing status and next_state
        }
        with pytest.raises(ValueError, match="Missing required fields"):
            validate_agent_signal(signal)

    def test_invalid_agent_type(self):
        """Test validation fails for invalid agent_type."""
        signal = {
            "agent_type": "INVALID",
            "session_id": "test-123",
            "timestamp": "2024-01-01T00:00:00Z",
            "status": "COMPLETE",
            "next_state": "QA_PASSED",
        }
        with pytest.raises(ValueError, match="Invalid agent_type"):
            validate_agent_signal(signal)

    def test_invalid_status(self):
        """Test validation fails for invalid status."""
        signal = {
            "agent_type": "QA",
            "session_id": "test-123",
            "timestamp": "2024-01-01T00:00:00Z",
            "status": "INVALID",
            "next_state": "QA_PASSED",
        }
        with pytest.raises(ValueError, match="Invalid status"):
            validate_agent_signal(signal)

    @pytest.mark.parametrize("agent_type", ["INITIALIZER", "SPEC_VALIDATOR", "DEV", "QA"])
    def test_all_agent_types_valid(self, agent_type):
        """Test all agent types are valid."""
        signal = {
            "agent_type": agent_type,
            "session_id": "test-123",
            "timestamp": "2024-01-01T00:00:00Z",
            "status": "COMPLETE",
            "next_state": "SPEC_VALIDATION",  # Valid next state for all agents
        }
        assert validate_agent_signal(signal) is True


class TestWorkflowStateTransitions:
    """Tests for valid state transitions (T104-T105)."""

    def test_valid_transitions_from_start(self):
        """Test valid transitions from START state."""
        assert VALID_TRANSITIONS[WorkflowState.START] == [WorkflowState.INITIALIZER]

    def test_valid_transitions_from_qa(self):
        """Test valid transitions from QA state."""
        assert WorkflowState.QA_PASSED in VALID_TRANSITIONS[WorkflowState.QA]
        assert WorkflowState.DEV_FEEDBACK in VALID_TRANSITIONS[WorkflowState.QA]

    def test_complete_is_terminal(self):
        """Test COMPLETE is a terminal state."""
        assert VALID_TRANSITIONS[WorkflowState.COMPLETE] == []

    def test_all_states_have_transitions_defined(self):
        """Test all states have transitions defined."""
        for state in WorkflowState:
            assert state in VALID_TRANSITIONS


class TestOrchestrator:
    """Tests for Orchestrator class (T100-T116)."""

    @pytest.fixture
    def orchestrator(self, tmp_path):
        """Create orchestrator with temporary directory."""
        return Orchestrator(tmp_path)

    def test_init_creates_directories(self, tmp_path):
        """Test T100: Orchestrator creates required directories."""
        orchestrator = Orchestrator(tmp_path)

        assert orchestrator.signals_dir.exists()
        assert orchestrator.processed_dir.exists()

    def test_load_workflow_state_creates_initial(self, orchestrator):
        """Test T106: Load creates initial state if file doesn't exist."""
        state = orchestrator.load_workflow_state()

        assert state["current_state"] == "START"
        assert state["next_agent"] == "INITIALIZER"
        assert "timestamp" in state

    def test_load_workflow_state_reads_existing(self, orchestrator):
        """Test T106: Load reads existing state file."""
        existing_state = {
            "current_state": "DEV_READY",
            "timestamp": "2024-01-01T00:00:00Z",
            "next_agent": "DEV",
        }
        atomic_write_json(orchestrator.workflow_state_path, existing_state)

        state = orchestrator.load_workflow_state()

        assert state["current_state"] == "DEV_READY"

    def test_save_workflow_state(self, orchestrator):
        """Test T106: Save workflow state atomically."""
        state = {
            "current_state": "QA_READY",
            "timestamp": "",
            "next_agent": "QA",
        }

        orchestrator.save_workflow_state(state)

        assert orchestrator.workflow_state_path.exists()
        with open(orchestrator.workflow_state_path) as f:
            saved = json.load(f)
        assert saved["current_state"] == "QA_READY"
        assert saved["timestamp"] != ""  # Timestamp should be updated

    def test_transition_state_valid(self, orchestrator):
        """Test T104: Valid state transition succeeds."""
        state = orchestrator.load_workflow_state()  # START

        new_state = orchestrator.transition_state(state, WorkflowState.INITIALIZER)

        assert new_state["current_state"] == "INITIALIZER"
        assert new_state["previous_state"] == "START"
        assert len(new_state["transition_history"]) == 1

    def test_transition_state_invalid_raises(self, orchestrator):
        """Test T105: Invalid state transition raises ValueError."""
        state = {
            "current_state": "START",
            "timestamp": "2024-01-01T00:00:00Z",
        }

        with pytest.raises(ValueError, match="Invalid transition"):
            orchestrator.transition_state(state, WorkflowState.COMPLETE)

    def test_transition_state_records_history(self, orchestrator):
        """Test T109: Transitions are recorded in history."""
        state = orchestrator.load_workflow_state()

        # Multiple transitions (updated for new workflow with SPEC_VALIDATION)
        state = orchestrator.transition_state(state, WorkflowState.INITIALIZER)
        state = orchestrator.transition_state(state, WorkflowState.SPEC_VALIDATION)
        state = orchestrator.transition_state(state, WorkflowState.SPEC_VALIDATED)
        state = orchestrator.transition_state(state, WorkflowState.DEV_READY)
        state = orchestrator.transition_state(state, WorkflowState.DEV)

        assert len(state["transition_history"]) == 5
        assert state["transition_history"][0]["from_state"] == "START"
        assert state["transition_history"][0]["to_state"] == "INITIALIZER"

    def test_poll_signals_empty(self, orchestrator):
        """Test T101: Poll returns empty list when no signals."""
        signals = orchestrator.poll_signals()
        assert signals == []

    def test_poll_signals_finds_valid(self, orchestrator):
        """Test T101: Poll finds valid signal files."""
        signal_data = {
            "agent_type": "DEV",
            "session_id": "test-123",
            "timestamp": "2024-01-01T00:00:00Z",
            "status": "COMPLETE",
            "next_state": "QA_READY",
        }
        signal_file = orchestrator.signals_dir / "dev-test.json"
        atomic_write_json(signal_file, signal_data)

        signals = orchestrator.poll_signals()

        assert len(signals) == 1
        assert signals[0]["agent_type"] == "DEV"

    def test_poll_signals_ignores_invalid(self, orchestrator):
        """Test T102: Poll ignores invalid signal files."""
        # Create invalid signal
        invalid_file = orchestrator.signals_dir / "invalid.json"
        invalid_file.write_text('{"invalid": "data"}')

        signals = orchestrator.poll_signals()

        assert len(signals) == 0

    def test_poll_signals_chronological_order(self, orchestrator):
        """Test T103: Signals are sorted by modification time."""
        # Create first signal
        signal1 = orchestrator.signals_dir / "first.json"
        atomic_write_json(
            signal1,
            {
                "agent_type": "DEV",
                "session_id": "1",
                "timestamp": "2024-01-01T00:00:00Z",
                "status": "COMPLETE",
                "next_state": "QA_READY",
            },
        )

        time.sleep(0.01)  # Ensure different mtime

        # Create second signal
        signal2 = orchestrator.signals_dir / "second.json"
        atomic_write_json(
            signal2,
            {
                "agent_type": "QA",
                "session_id": "2",
                "timestamp": "2024-01-01T00:00:01Z",
                "status": "COMPLETE",
                "next_state": "QA_PASSED",
            },
        )

        signals = orchestrator.poll_signals()

        assert len(signals) == 2
        assert signals[0]["session_id"] == "1"
        assert signals[1]["session_id"] == "2"

    def test_archive_signal(self, orchestrator):
        """Test T108: Signal files are archived after processing."""
        signal_file = orchestrator.signals_dir / "test.json"
        atomic_write_json(signal_file, {"test": True})

        orchestrator.archive_signal(str(signal_file))

        assert not signal_file.exists()
        assert (orchestrator.processed_dir / "test.json").exists()

    def test_process_signal_updates_state(self, orchestrator):
        """Test process_signal updates workflow state."""
        # Start in INITIALIZER state (updated for new workflow with SPEC_VALIDATION)
        state = {
            "current_state": "INITIALIZER",
            "timestamp": "2024-01-01T00:00:00Z",
            "transition_history": [],
        }

        signal_data = {
            "agent_type": "INITIALIZER",
            "session_id": "test",
            "timestamp": "2024-01-01T00:00:00Z",
            "status": "COMPLETE",
            "next_state": "SPEC_VALIDATION",  # Now goes to SPEC_VALIDATION
            "_file_path": str(orchestrator.signals_dir / "test.json"),
        }
        # Create the file so archive works
        atomic_write_json(Path(signal_data["_file_path"]), signal_data)

        new_state = orchestrator.process_signal(signal_data, state)

        assert new_state["current_state"] == "SPEC_VALIDATION"

    def test_process_signal_error_status(self, orchestrator):
        """Test process_signal handles ERROR status."""
        state = {
            "current_state": "DEV",
            "timestamp": "2024-01-01T00:00:00Z",
            "transition_history": [],
        }

        signal_data = {
            "agent_type": "DEV",
            "session_id": "test",
            "timestamp": "2024-01-01T00:00:00Z",
            "status": "ERROR",
            "next_state": "QA_READY",
            "error_message": "Dev agent failed",
        }

        new_state = orchestrator.process_signal(signal_data, state)

        # State should not change on error
        assert new_state["current_state"] == "DEV"

    def test_check_agent_timeout_not_started(self, orchestrator):
        """Test T112: No timeout when no agent started."""
        state = {"current_state": "START", "timestamp": ""}

        assert orchestrator.check_agent_timeout(state) is False

    def test_check_agent_timeout_within_limit(self, orchestrator):
        """Test T112: No timeout within time limit."""
        orchestrator.agent_start_time = time.time()
        state = {"current_state": "DEV", "timestamp": ""}

        assert orchestrator.check_agent_timeout(state) is False

    def test_check_agent_timeout_exceeded(self, orchestrator):
        """Test T113: Timeout when limit exceeded."""
        # Set start time in the past (beyond timeout)
        orchestrator.agent_start_time = time.time() - (orchestrator.DEFAULT_TIMEOUT_SIMPLE + 1)
        state = {"current_state": "DEV", "timestamp": ""}

        assert orchestrator.check_agent_timeout(state) is True

    @patch("subprocess.Popen")
    def test_spawn_agent_success(self, mock_popen, orchestrator):
        """Test T110: Spawn agent subprocess."""
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process

        state = {"current_state": "DEV_READY", "timestamp": ""}
        result = orchestrator.spawn_agent("DEV", state)

        assert result is True
        assert orchestrator.current_agent_pid == 12345
        assert orchestrator.agent_start_time is not None

    @patch("subprocess.Popen")
    def test_spawn_agent_already_running(self, mock_popen, orchestrator):
        """Test T115: Reject spawn if agent already running."""
        orchestrator.current_agent_pid = 12345

        state = {"current_state": "DEV_READY", "timestamp": ""}
        result = orchestrator.spawn_agent("DEV", state)

        assert result is False
        mock_popen.assert_not_called()

    def test_spawn_agent_unknown_type(self, orchestrator):
        """Test spawn_agent rejects unknown agent type."""
        state = {"current_state": "DEV_READY", "timestamp": ""}
        result = orchestrator.spawn_agent("UNKNOWN", state)

        assert result is False

    def test_run_once_processes_signals(self, orchestrator):
        """Test run_once processes pending signals."""
        # Set initial state to INITIALIZER
        initial_state = {
            "current_state": "INITIALIZER",
            "timestamp": "2024-01-01T00:00:00Z",
            "transition_history": [],
        }
        atomic_write_json(orchestrator.workflow_state_path, initial_state)

        # Create a completion signal (updated for new workflow with SPEC_VALIDATION)
        signal_data = {
            "agent_type": "INITIALIZER",
            "session_id": "test",
            "timestamp": "2024-01-01T00:00:00Z",
            "status": "COMPLETE",
            "next_state": "SPEC_VALIDATION",  # Now goes to SPEC_VALIDATION
        }
        atomic_write_json(orchestrator.signals_dir / "init-complete.json", signal_data)

        state = orchestrator.run_once()

        assert state["current_state"] == "SPEC_VALIDATION"


class TestWriteAgentCompletionSignal:
    """Tests for agent completion signal writing (T111)."""

    def test_write_signal_creates_file(self, tmp_path):
        """Test write_agent_completion_signal creates signal file."""
        signal_path = write_agent_completion_signal(
            project_dir=tmp_path,
            agent_type="QA",
            session_id="test-123",
            status="COMPLETE",
            next_state="QA_PASSED",
        )

        assert signal_path.exists()
        with open(signal_path) as f:
            data = json.load(f)
        assert data["agent_type"] == "QA"
        assert data["status"] == "COMPLETE"

    def test_write_signal_with_feature_id(self, tmp_path):
        """Test write_agent_completion_signal includes feature_id."""
        signal_path = write_agent_completion_signal(
            project_dir=tmp_path,
            agent_type="DEV",
            session_id="test-123",
            status="COMPLETE",
            next_state="QA_READY",
            feature_id=42,
        )

        with open(signal_path) as f:
            data = json.load(f)
        assert data["feature_id"] == 42

    def test_write_signal_with_error(self, tmp_path):
        """Test write_agent_completion_signal with error details."""
        signal_path = write_agent_completion_signal(
            project_dir=tmp_path,
            agent_type="DEV",
            session_id="test-123",
            status="ERROR",
            next_state="DEV",
            exit_code=1,
            error_message="Build failed",
        )

        with open(signal_path) as f:
            data = json.load(f)
        assert data["status"] == "ERROR"
        assert data["exit_code"] == 1
        assert data["error_message"] == "Build failed"

    def test_write_signal_with_artifacts(self, tmp_path):
        """Test write_agent_completion_signal includes artifacts."""
        artifacts = ["src/main.py", "tests/test_main.py"]
        signal_path = write_agent_completion_signal(
            project_dir=tmp_path,
            agent_type="DEV",
            session_id="test-123",
            status="COMPLETE",
            next_state="QA_READY",
            artifacts=artifacts,
        )

        with open(signal_path) as f:
            data = json.load(f)
        assert data["artifacts_created"] == artifacts

    def test_write_signal_creates_directory(self, tmp_path):
        """Test write_agent_completion_signal creates signals directory."""
        project = tmp_path / "new_project"
        project.mkdir()

        signal_path = write_agent_completion_signal(
            project_dir=project,
            agent_type="QA",
            session_id="test",
            status="COMPLETE",
            next_state="QA_PASSED",
        )

        assert (project / ".agent-signals").exists()
        assert signal_path.exists()


class TestGracefulShutdown:
    """Tests for graceful shutdown handling (T116)."""

    def test_shutdown_sets_running_false(self, tmp_path):
        """Test shutdown signal sets running to False."""
        orchestrator = Orchestrator(tmp_path)
        orchestrator.running = True

        orchestrator._handle_shutdown(15, None)  # SIGTERM

        assert orchestrator.running is False


class TestWorkflowStateMachine:
    """Integration tests for the full workflow state machine (T122-T123)."""

    @pytest.fixture
    def orchestrator(self, tmp_path):
        """Create orchestrator with temporary directory."""
        return Orchestrator(tmp_path)

    def test_full_workflow_happy_path(self, orchestrator):
        """Test T122: Full workflow transitions (updated for SPEC_VALIDATION)."""
        state = orchestrator.load_workflow_state()

        # START -> INITIALIZER
        state = orchestrator.transition_state(state, WorkflowState.INITIALIZER)
        assert state["current_state"] == "INITIALIZER"

        # INITIALIZER -> SPEC_VALIDATION (new step)
        state = orchestrator.transition_state(state, WorkflowState.SPEC_VALIDATION)
        assert state["current_state"] == "SPEC_VALIDATION"

        # SPEC_VALIDATION -> SPEC_VALIDATED (new step)
        state = orchestrator.transition_state(state, WorkflowState.SPEC_VALIDATED)
        assert state["current_state"] == "SPEC_VALIDATED"

        # SPEC_VALIDATED -> DEV_READY
        state = orchestrator.transition_state(state, WorkflowState.DEV_READY)
        assert state["current_state"] == "DEV_READY"

        # DEV_READY -> DEV
        state = orchestrator.transition_state(state, WorkflowState.DEV)
        assert state["current_state"] == "DEV"

        # DEV -> QA_READY
        state = orchestrator.transition_state(state, WorkflowState.QA_READY)
        assert state["current_state"] == "QA_READY"

        # QA_READY -> QA
        state = orchestrator.transition_state(state, WorkflowState.QA)
        assert state["current_state"] == "QA"

        # QA -> QA_PASSED
        state = orchestrator.transition_state(state, WorkflowState.QA_PASSED)
        assert state["current_state"] == "QA_PASSED"

        # QA_PASSED -> COMPLETE
        state = orchestrator.transition_state(state, WorkflowState.COMPLETE)
        assert state["current_state"] == "COMPLETE"

    def test_feedback_loop(self, orchestrator):
        """Test workflow with QA feedback loop (updated for SPEC_VALIDATION)."""
        state = orchestrator.load_workflow_state()

        # Get to QA state (including SPEC_VALIDATION steps)
        state = orchestrator.transition_state(state, WorkflowState.INITIALIZER)
        state = orchestrator.transition_state(state, WorkflowState.SPEC_VALIDATION)
        state = orchestrator.transition_state(state, WorkflowState.SPEC_VALIDATED)
        state = orchestrator.transition_state(state, WorkflowState.DEV_READY)
        state = orchestrator.transition_state(state, WorkflowState.DEV)
        state = orchestrator.transition_state(state, WorkflowState.QA_READY)
        state = orchestrator.transition_state(state, WorkflowState.QA)

        # QA fails -> feedback
        state = orchestrator.transition_state(state, WorkflowState.DEV_FEEDBACK)
        assert state["current_state"] == "DEV_FEEDBACK"

        # Back to DEV
        state = orchestrator.transition_state(state, WorkflowState.DEV)
        assert state["current_state"] == "DEV"

    def test_invalid_transition_blocked(self, orchestrator):
        """Test T123: Invalid transitions are blocked."""
        state = orchestrator.load_workflow_state()

        # Cannot go directly to COMPLETE from START
        with pytest.raises(ValueError):
            orchestrator.transition_state(state, WorkflowState.COMPLETE)

        # Cannot go to DEV from START
        with pytest.raises(ValueError):
            orchestrator.transition_state(state, WorkflowState.DEV)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
