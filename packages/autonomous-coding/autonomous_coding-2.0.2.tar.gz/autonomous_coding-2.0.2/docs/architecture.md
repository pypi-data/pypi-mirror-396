# Multi-Agent Autonomous Coding System Architecture

**Version**: 2.0.0
**Created**: 2025-12-07
**Status**: Proposed

---

## Executive Summary

This document describes the architecture of the Multi-Agent Autonomous Coding System, an evolution from the original two-agent pattern to a sophisticated multi-agent orchestration system with specialized roles, quality gates, and feedback loops.

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MULTI-AGENT AUTONOMOUS CODING SYSTEM                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         ORCHESTRATOR LAYER                            │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │  Workflow   │  │    State    │  │   Agent     │  │   Quality   │  │   │
│  │  │  Engine     │  │   Machine   │  │  Selector   │  │    Gates    │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                     │                                        │
│                                     ▼                                        │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                          AGENT LAYER                                  │   │
│  │                                                                       │   │
│  │  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐             │   │
│  │  │ INITIALIZER │     │  DEV AGENT  │     │  QA AGENT   │             │   │
│  │  │    AGENT    │     │             │     │             │             │   │
│  │  │             │     │  • Coding   │     │  • Testing  │             │   │
│  │  │ • Setup     │     │  • Features │     │  • Linting  │             │   │
│  │  │ • Planning  │     │  • Fixes    │     │  • Types    │             │   │
│  │  │ • Structure │     │  • Commits  │     │  • Validate │             │   │
│  │  └─────────────┘     └─────────────┘     └─────────────┘             │   │
│  │        │                   │                   │                      │   │
│  └────────┼───────────────────┼───────────────────┼──────────────────────┘   │
│           │                   │                   │                          │
│           ▼                   ▼                   ▼                          │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                      PERSISTENCE LAYER                                │   │
│  │                                                                       │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │  feature_   │  │  workflow-  │  │ qa-report   │  │    Git      │  │   │
│  │  │  list.json  │  │  state.json │  │   .json     │  │  Repository │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │   │
│  │                                                                       │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### 1. Orchestrator Layer

The orchestrator manages the workflow and coordinates agent activities.

```
┌─────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR (orchestrator.py)              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    STATE MACHINE                           │  │
│  │                                                            │  │
│  │  START ──► INITIALIZER ──► DEV_READY ──► DEV              │  │
│  │                                           │                │  │
│  │                                           ▼                │  │
│  │  COMPLETE ◄── QA_PASSED ◄── QA ◄── QA_READY               │  │
│  │       ▲                      │                             │  │
│  │       │                      ▼                             │  │
│  │       └─────────── DEV_FEEDBACK ──► DEV                   │  │
│  │                                                            │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Functions:                                                      │
│  ├── load_workflow_state(project_dir)                           │
│  ├── save_workflow_state(project_dir, state)                    │
│  ├── transition_state(project_dir, new_state)                   │
│  ├── get_next_agent(project_dir) → AgentType                    │
│  └── validate_transition(from_state, to_state) → bool           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Agent Layer

Each agent is a specialized AI instance with specific responsibilities.

#### 2.1 Initializer Agent

```
┌─────────────────────────────────────────────────────────────────┐
│                      INITIALIZER AGENT                           │
├─────────────────────────────────────────────────────────────────┤
│  Prompt: prompts/initializer_prompt.md                          │
│  Session: 1 (first session only)                                 │
│                                                                  │
│  Responsibilities:                                               │
│  ├── Read app_spec.txt                                          │
│  ├── Create feature_list.json (200+ features)                   │
│  ├── Create init.sh (environment setup)                         │
│  ├── Create project structure                                   │
│  ├── Initialize git repository                                  │
│  └── Create README.md                                           │
│                                                                  │
│  Permissions:                                                    │
│  ├── CREATE: feature_list.json, init.sh, structure              │
│  ├── MODIFY: None (read-only after creation)                    │
│  └── DELETE: None                                               │
│                                                                  │
│  Output Artifacts:                                               │
│  ├── feature_list.json (200+ features, all passes: false)       │
│  ├── init.sh (executable setup script)                          │
│  ├── README.md (project documentation)                          │
│  └── .gitignore, package.json, etc.                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### 2.2 Dev Agent

```
┌─────────────────────────────────────────────────────────────────┐
│                         DEV AGENT                                │
├─────────────────────────────────────────────────────────────────┤
│  Prompt: prompts/dev_prompt.md (renamed from coding_prompt.md)  │
│  Session: 2+ (multiple sessions)                                 │
│                                                                  │
│  Responsibilities:                                               │
│  ├── Read feature_list.json for next feature                    │
│  ├── Read qa-report.json for feedback (if exists)               │
│  ├── Implement one feature at a time                            │
│  ├── Write unit tests                                           │
│  ├── Make git commits                                           │
│  └── Signal completion via workflow state                       │
│                                                                  │
│  Permissions:                                                    │
│  ├── CREATE: Source code, tests, configs                        │
│  ├── MODIFY: Source code, tests, configs                        │
│  ├── DELETE: Source code (refactoring)                          │
│  └── FORBIDDEN: feature_list.json "passes" field                │
│                                                                  │
│  Input Artifacts:                                                │
│  ├── feature_list.json (read-only)                              │
│  ├── qa-report.json (feedback from QA)                          │
│  └── claude-progress.txt (session notes)                        │
│                                                                  │
│  Output Artifacts:                                               │
│  ├── Source code files                                          │
│  ├── Test files                                                 │
│  ├── Git commits                                                │
│  └── claude-progress.txt (updated)                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### 2.3 QA Agent

```
┌─────────────────────────────────────────────────────────────────┐
│                          QA AGENT                                │
├─────────────────────────────────────────────────────────────────┤
│  Prompt: prompts/qa_prompt.md (NEW)                             │
│  Session: After each Dev Agent session                           │
│                                                                  │
│  Responsibilities:                                               │
│  ├── Run lint gate (ESLint/Ruff)                                │
│  ├── Run type check gate (TypeScript/Mypy)                      │
│  ├── Run unit test gate (Jest/Pytest)                           │
│  ├── Run browser automation gate (Playwright)                   │
│  ├── Run story validation gate                                  │
│  ├── Generate qa-report.json                                    │
│  ├── Update feature_list.json "passes" field                    │
│  └── Run regression tests on passing features                   │
│                                                                  │
│  Permissions:                                                    │
│  ├── MODIFY: feature_list.json "passes" field ONLY              │
│  ├── CREATE: qa-report.json, screenshots                        │
│  ├── READ: All source code, tests, configs                      │
│  └── FORBIDDEN: Source code modifications                       │
│                                                                  │
│  Input Artifacts:                                                │
│  ├── feature_list.json (for test steps)                         │
│  ├── Source code (read-only)                                    │
│  └── workflow-state.json                                        │
│                                                                  │
│  Output Artifacts:                                               │
│  ├── qa-report.json (detailed results)                          │
│  ├── Screenshots (evidence)                                     │
│  ├── feature_list.json (passes field only)                      │
│  └── workflow-state.json (updated)                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3. Persistence Layer

All state is persisted through files to enable session independence.

```
┌─────────────────────────────────────────────────────────────────┐
│                     PERSISTENCE ARTIFACTS                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ feature_list.json                                            ││
│  │ ├── Single source of truth for features                     ││
│  │ ├── Created by: Initializer Agent                           ││
│  │ ├── Modified by: QA Agent (passes field only)               ││
│  │ └── Read by: All agents                                     ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ workflow-state.json                                          ││
│  │ ├── Current state machine position                          ││
│  │ ├── Next agent to run                                       ││
│  │ ├── Current feature being worked                            ││
│  │ └── State transition history                                ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ qa-report.json                                               ││
│  │ ├── Quality gate results                                    ││
│  │ ├── Error details with file:line                            ││
│  │ ├── Priority fixes list                                     ││
│  │ └── Timestamp and duration                                  ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ claude-progress.txt                                          ││
│  │ ├── Human-readable session notes                            ││
│  │ ├── What was accomplished                                   ││
│  │ ├── Issues encountered                                      ││
│  │ └── Next steps                                              ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Git Repository                                               ││
│  │ ├── Source code history                                     ││
│  │ ├── Commit messages as audit trail                          ││
│  │ └── Rollback capability                                     ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Complete Workflow

```
                              START
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       SESSION 1: INITIALIZER                     │
│                                                                  │
│  Input:  app_spec.txt                                           │
│  Output: feature_list.json, init.sh, project structure          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SESSION 2+: DEV AGENT                        │
│                                                                  │
│  Input:  feature_list.json, qa-report.json (if feedback loop)   │
│  Action: Implement feature, write tests, commit                 │
│  Output: Source code, tests, git commits                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SESSION: QA AGENT                           │
│                                                                  │
│  Input:  Source code, feature_list.json                         │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    QUALITY GATES                            │ │
│  │                                                             │ │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌───────┐ │ │
│  │  │  Lint   │ │  Type   │ │  Unit   │ │ Browser │ │ Story │ │ │
│  │  │  Gate   │ │  Check  │ │  Tests  │ │  Tests  │ │ Valid │ │ │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └───┬───┘ │ │
│  │       │           │           │           │          │      │ │
│  │       └───────────┴───────────┴───────────┴──────────┘      │ │
│  │                              │                               │ │
│  │                              ▼                               │ │
│  │                    ┌─────────────────┐                      │ │
│  │                    │  All Passed?    │                      │ │
│  │                    └────────┬────────┘                      │ │
│  │                             │                               │ │
│  └─────────────────────────────┼───────────────────────────────┘ │
│                                │                                  │
│              ┌─────────────────┴─────────────────┐               │
│              │                                   │               │
│              ▼                                   ▼               │
│  ┌───────────────────────┐         ┌───────────────────────┐   │
│  │        YES            │         │          NO           │   │
│  │  • Update passes:true │         │  • Create qa-report   │   │
│  │  • Next feature       │         │  • Trigger feedback   │   │
│  └───────────────────────┘         └───────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                                │
                 ┌──────────────┴──────────────┐
                 │                             │
                 ▼                             ▼
         [QA_PASSED]                   [DEV_FEEDBACK]
                 │                             │
                 │                             │
    ┌────────────┴────────────┐               │
    │                         │               │
    ▼                         ▼               │
[More Features?]         [COMPLETE]           │
    │                                         │
    │ Yes                                     │
    │                                         │
    └─────────────► DEV AGENT ◄───────────────┘
```

### Feedback Loop Detail

```
┌─────────────────────────────────────────────────────────────────┐
│                        FEEDBACK LOOP                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  DEV AGENT                              QA AGENT                 │
│      │                                      │                    │
│      │  1. Implements feature               │                    │
│      │  ─────────────────────►              │                    │
│      │                                      │                    │
│      │                        2. Runs gates │                    │
│      │                                      │                    │
│      │                        3. Gates FAIL │                    │
│      │                                      │                    │
│      │  4. Creates qa-report.json           │                    │
│      │  ◄─────────────────────              │                    │
│      │                                      │                    │
│      │  ┌─────────────────────────────────┐ │                    │
│      │  │ qa-report.json                  │ │                    │
│      │  │ {                               │ │                    │
│      │  │   "status": "FAILED",           │ │                    │
│      │  │   "gates": {...},               │ │                    │
│      │  │   "priority_fixes": [           │ │                    │
│      │  │     "Fix lint error at X:42",   │ │                    │
│      │  │     "Add missing type at Y:15"  │ │                    │
│      │  │   ]                             │ │                    │
│      │  │ }                               │ │                    │
│      │  └─────────────────────────────────┘ │                    │
│      │                                      │                    │
│      │  5. Reads qa-report.json             │                    │
│      │                                      │                    │
│      │  6. Fixes issues                     │                    │
│      │  ─────────────────────►              │                    │
│      │                                      │                    │
│      │                        7. Re-runs gates                   │
│      │                                      │                    │
│      │                        8. Gates PASS │                    │
│      │                                      │                    │
│      │  9. Updates passes: true             │                    │
│      │  ◄─────────────────────              │                    │
│      │                                      │                    │
│      ▼                                      ▼                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Security Architecture

### Role-Based Access Control Matrix

```
┌─────────────────────────────────────────────────────────────────┐
│                   RBAC PERMISSION MATRIX                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Resource              │ Initializer │  Dev  │   QA   │         │
│  ──────────────────────┼─────────────┼───────┼────────┤         │
│  Source Code           │      -      │  RWD  │   R    │         │
│  feature_list.json     │      C      │   R   │ R/W(*) │         │
│  workflow-state.json   │     RW      │  RW   │   RW   │         │
│  qa-report.json        │      -      │   R   │   RW   │         │
│  init.sh               │      C      │   R   │    R   │         │
│  Git Repository        │      W      │  RW   │    R   │         │
│  Browser               │      -      │   -   │   RW   │         │
│  Lint/Type Tools       │      -      │   -   │    X   │         │
│                                                                  │
│  Legend:                                                         │
│  C = Create only                                                │
│  R = Read                                                       │
│  W = Write                                                      │
│  D = Delete                                                     │
│  X = Execute                                                    │
│  (*) = Only "passes" field                                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Command Allowlist by Agent

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMMAND ALLOWLIST                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ALL AGENTS (Base):                                             │
│  ├── ls, cat, head, tail, wc, grep    # File inspection         │
│  ├── pwd                               # Directory               │
│  ├── git                               # Version control         │
│  ├── ps, lsof, sleep                   # Process info            │
│  └── cp, mkdir                         # File operations         │
│                                                                  │
│  INITIALIZER + DEV AGENTS:                                      │
│  ├── npm, node, npx                    # Node.js                 │
│  ├── pkill                             # Kill dev servers        │
│  ├── chmod +x                          # Make scripts executable │
│  └── ./init.sh                         # Run init script         │
│                                                                  │
│  QA AGENT (Additional):                                         │
│  ├── eslint                            # JS/TS linting           │
│  ├── tsc                               # TypeScript check        │
│  ├── jest, vitest                      # JS/TS testing           │
│  ├── playwright                        # Browser automation      │
│  ├── ruff                              # Python linting          │
│  ├── mypy                              # Python type check       │
│  └── pytest                            # Python testing          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quality Gates Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    QUALITY GATES PIPELINE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ GATE 1: LINT CHECK                                          ││
│  │ ├── Tool: ESLint (JS/TS) or Ruff (Python)                   ││
│  │ ├── Criteria: Zero errors                                   ││
│  │ ├── Timeout: 60 seconds                                     ││
│  │ └── Output: List of errors with file:line:message           ││
│  └─────────────────────────────────────────────────────────────┘│
│                           │                                      │
│                           ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ GATE 2: TYPE CHECK                                          ││
│  │ ├── Tool: TypeScript (JS/TS) or Mypy (Python)               ││
│  │ ├── Criteria: Zero type errors                              ││
│  │ ├── Timeout: 120 seconds                                    ││
│  │ └── Output: List of type errors with locations              ││
│  └─────────────────────────────────────────────────────────────┘│
│                           │                                      │
│                           ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ GATE 3: UNIT TESTS                                          ││
│  │ ├── Tool: Jest/Vitest (JS/TS) or Pytest (Python)            ││
│  │ ├── Criteria: 100% pass rate                                ││
│  │ ├── Timeout: 300 seconds                                    ││
│  │ └── Output: Test results with failures detailed             ││
│  └─────────────────────────────────────────────────────────────┘│
│                           │                                      │
│                           ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ GATE 4: BROWSER AUTOMATION                                  ││
│  │ ├── Tool: Playwright                                        ││
│  │ ├── Criteria: All E2E scenarios pass                        ││
│  │ ├── Timeout: 600 seconds                                    ││
│  │ ├── Screenshots: Captured at each step                      ││
│  │ └── Output: Pass/fail with console errors                   ││
│  └─────────────────────────────────────────────────────────────┘│
│                           │                                      │
│                           ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ GATE 5: STORY VALIDATION                                    ││
│  │ ├── Source: feature_list.json test steps                    ││
│  │ ├── Criteria: All acceptance criteria met                   ││
│  │ ├── Evidence: Screenshots for each step                     ││
│  │ └── Output: Step-by-step validation report                  ││
│  └─────────────────────────────────────────────────────────────┘│
│                           │                                      │
│                           ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    FINAL VERDICT                             ││
│  │                                                              ││
│  │  ALL PASSED ──► Update passes: true ──► Next feature        ││
│  │                                                              ││
│  │  ANY FAILED ──► Generate qa-report.json ──► Feedback loop   ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## File Structure

### Project Root (After Implementation)

```
autonomous-coding/
├── autonomous_agent_demo.py    # Entry point
├── agent.py                    # Session logic
├── client.py                   # Claude SDK client
├── orchestrator.py             # NEW: Workflow orchestration
├── qa_agent.py                 # NEW: QA gate implementations
├── security.py                 # Command allowlist
├── progress.py                 # Progress tracking
├── prompts.py                  # Prompt loading
│
├── prompts/
│   ├── app_spec.txt            # Application specification
│   ├── initializer_prompt.md   # Initializer agent prompt
│   ├── dev_prompt.md           # RENAMED: Dev agent prompt
│   └── qa_prompt.md            # NEW: QA agent prompt
│
├── docs/
│   ├── constitution.md         # UPDATED: Multi-agent constitution
│   ├── architecture.md         # NEW: This document
│   ├── qa-agent-spec.md        # NEW: QA agent specification
│   ├── qa-agent-plan.md        # NEW: QA agent implementation plan
│   ├── spec.md                 # Feature spec template
│   └── plan.md                 # Implementation plan template
│
├── tests/
│   ├── test_orchestrator.py    # NEW: Orchestrator tests
│   ├── test_qa_agent.py        # NEW: QA agent tests
│   └── test_security.py        # Security hook tests
│
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

### Generated Project Structure

```
my_project/                     # Generated by agents
├── feature_list.json           # Feature definitions
├── workflow-state.json         # NEW: Workflow state
├── qa-report.json              # NEW: QA reports
├── app_spec.txt                # Copied specification
├── init.sh                     # Environment setup
├── claude-progress.txt         # Session notes
├── .claude_settings.json       # Security settings
│
├── src/                        # Application source
├── tests/                      # Test files
├── screenshots/                # NEW: QA evidence
└── [application files]         # Generated code
```

---

## Future Enhancements

### Phase 2: Advanced Features

```
┌─────────────────────────────────────────────────────────────────┐
│                    FUTURE ENHANCEMENTS                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. ARCHITECT AGENT                                             │
│     ├── Code review                                             │
│     ├── Architecture decisions                                  │
│     ├── Refactoring recommendations                             │
│     └── Technical debt tracking                                 │
│                                                                  │
│  2. SECURITY AGENT                                              │
│     ├── Vulnerability scanning                                  │
│     ├── Dependency audit                                        │
│     ├── Secret detection                                        │
│     └── OWASP compliance                                        │
│                                                                  │
│  3. PERFORMANCE AGENT                                           │
│     ├── Load testing                                            │
│     ├── Performance profiling                                   │
│     ├── Bundle size analysis                                    │
│     └── Lighthouse audits                                       │
│                                                                  │
│  4. DOCUMENTATION AGENT                                         │
│     ├── API documentation                                       │
│     ├── Code comments                                           │
│     ├── README generation                                       │
│     └── Changelog maintenance                                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-12-07 | System | Initial two-agent architecture |
| 2.0.0 | 2025-12-07 | System | Multi-agent with QA Agent, orchestration, quality gates |

