# QA Agent Quickstart Guide

This guide will help you set up and run the QA Agent for independent quality validation.

## Prerequisites

- Python 3.10+
- Node.js 18+ (for JavaScript/TypeScript projects)
- Git

## Installation

### 1. Install Python Dependencies

```bash
# Create virtual environment
uv venv .venv
source .venv/bin/activate

# Install dependencies
uv pip install playwright pytest ruff mypy

# Install Playwright browsers
python -m playwright install chromium
```

### 2. Install JavaScript/TypeScript Dependencies (optional)

```bash
# Install pnpm if not present
npm install -g pnpm

# Install tools
pnpm add -D @biomejs/biome typescript vitest
```

### 3. Install Git Hook

```bash
# Copy pre-commit hook for RBAC enforcement
cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## Configuration

### Environment Variables

Set the `AGENT_TYPE` environment variable to identify the running agent:

```bash
# For QA Agent
export AGENT_TYPE=QA

# For Dev Agent
export AGENT_TYPE=DEV
```

### API Key Rotation (optional)

Configure multiple API keys for quota rotation:

```bash
export ANTHROPIC_API_KEY_1="sk-ant-your-first-key"
export ANTHROPIC_API_KEY_2="sk-ant-your-second-key"
export ANTHROPIC_API_KEY_3="sk-ant-your-third-key"
```

### Feature List

Create a `feature_list.json` file in your project root:

```json
[
  {
    "id": 1,
    "description": "Feature description",
    "test_steps": [
      "Navigate to /page",
      "Click on button",
      "Verify result"
    ],
    "passes": false,
    "qa_validated": false,
    "timeout_minutes": 10
  }
]
```

## Running the QA Agent

### Validate a Single Feature

```python
from qa_agent import QAAgent
from pathlib import Path

agent = QAAgent(Path("."))
report = agent.run_quality_gates(feature_id=1, feature_description="My Feature")
agent.save_report(report)
```

### Run Regression Suite

```python
from qa_agent import QAAgent
from pathlib import Path

agent = QAAgent(Path("."))
report = agent.run_regression_suite()
```

### Generate Summary Report

```python
from qa_agent import QAAgent
from pathlib import Path

agent = QAAgent(Path("."))
report = agent.generate_summary_report()
```

## Quality Gates

The QA Agent runs 5 quality gates:

1. **Lint** - Code style and quality (Biome for JS/TS, Ruff for Python)
2. **Type Check** - Type safety (TypeScript, Mypy)
3. **Unit Tests** - Test suite (Vitest, Pytest)
4. **Browser Automation** - E2E tests (Playwright)
5. **Story Validation** - User acceptance criteria

## Understanding Reports

### QA Report Structure

Reports are saved to `qa-reports/feature-{id}-{timestamp}.json`:

```json
{
  "feature_id": 1,
  "overall_status": "PASSED|FAILED",
  "gates": {
    "lint": { "passed": true, "errors": [] },
    "type_check": { "passed": true, "errors": [] },
    "unit_tests": { "passed": true, "errors": [] },
    "browser_automation": { "passed": true, "errors": [] },
    "story_validation": { "passed": true, "errors": [] }
  },
  "priority_fixes": [],
  "summary": {
    "gates_passed": 5,
    "gates_failed": 0,
    "total_errors": 0
  }
}
```

### Priority Fixes

When gates fail, `priority_fixes` contains actionable items:

- Priority 1: Lint errors (fix first)
- Priority 2: Type errors
- Priority 3: Test failures
- Priority 4: Browser test failures
- Priority 5: Story validation failures

## RBAC Enforcement

The pre-commit hook enforces role-based access control:

- **QA Agent** (`AGENT_TYPE=QA`): Can modify `passes`, `qa_validated`, `last_qa_run`, `qa_notes`, `qa_report_path` fields
- **Dev Agent** (`AGENT_TYPE=DEV`): Cannot modify these protected fields

### Emergency Bypass

```bash
# Use with caution - bypasses RBAC checks
git commit --no-verify -m "Emergency fix"
```

## Orchestrator

Start the orchestrator for automated workflow management:

```bash
python orchestrator.py --project-dir /path/to/project
```

### Workflow States

```
START → INITIALIZER → DEV_READY → DEV → QA_READY → QA → QA_PASSED/DEV_FEEDBACK → COMPLETE
```

## Troubleshooting

### Common Issues

1. **"No API credentials found"**
   - Set `ANTHROPIC_API_KEY` or numbered keys

2. **"RBAC VIOLATION"**
   - Set correct `AGENT_TYPE` environment variable
   - Only QA Agent can modify protected fields

3. **"Playwright browser not found"**
   - Run `python -m playwright install chromium`

4. **"feature_list.json not found"**
   - Create the file in your project root

### Logs

- QA Agent logs: Console output
- Orchestrator logs: `orchestrator.log`
- RBAC audit log: `.git/hooks/pre-commit.log`

## Next Steps

- Review the [API Rotation Guide](./api-rotation-guide.md)
- Check example files in `docs/examples/`
- Read the full [spec.md](./spec.md) for architecture details
