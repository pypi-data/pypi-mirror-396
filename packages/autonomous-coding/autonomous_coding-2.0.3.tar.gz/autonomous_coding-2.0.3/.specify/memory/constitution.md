<!--
SYNC IMPACT REPORT
==================
Version Change: Initial template → 2.0.0
Modified Principles: Template replaced with concrete principles from docs/constitution.md
Added Sections:
  - Overview section
  - Workflow State Machine section
  - Glossary section
  - Appendix A: Agent Prompt Templates
  - Appendix B: Quality Gate Tools
  - Version History table
Removed Sections:
  - Generic template placeholders
Templates Status:
  ✅ plan-template.md - Reviewed, constitution check section aligns with quality gates
  ✅ spec-template.md - Reviewed, user story prioritization aligns with incremental progress principle
  ✅ tasks-template.md - Reviewed, phase structure supports session independence and parallel work
  ⚠️  No command files found in .specify/templates/commands/ - skipping command file validation
Follow-up TODOs:
  - None - all placeholders filled with concrete values
==================
-->

# Autonomous Coding Agent Constitution

**Version**: 2.0.0 | **Ratified**: 2025-12-07 | **Last Amended**: 2025-12-07

---

## Overview

This constitution defines the non-negotiable principles, governance rules, and development standards for the Multi-Agent Autonomous Coding System. All feature specifications, implementation plans, and code changes MUST align with these principles.

The system enables AI agents to autonomously build complete applications over multiple sessions through coordinated multi-agent orchestration, strict quality gates, and persistent state management.

---

## Core Principles

### I. Multi-Agent Orchestration

The system operates as a coordinated multi-agent architecture with specialized roles. Each agent type has exclusive responsibilities and operates independently within its scope.

**Agent Roles:**

| Agent | Role | Responsibilities |
|-------|------|------------------|
| **Orchestrator** | Workflow Coordinator | Manages agent transitions, state machine, quality gates |
| **Initializer** | Project Setup | Creates feature_list.json, init.sh, project structure |
| **Dev Agent** | Implementation | Writes code, implements features |
| **QA Agent** | Quality Assurance | Testing, linting, type checking, story validation |

**Key Rules:**
- Agents MUST operate independently within their scope
- Inter-agent communication happens ONLY through shared artifacts
- Only the Orchestrator can transition between agent types
- Each agent type has exclusive permissions (see Principle II)

**Rationale**: Separation of concerns improves quality and prevents conflicts between development and validation activities. This architectural pattern enables parallel work and ensures independent validation of all code.

### II. Role-Based Access Control (RBAC)

Each agent has specific permissions and restrictions that MUST be enforced at all times.

**Permission Matrix:**

| Agent | Can Modify | Cannot Modify |
|-------|------------|---------------|
| **Initializer** | feature_list.json (create only), init.sh, project structure | Existing features, passes status |
| **Dev Agent** | Source code files, configurations | feature_list.json, test results |
| **QA Agent** | `passes` field only, qa-report.json, lint/type reports | Source code, feature definitions |

**Critical Rules:**
- Only QA Agent can change `"passes": false` to `"passes": true`
- Dev Agent CANNOT mark features as passing under any circumstances
- This separation MUST be maintained to ensure all code is independently validated

**Rationale**: Prevents self-certification and ensures genuine quality validation. This principle is non-negotiable as it forms the foundation of trustworthy autonomous development.

### III. Session Independence & State Persistence

Each agent operates in a fresh context window with no memory of previous sessions. All state MUST be persisted through artifacts.

**Persistence Artifacts:**

| Artifact | Purpose | Owner |
|----------|---------|-------|
| `feature_list.json` | Feature definitions and status | Initializer (create), QA (update passes) |
| `qa-report.json` | QA findings, test results, lint/type errors | QA Agent |
| `claude-progress.txt` | Session notes for continuity | All agents |
| `workflow-state.json` | Current workflow state and next agent | Orchestrator |
| Git commits | Code history and checkpoints | Dev Agent |

**Mandatory Rules:**
- Agents MUST begin with orientation to understand current state
- Agents MUST end with clean state and updated progress notes
- Agents MUST NEVER assume state from previous sessions

**Rationale**: Long-running tasks exceed single context windows. Persistence enables unlimited continuation across sessions, allowing autonomous agents to build complete applications over time.

### IV. Quality Gates

Features MUST pass through ALL quality gates before completion. No exceptions.

**Quality Gate Pipeline:**

```
┌─────────────────────────────────────────────────────────────────┐
│                      QUALITY GATE PIPELINE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Gate 1: Lint Check                                              │
│    ├── ESLint (JS/TS)                                           │
│    ├── Pylint/Ruff (Python)                                     │
│    └── MUST pass with 0 errors                                  │
│                                                                  │
│  Gate 2: Type Check                                              │
│    ├── TypeScript (tsc --noEmit)                                │
│    ├── Python (mypy/pyright)                                    │
│    └── MUST pass with 0 errors                                  │
│                                                                  │
│  Gate 3: Unit Tests                                              │
│    ├── Jest/Vitest (JS/TS)                                      │
│    ├── Pytest (Python)                                          │
│    └── MUST pass 100%                                           │
│                                                                  │
│  Gate 4: Browser Automation Tests                                │
│    ├── E2E user flow verification                               │
│    ├── Screenshot capture                                       │
│    └── Zero console errors                                      │
│                                                                  │
│  Gate 5: Story Validation                                        │
│    ├── All acceptance criteria verified                         │
│    ├── Test steps executed successfully                         │
│    └── Visual appearance matches spec                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Enforcement Rules:**
- All gates MUST pass before marking feature complete
- Any gate failure MUST trigger feedback loop to Dev Agent
- QA Agent MUST document all findings in qa-report.json

**Rationale**: Multiple validation layers catch different types of issues. This comprehensive approach ensures production-quality code with zero tolerance for technical debt.

### V. Feedback Loop Protocol

When QA Agent finds issues, a structured feedback loop MUST be triggered to guide Dev Agent fixes.

**Feedback Flow:**

```
Dev Agent                    QA Agent
    │                            │
    │  Implements Feature        │
    │ ────────────────────────►  │
    │                            │
    │                     Runs Quality Gates
    │                            │
    │    ◄──── PASS ────────────│
    │         (marks passes:true)│
    │                            │
    │    ◄──── FAIL ────────────│
    │    (qa-report.json)        │
    │                            │
    │  Reads qa-report.json      │
    │  Fixes Issues              │
    │                            │
    │  Re-submits ──────────────►│
    │                            │
```

**QA Report Schema (qa-report.json):**

```json
{
  "feature_id": 42,
  "status": "FAILED",
  "gates": {
    "lint": { "passed": false, "errors": [...] },
    "type_check": { "passed": true },
    "unit_tests": { "passed": true },
    "browser_tests": { "passed": false, "errors": [...] },
    "story_validation": { "passed": false, "issues": [...] }
  },
  "summary": "2 of 5 gates failed",
  "priority_fixes": [
    "Fix ESLint error in src/components/Chat.tsx:42",
    "Console error: undefined is not a function in message handler"
  ],
  "timestamp": "2025-12-07T10:30:00Z"
}
```

**Rationale**: Structured feedback ensures Dev Agent can efficiently address issues without ambiguity. Clear, actionable reports minimize iteration cycles and improve development velocity.

### VI. Single Source of Truth

`feature_list.json` is the authoritative record of ALL features and their implementation status.

**Immutability Rules:**
- Contains 200+ detailed end-to-end test cases
- Features are NEVER removed or edited after initial creation
- Only the `"passes"` field may be modified (by QA Agent only)
- Features MUST be ordered by priority (fundamental features first)

**Extended Schema with QA Fields:**

```json
{
  "id": 1,
  "category": "functional",
  "description": "Feature description",
  "steps": ["Step 1", "Step 2", "Step 3"],
  "passes": false,
  "qa_validated": false,
  "last_qa_run": null,
  "qa_notes": null
}
```

**Rationale**: Preventing feature drift and ensuring complete traceability. The immutability of feature definitions ensures consistent validation criteria across all sessions.

### VII. Security First

All operations MUST respect security constraints. Unauthorized commands are blocked.

**Allowed Commands:**

```
ls, cat, head, tail, wc, grep     # File inspection
npm, node, npx                     # Node.js operations
git                                # Version control
ps, lsof, sleep, pkill             # Process management (dev processes only)
cp, mkdir, chmod                   # File operations (restricted)
eslint, tsc, jest, vitest          # QA tools (QA Agent only)
pytest, mypy, ruff                 # Python QA tools
```

**Agent-Specific Command Extensions:**

| Agent | Additional Allowed Commands |
|-------|---------------------------|
| QA Agent | `eslint`, `tsc`, `jest`, `vitest`, `pytest`, `mypy`, `ruff`, `playwright` |

**Rationale**: Autonomous agents MUST operate within strict security boundaries. The allowlist approach prevents malicious or unintended system modifications while enabling necessary development operations.

### VIII. Quality Over Speed

Production-quality is the ONLY acceptable standard. Technical debt is not permitted.

**Quality Requirements (ALL mandatory):**
- Zero console errors
- Zero lint errors
- Zero type errors
- Polished UI matching design specifications exactly
- All features work end-to-end through the UI
- Fast, responsive, professional appearance
- Fix broken tests before implementing new features

**Rationale**: Unlimited time across sessions means there is no excuse for technical debt. Quality is never sacrificed for speed in autonomous development.

### IX. Incremental Progress

Each session MUST complete measurable work and prepare for the next session.

**Session Requirements:**
- Complete at least one feature perfectly
- Make progress that can be continued by the next session
- Commit all working code with descriptive messages
- Update progress notes for future agents

**Session Handoff Protocol:**

1. Commit all changes
2. Update `claude-progress.txt` with session summary
3. Update `workflow-state.json` with next agent type
4. Ensure clean working state (no uncommitted changes)

**Rationale**: Small, verified increments compound into complete applications. Clean handoffs enable seamless continuation across sessions and context windows.

---

## Workflow State Machine

The system follows a strict state machine for workflow coordination:

```
                    ┌─────────────────────────────────────────────────┐
                    │              WORKFLOW STATE MACHINE              │
                    └─────────────────────────────────────────────────┘

    ┌─────────┐     ┌─────────────┐     ┌───────────┐     ┌──────────┐
    │  START  │────►│ INITIALIZER │────►│ DEV_READY │────►│   DEV    │
    └─────────┘     └─────────────┘     └───────────┘     └────┬─────┘
                                                               │
                                                               │ Feature
                                                               │ Implemented
                                                               ▼
    ┌─────────┐     ┌─────────────┐     ┌───────────┐     ┌──────────┐
    │COMPLETE │◄────│  QA_PASSED  │◄────│    QA     │◄────│ QA_READY │
    └─────────┘     └─────────────┘     └─────┬─────┘     └──────────┘
         ▲                                    │
         │                                    │ QA Failed
         │                                    ▼
         │               ┌───────────────────────────────┐
         │               │         DEV_FEEDBACK          │
         │               │   (qa-report.json created)    │
         │               └───────────────┬───────────────┘
         │                               │
         │                               │ Dev fixes issues
         │                               ▼
         │                          ┌──────────┐
         └──────────────────────────│   DEV    │
                                    └──────────┘
```

**State Definitions:**

| State | Description | Next Agent |
|-------|-------------|------------|
| `START` | Fresh project | Initializer |
| `INITIALIZER` | Setting up project | - |
| `DEV_READY` | Ready for development | Dev Agent |
| `DEV` | Feature being implemented | - |
| `QA_READY` | Feature ready for QA | QA Agent |
| `QA` | Running quality gates | - |
| `QA_PASSED` | All gates passed | Dev Agent (next feature) |
| `DEV_FEEDBACK` | QA found issues | Dev Agent |
| `COMPLETE` | All features done | - |

---

## Governance

### Amendment Procedure

1. Propose changes with clear rationale
2. Review impact on existing specifications and plans
3. Version bump according to semantic versioning:
   - **MAJOR**: Backward-incompatible governance/principle changes
   - **MINOR**: New principle/section added or materially expanded guidance
   - **PATCH**: Clarifications, wording, typo fixes, non-semantic refinements
4. Update dependent artifacts to maintain alignment

### Compliance Review

- All new features MUST be reviewed against constitutional principles
- Non-compliance automatically blocks implementation
- Constitution conflicts require specification adjustment, not principle dilution

### Version History

| Version | Date | Type | Description |
|---------|------|------|-------------|
| 1.0.0 | 2025-12-07 | MAJOR | Initial constitution (two-agent pattern) |
| 2.0.0 | 2025-12-07 | MAJOR | Multi-agent architecture with QA Agent, quality gates, RBAC |

---

## Glossary

| Term | Definition |
|------|------------|
| **Agent** | An AI coding assistant operating within a single context window |
| **Session** | A single context window execution, typically bounded by token limits |
| **Feature** | A discrete, testable unit of functionality defined in feature_list.json |
| **Quality Gate** | A validation checkpoint that MUST pass before proceeding |
| **Brownfield** | An existing project with established architecture and patterns |
| **Verification** | Browser automation testing confirming feature implementation |
| **RBAC** | Role-Based Access Control - agents have specific permissions |
| **Feedback Loop** | Process where QA findings are sent back to Dev Agent for fixing |

---

## Appendix A: Agent Prompt Templates

Each agent type uses a specialized prompt loaded from `prompts/`:

- `initializer_prompt.md` - Project setup agent
- `coding_prompt.md` → `dev_prompt.md` - Development agent
- `qa_prompt.md` - Quality assurance agent

---

## Appendix B: Quality Gate Tools

| Gate | Tool | Configuration |
|------|------|---------------|
| Lint (JS/TS) | ESLint | `.eslintrc.json` |
| Lint (Python) | Ruff | `pyproject.toml` |
| Type (JS/TS) | TypeScript | `tsconfig.json` |
| Type (Python) | Mypy | `mypy.ini` |
| Unit Test | Jest/Vitest/Pytest | `jest.config.js` / `vitest.config.js` / `pytest.ini` |
| E2E Test | Playwright | Browser automation |
