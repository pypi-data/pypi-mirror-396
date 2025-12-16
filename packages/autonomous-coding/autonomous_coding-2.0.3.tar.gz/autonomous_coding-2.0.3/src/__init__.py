"""
Autonomous Coding Agent
=======================

A multi-agent autonomous coding system powered by Claude AI.

This package provides:
- Orchestrator: Coordinates workflow between agents
- Agents: Initializer, Dev, and QA agents
- Quality Gates: Lint, type check, unit tests, browser automation, story validation
- API Rotation: Automatic key rotation for long-running sessions

Example usage:
    from core.orchestrator import Orchestrator
    from quality.qa_agent import QAAgent

    # Run orchestrator
    orchestrator = Orchestrator(project_dir)
    orchestrator.run()

    # Or run QA agent directly
    qa = QAAgent(project_dir)
    report = qa.run_quality_gates(feature_id=1)
"""

__version__ = "2.0.3"
__author__ = "Anthropic"

from agents.session import (
    run_agent_session,
    run_autonomous_agent,
)
from core.client import create_client
from core.orchestrator import (
    Orchestrator,
    WorkflowState,
    write_agent_completion_signal,
)
from quality.gates import (
    BrowserAutomationGate,
    LintGate,
    StoryValidationGate,
    TypeCheckGate,
    UnitTestGate,
)
from quality.qa_agent import QAAgent

__all__ = [
    # Version
    "__version__",
    # Orchestrator
    "Orchestrator",
    "WorkflowState",
    "write_agent_completion_signal",
    # Client
    "create_client",
    # QA
    "QAAgent",
    "LintGate",
    "TypeCheckGate",
    "UnitTestGate",
    "BrowserAutomationGate",
    "StoryValidationGate",
    # Agents
    "run_agent_session",
    "run_autonomous_agent",
]
