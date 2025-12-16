# Implementation Plan: QA Agent

**Feature Branch**: `001-qa-agent`
**Spec Reference**: `docs/qa-agent-spec.md`
**Created**: 2025-12-07
**Status**: Draft

---

## Technical Context

### Existing Architecture

| Component | Location | Description |
|-----------|----------|-------------|
| Agent Entry Point | `autonomous_agent_demo.py` | Main entry point, manages agent sessions |
| Agent Logic | `agent.py` | `run_agent_session()` and `run_autonomous_agent()` functions |
| SDK Client | `client.py` | Claude SDK client configuration |
| Security | `security.py` | `ALLOWED_COMMANDS` allowlist, `bash_security_hook()` |
| Progress Tracking | `progress.py` | `count_passing_tests()`, `print_progress_summary()` |
| Prompts | `prompts.py` | `load_prompt()`, `get_initializer_prompt()`, `get_coding_prompt()` |

### Current Agent Flow

```
autonomous_agent_demo.py
         │
         ▼
    run_autonomous_agent()  ─────► Creates client per session
         │                         (fresh context window)
         │
         ├── Session 1: Initializer Agent
         │      └── get_initializer_prompt()
         │
         └── Session 2+: Coding Agent
                └── get_coding_prompt()
```

### Proposed Architecture

```
autonomous_agent_demo.py
         │
         ▼
    run_autonomous_agent()  ─────► Orchestrator logic
         │                         Reads workflow-state.json
         │
         ├── State: START/INITIALIZER
         │      └── get_initializer_prompt()
         │
         ├── State: DEV_READY/DEV/DEV_FEEDBACK
         │      └── get_dev_prompt()
         │
         └── State: QA_READY/QA
                └── get_qa_prompt()
```

### Tech Stack

| Layer | Technology | Notes |
|-------|------------|-------|
| Runtime | Python 3.x | Core agent logic |
| AI SDK | Claude Agent SDK | `claude-code-sdk` |
| CLI | Claude Code CLI | `@anthropic-ai/claude-code` |
| Version Control | Git | Progress persistence |
| Browser Automation | Playwright | E2E testing |
| Linting (JS/TS) | ESLint | Static analysis |
| Type Check (JS/TS) | TypeScript | `tsc --noEmit` |
| Linting (Python) | Ruff | Fast Python linter |
| Type Check (Python) | Mypy | Static type checker |
| Testing (JS/TS) | Jest/Vitest | Unit tests |
| Testing (Python) | Pytest | Unit tests |

---

## Constitution Compliance Check

### Pre-Design Evaluation

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Multi-Agent Orchestration | ✅ Compliant | Adding QA Agent to architecture |
| II. Role-Based Access Control | ✅ Compliant | QA Agent has exclusive `passes` permission |
| III. Session Independence | ✅ Compliant | qa-report.json enables cross-session state |
| IV. Quality Gates | ✅ Compliant | Implementing all 5 gates |
| V. Feedback Loop Protocol | ✅ Compliant | qa-report.json format defined |
| VI. Single Source of Truth | ✅ Compliant | feature_list.json schema extended |
| VII. Security First | ✅ Compliant | QA tools added to allowlist |
| VIII. Quality Over Speed | ✅ Compliant | Multiple validation layers |
| IX. Incremental Progress | ✅ Compliant | Each gate run produces results |

---

## Phase 0: Research & Clarification

### Resolved Questions

| Question | Resolution |
|----------|------------|
| How to detect project language (JS/TS vs Python)? | Check for `package.json` (Node) or `pyproject.toml`/`requirements.txt` (Python) |
| Which browser automation tool? | Playwright (better cross-browser support) |
| How to handle flaky tests? | Retry up to 3 times before failing |

### Research Completed

- [x] Claude Agent SDK supports multiple concurrent sessions
- [x] Playwright can be installed via `npm install -D playwright`
- [x] ESLint and TypeScript available as CLI tools
- [x] Ruff and Mypy available via pip
- [x] JSON schema validation for qa-report.json

---

## Phase 1: Design Artifacts

### 1.1 Data Models

#### Workflow State (workflow-state.json)

```python
# Location: New file at project root

@dataclass
class WorkflowState:
    """
    Tracks current workflow state for orchestrator.
    """
    current_state: str       # START, INITIALIZER, DEV_READY, DEV, QA_READY, QA, QA_PASSED, DEV_FEEDBACK, COMPLETE
    next_agent: str          # initializer, dev, qa
    current_feature_id: Optional[int]  # Feature being worked on
    qa_retries: int          # Number of QA retries for current feature
    last_transition: str     # ISO timestamp
    history: List[Dict]      # State transition history

# Example workflow-state.json:
{
  "current_state": "QA_READY",
  "next_agent": "qa",
  "current_feature_id": 42,
  "qa_retries": 0,
  "last_transition": "2025-12-07T10:30:00Z",
  "history": [
    {"from": "DEV", "to": "QA_READY", "timestamp": "2025-12-07T10:30:00Z"}
  ]
}
```

#### QA Report (qa-report.json)

```python
# Location: New file at project root

@dataclass
class QAGateResult:
    """Result of a single quality gate."""
    gate_name: str           # lint, type_check, unit_tests, browser_tests, story_validation
    passed: bool
    duration_ms: int
    errors: List[Dict]       # [{file, line, message, severity}]
    warnings: List[Dict]

@dataclass
class QAReport:
    """
    Complete QA report for a feature.
    """
    feature_id: int
    feature_description: str
    status: str              # PASSED, FAILED, ERROR
    gates: Dict[str, QAGateResult]
    summary: str
    priority_fixes: List[str]
    screenshots: List[str]   # Paths to captured screenshots
    timestamp: str           # ISO timestamp
    duration_total_ms: int
    retry_count: int

# Example qa-report.json:
{
  "feature_id": 42,
  "feature_description": "User login flow",
  "status": "FAILED",
  "gates": {
    "lint": {
      "gate_name": "lint",
      "passed": false,
      "duration_ms": 1234,
      "errors": [
        {"file": "src/Login.tsx", "line": 42, "message": "Unexpected any", "severity": "error"}
      ],
      "warnings": []
    },
    "type_check": {"gate_name": "type_check", "passed": true, "duration_ms": 2345, "errors": [], "warnings": []},
    "unit_tests": {"gate_name": "unit_tests", "passed": true, "duration_ms": 5678, "errors": [], "warnings": []},
    "browser_tests": {"gate_name": "browser_tests", "passed": false, "duration_ms": 10000, "errors": [
      {"file": "e2e/login.spec.ts", "line": 15, "message": "Element not found: #login-button", "severity": "error"}
    ], "warnings": []},
    "story_validation": {"gate_name": "story_validation", "passed": false, "duration_ms": 8000, "errors": [
      {"step": 3, "message": "Expected 'Welcome' text not found", "severity": "error"}
    ], "warnings": []}
  },
  "summary": "2 of 5 gates passed",
  "priority_fixes": [
    "1. Fix ESLint error in src/Login.tsx:42 - Unexpected any",
    "2. Add #login-button element to Login component",
    "3. Ensure 'Welcome' text appears after login"
  ],
  "screenshots": ["screenshots/login-step1.png", "screenshots/login-step3-fail.png"],
  "timestamp": "2025-12-07T10:30:00Z",
  "duration_total_ms": 27257,
  "retry_count": 0
}
```

#### Extended Feature Schema

```python
# Location: feature_list.json (schema extension)

@dataclass
class Feature:
    """
    Extended feature definition with QA fields.
    """
    id: int
    category: str            # functional, style
    description: str
    steps: List[str]
    passes: bool             # Only QA can modify
    qa_validated: bool       # True after QA runs successfully
    last_qa_run: Optional[str]  # ISO timestamp
    qa_notes: Optional[str]  # Notes from QA Agent

# Example feature entry:
{
  "id": 42,
  "category": "functional",
  "description": "User can log in with valid credentials",
  "steps": [
    "Step 1: Navigate to login page",
    "Step 2: Enter valid username",
    "Step 3: Enter valid password",
    "Step 4: Click login button",
    "Step 5: Verify redirect to dashboard",
    "Step 6: Verify welcome message displays"
  ],
  "passes": true,
  "qa_validated": true,
  "last_qa_run": "2025-12-07T10:30:00Z",
  "qa_notes": "All 5 gates passed on first attempt"
}
```

### 1.2 New Modules

#### orchestrator.py (NEW)

```python
# Location: orchestrator.py

"""
Workflow Orchestrator
=====================

Manages agent transitions based on workflow state machine.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import json
from datetime import datetime
from enum import Enum


class WorkflowState(Enum):
    START = "START"
    INITIALIZER = "INITIALIZER"
    DEV_READY = "DEV_READY"
    DEV = "DEV"
    QA_READY = "QA_READY"
    QA = "QA"
    QA_PASSED = "QA_PASSED"
    DEV_FEEDBACK = "DEV_FEEDBACK"
    COMPLETE = "COMPLETE"


class AgentType(Enum):
    INITIALIZER = "initializer"
    DEV = "dev"
    QA = "qa"


# State transition rules
VALID_TRANSITIONS = {
    WorkflowState.START: [WorkflowState.INITIALIZER],
    WorkflowState.INITIALIZER: [WorkflowState.DEV_READY],
    WorkflowState.DEV_READY: [WorkflowState.DEV],
    WorkflowState.DEV: [WorkflowState.QA_READY],
    WorkflowState.QA_READY: [WorkflowState.QA],
    WorkflowState.QA: [WorkflowState.QA_PASSED, WorkflowState.DEV_FEEDBACK],
    WorkflowState.QA_PASSED: [WorkflowState.DEV_READY, WorkflowState.COMPLETE],
    WorkflowState.DEV_FEEDBACK: [WorkflowState.DEV],
}

# State to agent mapping
STATE_TO_AGENT = {
    WorkflowState.START: AgentType.INITIALIZER,
    WorkflowState.INITIALIZER: AgentType.INITIALIZER,
    WorkflowState.DEV_READY: AgentType.DEV,
    WorkflowState.DEV: AgentType.DEV,
    WorkflowState.QA_READY: AgentType.QA,
    WorkflowState.QA: AgentType.QA,
    WorkflowState.DEV_FEEDBACK: AgentType.DEV,
}


def load_workflow_state(project_dir: Path) -> dict:
    """Load workflow state from file."""
    state_file = project_dir / "workflow-state.json"
    if state_file.exists():
        return json.loads(state_file.read_text())
    return {
        "current_state": WorkflowState.START.value,
        "next_agent": AgentType.INITIALIZER.value,
        "current_feature_id": None,
        "qa_retries": 0,
        "last_transition": datetime.now().isoformat(),
        "history": []
    }


def save_workflow_state(project_dir: Path, state: dict) -> None:
    """Save workflow state to file."""
    state_file = project_dir / "workflow-state.json"
    state_file.write_text(json.dumps(state, indent=2))


def transition_state(project_dir: Path, new_state: WorkflowState) -> dict:
    """
    Transition to a new workflow state.
    
    Raises:
        ValueError: If transition is invalid
    """
    current = load_workflow_state(project_dir)
    current_state = WorkflowState(current["current_state"])
    
    if new_state not in VALID_TRANSITIONS.get(current_state, []):
        raise ValueError(f"Invalid transition: {current_state} -> {new_state}")
    
    current["history"].append({
        "from": current_state.value,
        "to": new_state.value,
        "timestamp": datetime.now().isoformat()
    })
    current["current_state"] = new_state.value
    current["next_agent"] = STATE_TO_AGENT.get(new_state, AgentType.DEV).value
    current["last_transition"] = datetime.now().isoformat()
    
    save_workflow_state(project_dir, current)
    return current


def get_next_agent(project_dir: Path) -> AgentType:
    """Determine which agent should run next."""
    state = load_workflow_state(project_dir)
    return AgentType(state["next_agent"])
```

#### qa_agent.py (NEW)

```python
# Location: qa_agent.py

"""
QA Agent Module
===============

Implements quality gates and story validation for the QA Agent.
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class GateResult:
    gate_name: str
    passed: bool
    duration_ms: int
    errors: List[Dict]
    warnings: List[Dict]


def detect_project_type(project_dir: Path) -> str:
    """Detect if project is Node.js or Python."""
    if (project_dir / "package.json").exists():
        return "node"
    elif (project_dir / "pyproject.toml").exists() or (project_dir / "requirements.txt").exists():
        return "python"
    return "unknown"


def run_lint_gate(project_dir: Path) -> GateResult:
    """Run linting gate based on project type."""
    project_type = detect_project_type(project_dir)
    start = datetime.now()
    errors = []
    
    if project_type == "node":
        result = subprocess.run(
            ["npx", "eslint", ".", "--format", "json"],
            cwd=project_dir,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            try:
                eslint_output = json.loads(result.stdout)
                for file_result in eslint_output:
                    for msg in file_result.get("messages", []):
                        errors.append({
                            "file": file_result["filePath"],
                            "line": msg.get("line", 0),
                            "message": msg.get("message", "Unknown error"),
                            "severity": "error" if msg.get("severity") == 2 else "warning"
                        })
            except json.JSONDecodeError:
                errors.append({"file": "", "line": 0, "message": result.stderr, "severity": "error"})
    
    duration = int((datetime.now() - start).total_seconds() * 1000)
    return GateResult("lint", len(errors) == 0, duration, errors, [])


def run_type_check_gate(project_dir: Path) -> GateResult:
    """Run type checking gate."""
    project_type = detect_project_type(project_dir)
    start = datetime.now()
    errors = []
    
    if project_type == "node":
        result = subprocess.run(
            ["npx", "tsc", "--noEmit"],
            cwd=project_dir,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            for line in result.stdout.split("\n"):
                if "error TS" in line:
                    errors.append({"file": "", "line": 0, "message": line, "severity": "error"})
    
    duration = int((datetime.now() - start).total_seconds() * 1000)
    return GateResult("type_check", len(errors) == 0, duration, errors, [])


def run_unit_test_gate(project_dir: Path) -> GateResult:
    """Run unit tests gate."""
    project_type = detect_project_type(project_dir)
    start = datetime.now()
    errors = []
    
    if project_type == "node":
        # Try vitest first, then jest
        result = subprocess.run(
            ["npx", "vitest", "run", "--reporter=json"],
            cwd=project_dir,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            errors.append({"file": "", "line": 0, "message": result.stderr or "Tests failed", "severity": "error"})
    
    duration = int((datetime.now() - start).total_seconds() * 1000)
    return GateResult("unit_tests", len(errors) == 0, duration, errors, [])


def run_all_gates(project_dir: Path, feature_id: int) -> Dict:
    """Run all quality gates and generate report."""
    gates = {
        "lint": run_lint_gate(project_dir),
        "type_check": run_type_check_gate(project_dir),
        "unit_tests": run_unit_test_gate(project_dir),
    }
    
    # Calculate summary
    passed_count = sum(1 for g in gates.values() if g.passed)
    total_count = len(gates)
    all_passed = passed_count == total_count
    
    # Generate priority fixes
    priority_fixes = []
    for gate in gates.values():
        for error in gate.errors[:3]:  # Top 3 errors per gate
            priority_fixes.append(f"[{gate.gate_name}] {error['file']}:{error['line']} - {error['message']}")
    
    report = {
        "feature_id": feature_id,
        "status": "PASSED" if all_passed else "FAILED",
        "gates": {name: asdict(result) for name, result in gates.items()},
        "summary": f"{passed_count} of {total_count} gates passed",
        "priority_fixes": priority_fixes[:10],  # Top 10 overall
        "timestamp": datetime.now().isoformat(),
    }
    
    # Save report
    report_file = project_dir / "qa-report.json"
    report_file.write_text(json.dumps(report, indent=2))
    
    return report


def update_feature_status(project_dir: Path, feature_id: int, passed: bool, notes: str = "") -> None:
    """Update feature status in feature_list.json (QA Agent only)."""
    feature_file = project_dir / "feature_list.json"
    features = json.loads(feature_file.read_text())
    
    for feature in features:
        if feature.get("id") == feature_id:
            feature["passes"] = passed
            feature["qa_validated"] = True
            feature["last_qa_run"] = datetime.now().isoformat()
            feature["qa_notes"] = notes
            break
    
    feature_file.write_text(json.dumps(features, indent=2))
```

### 1.3 Modified Modules

#### prompts.py (MODIFIED)

```diff
# Location: prompts.py

def load_prompt(name: str) -> str:
    """Load a prompt template from the prompts directory."""
    prompt_path = PROMPTS_DIR / f"{name}.md"
    return prompt_path.read_text()


def get_initializer_prompt() -> str:
    """Load the initializer prompt."""
    return load_prompt("initializer_prompt")


-def get_coding_prompt() -> str:
-    """Load the coding agent prompt."""
-    return load_prompt("coding_prompt")
+def get_dev_prompt() -> str:
+    """Load the dev agent prompt."""
+    return load_prompt("dev_prompt")
+
+
+def get_qa_prompt() -> str:
+    """Load the QA agent prompt."""
+    return load_prompt("qa_prompt")
```

#### security.py (MODIFIED)

```diff
# Location: security.py

ALLOWED_COMMANDS = {
    # File inspection
    "ls", "cat", "head", "tail", "wc", "grep",
    # File operations
    "cp", "mkdir", "chmod",
    # Directory
    "pwd",
    # Node.js development
    "npm", "node", "npx",
    # Version control
    "git",
    # Process management
    "ps", "lsof", "sleep", "pkill",
    # Script execution
    "init.sh",
+   # QA tools (allowed for QA Agent)
+   "eslint", "tsc", "jest", "vitest", "playwright",
+   "ruff", "mypy", "pytest",
}
```

#### agent.py (MODIFIED)

```diff
# Location: agent.py

-from prompts import get_initializer_prompt, get_coding_prompt, copy_spec_to_project
+from prompts import get_initializer_prompt, get_dev_prompt, get_qa_prompt, copy_spec_to_project
+from orchestrator import (
+    load_workflow_state, transition_state, get_next_agent,
+    WorkflowState, AgentType
+)


async def run_autonomous_agent(
    project_dir: Path,
    model: str,
    max_iterations: Optional[int] = None,
) -> None:
    # ... existing setup code ...
    
-   # Check if this is a fresh start or continuation
-   tests_file = project_dir / "feature_list.json"
-   is_first_run = not tests_file.exists()
+   # Load workflow state
+   workflow = load_workflow_state(project_dir)
+   current_state = WorkflowState(workflow["current_state"])
    
-   if is_first_run:
+   if current_state == WorkflowState.START:
        print("Fresh start - will use initializer agent")
        copy_spec_to_project(project_dir)
-   else:
-       print("Continuing existing project")
+       transition_state(project_dir, WorkflowState.INITIALIZER)
+   else:
+       print(f"Continuing from state: {current_state.value}")
        print_progress_summary(project_dir)
    
    # Main loop
    while True:
        iteration += 1
        
-       # Choose prompt based on session type
-       if is_first_run:
-           prompt = get_initializer_prompt()
-           is_first_run = False
-       else:
-           prompt = get_coding_prompt()
+       # Determine next agent from workflow state
+       next_agent = get_next_agent(project_dir)
+       
+       if next_agent == AgentType.INITIALIZER:
+           prompt = get_initializer_prompt()
+           print_session_header(iteration, "INITIALIZER")
+       elif next_agent == AgentType.DEV:
+           prompt = get_dev_prompt()
+           print_session_header(iteration, "DEV AGENT")
+       elif next_agent == AgentType.QA:
+           prompt = get_qa_prompt()
+           print_session_header(iteration, "QA AGENT")
        
        # ... rest of session handling ...
```

---

## Phase 2: Implementation Tasks

### Task Group 1: Core Infrastructure (Priority: P0)

| ID | Task | File | Dependencies | Effort |
|----|------|------|--------------|--------|
| T1.1 | Create `orchestrator.py` module | `orchestrator.py` | None | 45 min |
| T1.2 | Create `qa_agent.py` module | `qa_agent.py` | None | 60 min |
| T1.3 | Create `qa_prompt.md` template | `prompts/qa_prompt.md` | None | 30 min |
| T1.4 | Rename `coding_prompt.md` to `dev_prompt.md` | `prompts/` | None | 5 min |

### Task Group 2: Workflow Integration (Priority: P0)

| ID | Task | File | Dependencies | Effort |
|----|------|------|--------------|--------|
| T2.1 | Update `prompts.py` with new functions | `prompts.py` | T1.3, T1.4 | 15 min |
| T2.2 | Update `security.py` with QA commands | `security.py` | None | 10 min |
| T2.3 | Refactor `agent.py` for orchestration | `agent.py` | T1.1, T2.1 | 45 min |
| T2.4 | Update `autonomous_agent_demo.py` | `autonomous_agent_demo.py` | T2.3 | 20 min |

### Task Group 3: Quality Gates (Priority: P0)

| ID | Task | File | Dependencies | Effort |
|----|------|------|--------------|--------|
| T3.1 | Implement lint gate (ESLint/Ruff) | `qa_agent.py` | T1.2 | 30 min |
| T3.2 | Implement type check gate | `qa_agent.py` | T1.2 | 30 min |
| T3.3 | Implement unit test gate | `qa_agent.py` | T1.2 | 30 min |
| T3.4 | Implement browser automation gate | `qa_agent.py` | T1.2 | 60 min |
| T3.5 | Implement story validation gate | `qa_agent.py` | T1.2 | 45 min |

### Task Group 4: Reporting & Feedback (Priority: P1)

| ID | Task | File | Dependencies | Effort |
|----|------|------|--------------|--------|
| T4.1 | Implement `qa-report.json` generation | `qa_agent.py` | T3.* | 30 min |
| T4.2 | Implement feature status update | `qa_agent.py` | T4.1 | 20 min |
| T4.3 | Add progress tracking for QA | `progress.py` | T4.1 | 20 min |

### Task Group 5: Testing & Documentation (Priority: P1)

| ID | Task | File | Dependencies | Effort |
|----|------|------|--------------|--------|
| T5.1 | Create unit tests for orchestrator | `test_orchestrator.py` | T1.1 | 30 min |
| T5.2 | Create unit tests for qa_agent | `test_qa_agent.py` | T1.2 | 45 min |
| T5.3 | Update README with multi-agent info | `README.md` | All | 30 min |
| T5.4 | Add feature entries to feature_list | `docs/qa-agent-spec.md` | All | 15 min |

### Task Dependency Graph

```
T1.1 ────┬────────────────────────────────► T2.3 ────► T2.4
         │                                    ▲
T1.2 ────┼────► T3.1 ─┬                      │
         │     T3.2 ─┼──► T4.1 ──► T4.2 ─────┤
         │     T3.3 ─┤       │               │
         │     T3.4 ─┤       └──► T4.3 ──────┤
         │     T3.5 ─┘                       │
         │                                    │
T1.3 ────┼──► T2.1 ───────────────────────────┘
T1.4 ────┘
         
T2.2 ──────────────────────────────────────► T2.3

T5.1 ◄──── T1.1
T5.2 ◄──── T1.2
T5.3 ◄──── All
T5.4 ◄──── All
```

### Parallel Execution Opportunities

| Phase | Parallel Tasks | Sequential After |
|-------|---------------|------------------|
| 1 | T1.1, T1.2, T1.3, T1.4, T2.2 | - |
| 2 | T2.1, T3.1, T3.2, T3.3, T3.4, T3.5 | Phase 1 |
| 3 | T2.3, T4.1, T4.2, T4.3 | Phase 2 |
| 4 | T2.4, T5.1, T5.2 | Phase 3 |
| 5 | T5.3, T5.4 | Phase 4 |

---

## Phase 3: Verification Checkpoints

### Checkpoint 1: Infrastructure Complete

- [ ] `orchestrator.py` created with state machine
- [ ] `qa_agent.py` created with basic structure
- [ ] `qa_prompt.md` created
- [ ] `dev_prompt.md` renamed
- [ ] All new files have no syntax errors
- [ ] Git commit: "Add QA Agent infrastructure"

### Checkpoint 2: Workflow Integration Complete

- [ ] `prompts.py` updated with new functions
- [ ] `security.py` updated with QA commands
- [ ] `agent.py` refactored for orchestration
- [ ] State transitions work correctly
- [ ] Can switch between agent types
- [ ] Git commit: "Integrate workflow orchestration"

### Checkpoint 3: Quality Gates Complete

- [ ] Lint gate runs and reports errors
- [ ] Type check gate runs and reports errors
- [ ] Unit test gate runs and reports failures
- [ ] Browser automation gate runs
- [ ] Story validation gate runs
- [ ] All gates produce structured output
- [ ] Git commit: "Implement quality gates"

### Checkpoint 4: Full System Test

- [ ] Fresh project: Initializer → Dev → QA flow works
- [ ] QA failure triggers feedback loop
- [ ] Dev Agent can read qa-report.json
- [ ] Fixed issues pass on re-run
- [ ] Feature marked as passing only by QA
- [ ] workflow-state.json tracks correctly
- [ ] Git commit: "QA Agent feature complete"

### Checkpoint 5: Documentation Complete

- [ ] README updated
- [ ] All tests passing
- [ ] Feature entries added to spec
- [ ] Git commit: "Documentation and tests"

---

## Rollback Plan

### If Integration Fails

1. Revert to two-agent pattern:
   ```bash
   git checkout HEAD~1 -- agent.py prompts.py
   ```

2. Keep new modules but don't use them:
   - `orchestrator.py` and `qa_agent.py` can remain as unused modules

3. Document issues in `claude-progress.txt`:
   - What failed
   - Error messages
   - Suggested fixes for next session

### Preserve Backwards Compatibility

- `get_coding_prompt()` redirects to `get_dev_prompt()`
- If no `workflow-state.json`, fall back to two-agent pattern
- QA Agent is opt-in until fully tested

---

## Security Considerations

### New Bash Commands Required

| Command | Justification | Risk Level |
|---------|---------------|------------|
| `eslint` | JavaScript linting | Low - read-only analysis |
| `tsc` | TypeScript type checking | Low - read-only analysis |
| `jest` | JavaScript unit tests | Low - sandboxed tests |
| `vitest` | JavaScript unit tests | Low - sandboxed tests |
| `playwright` | Browser automation | Medium - network access for browser |
| `ruff` | Python linting | Low - read-only analysis |
| `mypy` | Python type checking | Low - read-only analysis |
| `pytest` | Python unit tests | Low - sandboxed tests |

### Security Review Checklist

- [x] All new commands are read-only or test-only
- [x] No arbitrary command execution
- [x] File operations restricted to project directory
- [x] QA Agent cannot modify source code
- [x] Playwright runs in sandboxed browser

---

## Estimated Timeline

| Phase | Tasks | Effort | Cumulative |
|-------|-------|--------|------------|
| Phase 1: Infrastructure | T1.1-T1.4, T2.2 | 2.5 hrs | 2.5 hrs |
| Phase 2: Quality Gates | T2.1, T3.1-T3.5 | 4 hrs | 6.5 hrs |
| Phase 3: Integration | T2.3, T4.1-T4.3 | 2 hrs | 8.5 hrs |
| Phase 4: Testing | T2.4, T5.1-T5.2 | 2 hrs | 10.5 hrs |
| Phase 5: Documentation | T5.3-T5.4 | 1 hr | 11.5 hrs |

**Total Estimated Effort**: ~12 hours across 3-4 agent sessions

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2025-12-07 | System | Initial plan |


