# Feature Specification: QA Agent

**Feature Branch**: `001-qa-agent`
**Created**: 2025-12-07
**Status**: Draft
**Constitution Compliance**: ✅ Verified against v2.0.0

---

## Overview

Introduce a dedicated Quality Assurance (QA) Agent to the autonomous coding system. The QA Agent is responsible for independently validating all work done by the Dev Agent through comprehensive testing, linting, type checking, and story validation. This agent ensures that no feature is marked as complete without passing rigorous quality gates.

**Problem Statement**: Currently, the Dev Agent both implements and validates its own work, which violates the principle of independent verification and can lead to self-certification bias.

**Value Proposition**: 
- Independent quality validation increases confidence in feature completeness
- Automated quality gates catch issues before they compound
- Structured feedback loop enables efficient issue resolution
- Clear separation of concerns improves overall code quality

---

## User Scenarios & Testing

### User Story 1 - QA Agent Runs Quality Gates (Priority: P0)

**As a** system orchestrator,
**I want** the QA Agent to run all quality gates on implemented features,
**So that** code quality is independently verified before marking features complete.

**Acceptance Criteria:**
- [ ] QA Agent can run ESLint/Ruff for linting
- [ ] QA Agent can run TypeScript/Mypy for type checking
- [ ] QA Agent can run Jest/Pytest for unit tests
- [ ] QA Agent can run Playwright for browser automation tests
- [ ] All gates must pass before feature is marked complete
- [ ] Results are logged to `qa-report.json`

**Testing Steps:**
1. Have Dev Agent implement a feature with intentional lint error
2. Trigger QA Agent to run quality gates
3. Verify lint gate fails and is reported
4. Verify `qa-report.json` contains detailed error information
5. Verify feature `passes` remains `false`
6. Fix the lint error and re-run QA
7. Verify all gates pass
8. Verify feature `passes` is now `true`
9. Take screenshots of terminal output

**Why this priority**: Core functionality - QA Agent is useless without quality gates.

---

### User Story 2 - QA Agent Creates Feedback Report (Priority: P0)

**As a** Dev Agent,
**I want** detailed feedback reports when QA fails,
**So that** I can efficiently identify and fix issues.

**Acceptance Criteria:**
- [ ] `qa-report.json` is created/updated after each QA run
- [ ] Report includes pass/fail status for each gate
- [ ] Report includes specific error messages with file:line references
- [ ] Report includes prioritized list of fixes
- [ ] Report is readable by subsequent Dev Agent sessions

**Testing Steps:**
1. Create a feature with multiple types of issues (lint, type, test failure)
2. Run QA Agent
3. Verify `qa-report.json` is created
4. Verify report contains all issue types
5. Verify error messages include file paths and line numbers
6. Verify priority fixes section is populated
7. Verify Dev Agent can read and act on the report

**Why this priority**: Feedback mechanism is essential for the loop to function.

---

### User Story 3 - QA Agent Performs Story Validation (Priority: P1)

**As a** product owner,
**I want** the QA Agent to validate features against user story acceptance criteria,
**So that** implemented features actually fulfill requirements.

**Acceptance Criteria:**
- [ ] QA Agent reads feature definition from `feature_list.json`
- [ ] QA Agent executes all test steps defined in feature
- [ ] QA Agent verifies acceptance criteria are met
- [ ] QA Agent captures screenshots at each step
- [ ] QA Agent reports which steps passed/failed

**Testing Steps:**
1. Define a feature with 5+ test steps
2. Implement the feature
3. Run QA Agent story validation
4. Verify each test step is executed
5. Verify screenshots are captured
6. Verify step-by-step results are reported
7. Verify overall pass/fail is accurate

**Why this priority**: Story validation ensures features meet requirements, not just code quality.

---

### User Story 4 - QA Agent Updates Feature Status (Priority: P1)

**As a** system,
**I want** only the QA Agent to mark features as passing,
**So that** we ensure independent verification.

**Acceptance Criteria:**
- [ ] Dev Agent cannot modify `passes` field in `feature_list.json`
- [ ] QA Agent can only modify `passes` field (not feature definitions)
- [ ] QA Agent also updates `qa_validated` and `last_qa_run` fields
- [ ] Audit trail is maintained in git commits

**Testing Steps:**
1. Attempt to modify `passes` field with Dev Agent prompt
2. Verify the modification is blocked or reverted
3. Run QA Agent on a passing feature
4. Verify `passes` is updated to `true`
5. Verify `qa_validated` is set to `true`
6. Verify `last_qa_run` has timestamp
7. Verify git commit shows QA Agent as author

**Why this priority**: RBAC enforcement is critical for separation of concerns.

---

### User Story 5 - QA Agent Handles Browser Automation (Priority: P1)

**As a** QA Agent,
**I want** to test features through browser automation,
**So that** I can verify end-to-end user experience.

**Acceptance Criteria:**
- [ ] QA Agent can navigate to the application URL
- [ ] QA Agent can interact with UI elements (click, type, scroll)
- [ ] QA Agent can capture screenshots at each step
- [ ] QA Agent can check for console errors
- [ ] QA Agent can verify visual appearance

**Testing Steps:**
1. Start the application via `init.sh`
2. Run QA Agent browser tests
3. Verify navigation to application
4. Verify click interactions work
5. Verify form input works
6. Verify screenshots are captured
7. Verify console errors are detected and reported
8. Take screenshot of final page state

**Why this priority**: Browser automation is the gold standard for E2E verification.

---

### User Story 6 - Orchestrator Manages Agent Transitions (Priority: P1)

**As a** system orchestrator,
**I want** to manage transitions between Dev and QA agents,
**So that** the workflow follows the defined state machine.

**Acceptance Criteria:**
- [ ] `workflow-state.json` tracks current state and next agent
- [ ] Transitions follow the state machine defined in constitution
- [ ] Invalid transitions are blocked
- [ ] State changes are logged

**Testing Steps:**
1. Start fresh project (state: START)
2. Verify Initializer runs (state: INITIALIZER → DEV_READY)
3. Verify Dev Agent runs (state: DEV)
4. Complete feature implementation
5. Verify transition to QA_READY
6. Run QA Agent (state: QA)
7. Verify transition based on QA result (QA_PASSED or DEV_FEEDBACK)
8. Verify state machine is followed correctly

**Why this priority**: Orchestration ensures correct agent sequencing.

---

### User Story 7 - QA Agent Detects Regressions (Priority: P2)

**As a** QA Agent,
**I want** to detect regressions in previously passing features,
**So that** new changes don't break existing functionality.

**Acceptance Criteria:**
- [ ] QA Agent runs regression tests on all `passes: true` features
- [ ] Regressions are reported immediately
- [ ] Regressed features are marked as `passes: false`
- [ ] Regression report includes which commit introduced the issue

**Testing Steps:**
1. Have 3+ features marked as passing
2. Introduce a change that breaks one feature
3. Run QA regression suite
4. Verify regression is detected
5. Verify feature is marked as failing
6. Verify report identifies the breaking change
7. Verify Dev Agent receives feedback

**Why this priority**: Regression detection prevents quality degradation over time.

---

### User Story 8 - QA Agent Generates Test Reports (Priority: P2)

**As a** project stakeholder,
**I want** comprehensive test reports,
**So that** I can track quality metrics over time.

**Acceptance Criteria:**
- [ ] Summary report shows pass/fail counts by category
- [ ] Coverage metrics are tracked
- [ ] Historical trend data is maintained
- [ ] Report is human-readable (Markdown format)

**Testing Steps:**
1. Run QA Agent on multiple features
2. Verify summary report is generated
3. Verify pass/fail counts are accurate
4. Verify category breakdown (functional, style, etc.)
5. Verify historical data is appended
6. Review report readability

**Why this priority**: Reporting enables progress tracking and quality visibility.

---

## Feature List Entries

```json
[
  {
    "id": 201,
    "category": "functional",
    "description": "QA Agent - Run ESLint linting gate",
    "steps": [
      "Step 1: Create file with intentional lint error",
      "Step 2: Run QA Agent lint gate",
      "Step 3: Verify lint error is detected",
      "Step 4: Verify error is logged to qa-report.json",
      "Step 5: Fix lint error",
      "Step 6: Re-run lint gate",
      "Step 7: Verify gate passes"
    ],
    "passes": false
  },
  {
    "id": 202,
    "category": "functional",
    "description": "QA Agent - Run TypeScript type checking gate",
    "steps": [
      "Step 1: Create file with type error",
      "Step 2: Run QA Agent type check gate",
      "Step 3: Verify type error is detected",
      "Step 4: Verify error includes file:line reference",
      "Step 5: Fix type error",
      "Step 6: Verify gate passes"
    ],
    "passes": false
  },
  {
    "id": 203,
    "category": "functional",
    "description": "QA Agent - Run unit test gate",
    "steps": [
      "Step 1: Create failing unit test",
      "Step 2: Run QA Agent test gate",
      "Step 3: Verify test failure is detected",
      "Step 4: Verify failure details are logged",
      "Step 5: Fix the test",
      "Step 6: Verify gate passes"
    ],
    "passes": false
  },
  {
    "id": 204,
    "category": "functional",
    "description": "QA Agent - Run browser automation tests",
    "steps": [
      "Step 1: Start application",
      "Step 2: Run QA Agent browser tests",
      "Step 3: Navigate to application",
      "Step 4: Perform user interactions",
      "Step 5: Capture screenshots",
      "Step 6: Check for console errors",
      "Step 7: Verify results are logged"
    ],
    "passes": false
  },
  {
    "id": 205,
    "category": "functional",
    "description": "QA Agent - Story validation against acceptance criteria",
    "steps": [
      "Step 1: Read feature definition from feature_list.json",
      "Step 2: Execute test steps",
      "Step 3: Verify each acceptance criterion",
      "Step 4: Capture evidence (screenshots)",
      "Step 5: Report step-by-step results"
    ],
    "passes": false
  },
  {
    "id": 206,
    "category": "functional",
    "description": "QA Agent - Create detailed feedback report (qa-report.json)",
    "steps": [
      "Step 1: Run all quality gates",
      "Step 2: Verify qa-report.json is created",
      "Step 3: Verify gate statuses are recorded",
      "Step 4: Verify error details include file:line",
      "Step 5: Verify priority fixes are listed",
      "Step 6: Verify timestamp is accurate"
    ],
    "passes": false
  },
  {
    "id": 207,
    "category": "functional",
    "description": "QA Agent - Update feature status in feature_list.json",
    "steps": [
      "Step 1: Run QA on implemented feature",
      "Step 2: All gates pass",
      "Step 3: Verify passes field changes to true",
      "Step 4: Verify qa_validated is true",
      "Step 5: Verify last_qa_run has timestamp",
      "Step 6: Verify git commit is made"
    ],
    "passes": false
  },
  {
    "id": 208,
    "category": "functional",
    "description": "QA Agent - RBAC enforcement (Dev cannot mark passing)",
    "steps": [
      "Step 1: Attempt to modify passes with Dev Agent",
      "Step 2: Verify modification is blocked",
      "Step 3: Run QA Agent",
      "Step 4: Verify only QA can modify passes"
    ],
    "passes": false
  },
  {
    "id": 209,
    "category": "functional",
    "description": "Orchestrator - State machine transitions",
    "steps": [
      "Step 1: Verify START → INITIALIZER transition",
      "Step 2: Verify INITIALIZER → DEV_READY transition",
      "Step 3: Verify DEV → QA_READY transition",
      "Step 4: Verify QA → QA_PASSED (on success)",
      "Step 5: Verify QA → DEV_FEEDBACK (on failure)",
      "Step 6: Verify workflow-state.json updates"
    ],
    "passes": false
  },
  {
    "id": 210,
    "category": "functional",
    "description": "QA Agent - Regression detection",
    "steps": [
      "Step 1: Have 3 features passing",
      "Step 2: Introduce breaking change",
      "Step 3: Run regression suite",
      "Step 4: Verify regression detected",
      "Step 5: Verify feature marked as failing",
      "Step 6: Verify report identifies breaking commit"
    ],
    "passes": false
  },
  {
    "id": 211,
    "category": "style",
    "description": "QA Agent - Generate human-readable test report",
    "steps": [
      "Step 1: Run QA on multiple features",
      "Step 2: Verify summary report generated",
      "Step 3: Verify pass/fail counts accurate",
      "Step 4: Verify category breakdown included",
      "Step 5: Verify Markdown format is readable"
    ],
    "passes": false
  },
  {
    "id": 212,
    "category": "functional",
    "description": "QA Agent - Full feedback loop (fail → fix → pass)",
    "steps": [
      "Step 1: Implement feature with issues",
      "Step 2: Run QA (expect failure)",
      "Step 3: Verify qa-report.json created",
      "Step 4: Dev Agent reads report",
      "Step 5: Dev Agent fixes issues",
      "Step 6: Re-run QA",
      "Step 7: Verify all gates pass",
      "Step 8: Verify feature marked complete",
      "Step 9: Take screenshots throughout"
    ],
    "passes": false
  }
]
```

---

## Constitution Compliance Checklist

- [x] **I. Multi-Agent Orchestration**: QA Agent is a new specialized role in the architecture
- [x] **II. Role-Based Access Control**: QA Agent has exclusive permission to update passes field
- [x] **III. Session Independence**: qa-report.json enables cross-session communication
- [x] **IV. Quality Gates**: Feature implements the 5 quality gates defined in constitution
- [x] **V. Feedback Loop Protocol**: Detailed feedback reports enable Dev Agent fixes
- [x] **VI. Single Source of Truth**: feature_list.json schema extended with QA fields
- [x] **VII. Security First**: QA commands added to agent-specific allowlist
- [x] **VIII. Quality Over Speed**: Multiple validation layers ensure production quality
- [x] **IX. Incremental Progress**: Each QA run produces actionable results

---

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| Initializer Agent | ✅ Implemented | Creates feature_list.json |
| Dev Agent | ✅ Implemented | Implements features |
| Browser automation tools | ✅ Available | Playwright/Puppeteer |
| Lint/type tools | 🔄 To be configured | ESLint, TypeScript, Ruff, Mypy |

---

## Out of Scope

- AI-based test generation (future feature)
- Performance testing (future feature)
- Security scanning (future feature)
- Cross-browser testing (future feature)
- Mobile testing (future feature)

---

## Open Questions

1. **Q**: Should QA Agent run automatically after Dev Agent completes, or be triggered manually?
   **A**: Automatically triggered by Orchestrator when workflow enters QA_READY state.

2. **Q**: How do we handle flaky tests?
   **A**: Retry up to 3 times before marking as failed. Log flakiness in report.

3. **Q**: Should QA Agent have different strictness levels?
   **A**: Initially strict (all gates must pass). Consider configurable strictness in future.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2025-12-07 | System | Initial draft |

