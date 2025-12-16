# Implementation Plan: [NEW_FEATURE_NAME]

**Feature Branch**: `NNN-feature-name`
**Spec Reference**: `docs/spec.md`
**Created**: 2025-12-07
**Status**: Draft

---

## Technical Context

### Existing Architecture

<!-- 
Document the current architecture relevant to this feature.
Reference existing code patterns and modules.
-->

| Component | Location | Description |
|-----------|----------|-------------|
| Agent Entry Point | `autonomous_agent_demo.py` | Main entry point, manages agent sessions |
| Agent Logic | `agent.py` | Session logic for initializer and coding agents |
| SDK Client | `client.py` | Claude SDK client configuration |
| Security | `security.py` | Bash command allowlist and validation |
| Progress Tracking | `progress.py` | Progress tracking utilities |
| Prompts | `prompts.py` | Prompt loading utilities |

### Tech Stack

| Layer | Technology | Notes |
|-------|------------|-------|
| Runtime | Python 3.x | Core agent logic |
| AI SDK | Claude Agent SDK | `pip install claude-code-sdk` |
| CLI | Claude Code CLI | `npm install -g @anthropic-ai/claude-code` |
| Version Control | Git | Progress persistence |

### File Structure

```
autonomous-coding/
├── autonomous_agent_demo.py  # Main entry point
├── agent.py                  # Agent session logic
├── client.py                 # Claude SDK client configuration
├── security.py               # Bash command allowlist and validation
├── progress.py               # Progress tracking utilities
├── prompts.py                # Prompt loading utilities
├── prompts/
│   ├── app_spec.txt          # Application specification
│   ├── initializer_prompt.md # First session prompt
│   └── coding_prompt.md      # Continuation session prompt
├── docs/
│   ├── constitution.md       # Project constitution
│   ├── spec.md               # Feature specification template
│   └── plan.md               # Implementation plan template
└── requirements.txt          # Python dependencies
```

---

## Constitution Compliance Check

<!-- 
Verify alignment with constitutional principles before implementation.
This section is evaluated BEFORE and AFTER the design phase.
-->

### Pre-Design Evaluation

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Agent Autonomy | 🔄 Pending | [How does this feature support session independence?] |
| II. Single Source of Truth | 🔄 Pending | [Does this feature respect feature_list.json as the source of truth?] |
| III. Test-Driven Verification | 🔄 Pending | [Can this feature be verified via browser automation?] |
| IV. Quality Over Speed | 🔄 Pending | [Does this feature maintain production quality standards?] |
| V. Incremental Progress | 🔄 Pending | [Can this feature be completed in one session?] |
| VI. Security First | 🔄 Pending | [Does this feature require new bash commands?] |
| VII. Two-Agent Pattern | 🔄 Pending | [Is this compatible with initializer/coding agent workflow?] |

### Post-Design Evaluation

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Agent Autonomy | ❓ | [Updated after design] |
| II. Single Source of Truth | ❓ | [Updated after design] |
| III. Test-Driven Verification | ❓ | [Updated after design] |
| IV. Quality Over Speed | ❓ | [Updated after design] |
| V. Incremental Progress | ❓ | [Updated after design] |
| VI. Security First | ❓ | [Updated after design] |
| VII. Two-Agent Pattern | ❓ | [Updated after design] |

---

## Phase 0: Research & Clarification

<!-- 
Resolve all "NEEDS CLARIFICATION" items before proceeding to design.
Use /speckit.clarify if needed.
-->

### Open Questions

| Question | Status | Resolution |
|----------|--------|------------|
| [Question from spec] | NEEDS CLARIFICATION | [Answer after research] |

### Research Tasks

- [ ] Review existing code patterns in `agent.py`
- [ ] Understand current security constraints in `security.py`
- [ ] Analyze prompt structure in `prompts/`
- [ ] Review progress tracking in `progress.py`

---

## Phase 1: Design Artifacts

### Data Model Changes

<!-- 
Define any new data structures or modifications to existing ones.
-->

#### New Entity: [EntityName]

```python
# Location: [file path]

@dataclass
class EntityName:
    """
    [Description of the entity]
    """
    id: str                    # Unique identifier
    field1: str                # [Description]
    field2: int                # [Description]
    created_at: datetime       # Creation timestamp
    updated_at: datetime       # Last update timestamp
```

#### Modified Entity: [ExistingEntity]

```diff
# Location: [file path]

@dataclass
class ExistingEntity:
    existing_field: str
+   new_field: str            # [Description of new field]
+   another_field: Optional[int] = None  # [Description]
```

### API Contracts

<!-- 
Define any new functions, methods, or interfaces.
-->

#### New Function: `function_name`

```python
# Location: [file path]

def function_name(
    param1: str,
    param2: int,
    optional_param: Optional[str] = None
) -> ReturnType:
    """
    [Description of what the function does]
    
    Args:
        param1: [Description]
        param2: [Description]
        optional_param: [Description]
    
    Returns:
        [Description of return value]
    
    Raises:
        ValueError: [When this error occurs]
    
    Example:
        >>> result = function_name("value", 42)
        >>> print(result)
    """
    pass
```

### Integration Points

<!-- 
Document how this feature integrates with existing components.
-->

| Component | Integration Type | Description |
|-----------|------------------|-------------|
| `agent.py` | [Import/Call/Extend] | [How this integrates] |
| `security.py` | [Import/Call/Extend] | [How this integrates] |
| `prompts.py` | [Import/Call/Extend] | [How this integrates] |

---

## Phase 2: Implementation Tasks

<!-- 
Break down implementation into specific, actionable tasks.
This section will be expanded by /speckit.tasks.
-->

### Task Breakdown

#### Setup Tasks

- [ ] **Task 1**: Create new module file
  - File: `[file_path]`
  - Dependencies: None
  - Estimated effort: [X minutes]

- [ ] **Task 2**: Add imports to existing modules
  - File: `[file_path]`
  - Dependencies: Task 1
  - Estimated effort: [X minutes]

#### Core Implementation

- [ ] **Task 3**: Implement core logic
  - File: `[file_path]`
  - Dependencies: Task 1, Task 2
  - Estimated effort: [X minutes]
  - TDD: Write tests first, then implement

- [ ] **Task 4**: Add integration with existing components
  - File: `[file_path]`
  - Dependencies: Task 3
  - Estimated effort: [X minutes]

#### Testing & Verification

- [ ] **Task 5**: Add feature to `feature_list.json`
  - File: `feature_list.json`
  - Dependencies: Task 4
  - Estimated effort: [X minutes]

- [ ] **Task 6**: Verify via browser automation
  - Dependencies: Task 5
  - Estimated effort: [X minutes]

#### Documentation

- [ ] **Task 7**: Update `README.md`
  - File: `README.md`
  - Dependencies: Task 6
  - Estimated effort: [X minutes]

- [ ] **Task 8**: Update `claude-progress.txt`
  - File: `claude-progress.txt`
  - Dependencies: Task 7
  - Estimated effort: [X minutes]

### Task Dependencies Graph

```
Task 1 ──┬──> Task 3 ──> Task 4 ──> Task 5 ──> Task 6 ──> Task 7 ──> Task 8
         │
Task 2 ──┘
```

### Parallel Execution Opportunities

| Task Group | Tasks | Can Run in Parallel? |
|------------|-------|---------------------|
| Setup | Task 1, Task 2 | ✅ Yes |
| Core | Task 3, Task 4 | ❌ No (sequential) |
| Documentation | Task 7, Task 8 | ✅ Yes |

---

## Phase 3: Verification Checkpoints

<!-- 
Define verification checkpoints to ensure quality at each stage.
-->

### Checkpoint 1: Setup Complete

- [ ] New files created
- [ ] Imports added
- [ ] No lint errors
- [ ] Git commit made

### Checkpoint 2: Core Implementation Complete

- [ ] Core logic implemented
- [ ] Integration working
- [ ] Unit tests passing
- [ ] No console errors

### Checkpoint 3: Feature Complete

- [ ] All acceptance criteria met
- [ ] Browser automation tests pass
- [ ] Screenshots captured
- [ ] `feature_list.json` updated
- [ ] `passes: true` for all related tests

### Checkpoint 4: Documentation Complete

- [ ] README updated
- [ ] Progress notes updated
- [ ] Final git commit made
- [ ] Codebase in clean state

---

## Rollback Plan

<!-- 
Define how to roll back if implementation fails.
-->

1. Revert to last known good commit: `git revert HEAD`
2. Do not update `feature_list.json` if feature is incomplete
3. Document issues in `claude-progress.txt`
4. Leave detailed notes for next session

---

## Security Considerations

<!-- 
Document any security implications of this feature.
-->

### New Bash Commands Required

| Command | Justification | Risk Level |
|---------|---------------|------------|
| [command] | [Why needed] | [Low/Medium/High] |

> **Note**: Any new bash commands MUST be added to `security.py` ALLOWED_COMMANDS and justified in the constitution amendment.

### Security Review Checklist

- [ ] No arbitrary command execution
- [ ] File operations restricted to project directory
- [ ] Input validation for all user inputs
- [ ] No secrets or credentials in code

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2025-12-07 | [Author] | Initial plan |

