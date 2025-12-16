"""
Core module for the autonomous coding system.

Contains:
- orchestrator: Workflow state machine and agent coordination
- client: Claude SDK client configuration
- security: Bash command allowlist and validation
- progress: Progress tracking utilities
- prompts: Prompt loading utilities
"""

from core.client import create_client
from core.orchestrator import (
    Orchestrator,
    WorkflowState,
    atomic_write_json,
    write_agent_completion_signal,
)
from core.progress import ProgressTracker
from core.prompts import (
    get_coding_prompt,
    get_initializer_prompt,
    get_orchestrator_prompt,
    get_qa_prompt,
    get_spec_validation_prompt,
    load_prompt,
)
from core.security import (
    ALLOWED_COMMANDS,
    SecurityHook,
    is_command_allowed,
)

__all__ = [
    # Orchestrator
    "Orchestrator",
    "WorkflowState",
    "write_agent_completion_signal",
    "atomic_write_json",
    # Client
    "create_client",
    # Security
    "ALLOWED_COMMANDS",
    "is_command_allowed",
    "SecurityHook",
    # Progress
    "ProgressTracker",
    # Prompts
    "load_prompt",
    "get_initializer_prompt",
    "get_coding_prompt",
    "get_qa_prompt",
    "get_orchestrator_prompt",
    "get_spec_validation_prompt",
]
