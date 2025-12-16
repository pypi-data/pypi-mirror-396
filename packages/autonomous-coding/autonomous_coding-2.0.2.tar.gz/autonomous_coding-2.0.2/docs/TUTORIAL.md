# Autonomous Coding Agent - Complete Tutorial

A comprehensive guide to using the Autonomous Coding Agent for building applications with AI.

## Table of Contents

1. [Quick Start](#quick-start)
2. [CLI Commands Reference](#cli-commands-reference)
3. [Session Management](#session-management)
4. [Pause and Resume](#pause-and-resume)
5. [API Configuration & Rotation](#api-configuration--rotation)
6. [Custom Specifications & Templates](#custom-specifications--templates)
7. [Remote Execution (VS Code SSH)](#remote-execution-vs-code-ssh)
   - [Headless Browser Testing](#headless-browser-testing-no-gui)
8. [Monitoring & Troubleshooting](#monitoring--troubleshooting)

---

## Quick Start

### Installation

```bash
# Option 1: Install from PyPI
pip install autonomous-coding

# Option 2: Install with all dependencies (recommended)
pip install "autonomous-coding[all]"

# Option 3: Development mode with uv
git clone https://github.com/anthropics/claude-quickstarts.git
cd claude-quickstarts/autonomous-coding
uv sync
```

### Your First Build

```bash
# Set your API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Build an e-commerce application
autonomous-coding --project-dir ./my-shop --spec ecommerce

# Or build a task manager
autonomous-coding --project-dir ./my-tasks --spec task_manager
```

### What Happens

1. **Session 1 (Initializer)**: Creates `feature_list.json` with 200 test cases
2. **Sessions 2+**: Implements features one by one, marking them as passing
3. **Auto-continue**: Sessions run continuously until complete or interrupted

---

## CLI Commands Reference

### Main Command: `autonomous-coding`

The primary CLI for running the autonomous coding agent.

```bash
autonomous-coding [OPTIONS]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--project-dir PATH` | Directory for the project | `./autonomous_demo_project` |
| `--max-iterations N` | Maximum number of sessions | Unlimited |
| `--model MODEL` | Claude model to use | `claude-sonnet-4-5-20250929` |
| `--spec TEMPLATE` | Template name (`ecommerce`, `task_manager`, or custom) | None |
| `--force-spec` | Force update `app_spec.txt` from template | False |
| `--version` | Show version and exit | - |

#### Examples

```bash
# Quick demo (3 sessions only)
autonomous-coding --project-dir ./my_project --max-iterations 3

# Build e-commerce app with unlimited sessions
autonomous-coding --project-dir ./my_shop --spec ecommerce

# Use a specific model
autonomous-coding --project-dir ./my_project --model claude-sonnet-4-20250514

# Force refresh the spec file from template
autonomous-coding --project-dir ./my_shop --spec ecommerce --force-spec
```

### Additional CLI Commands

| Command | Description | Example |
|---------|-------------|---------|
| `ac-demo` | Alias for `autonomous-coding` | `ac-demo --project-dir ./demo` |
| `ac-orchestrator` | Run multi-agent orchestrator workflow | `ac-orchestrator --project-dir ./project` |
| `ac-qa` | Run QA agent for feature validation | `ac-qa --project-dir ./project --feature-id 1` |
| `ac-spec-validator` | Validate app specification | `ac-spec-validator --project-dir ./project` |

```bash
# Run orchestrator (advanced multi-agent workflow)
uv run ac-orchestrator --project-dir ./my_project

# Run QA on specific feature
uv run ac-qa --project-dir ./my_project --feature-id 1

# Validate specification before building
uv run ac-spec-validator --project-dir ./my_project
```

---

## Session Management

### How Sessions Work

Each session is a **fresh context window** - the agent doesn't remember previous sessions. Instead, it relies on:

- `feature_list.json` - Master list of features with pass/fail status
- `claude-progress.txt` - Notes from previous sessions
- Git history - All code changes

### Session Flow

```
┌──────────────────────────────────────────────────────────────┐
│                    SESSION LIFECYCLE                          │
└──────────────────────────────────────────────────────────────┘

  Start Command
       │
       ▼
  ┌─────────────────┐
  │ Load State      │◄──── Reads feature_list.json
  │ (Fresh or       │      and claude-progress.txt
  │  Resume?)       │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │ Session N       │──── Implements 1 feature
  │ (5-30 min)      │     Updates feature_list.json
  └────────┬────────┘     Git commits changes
           │
           ▼
  ┌─────────────────┐
  │ Session Result  │
  │                 │
  │  Continue → Wait 3s → Next Session
  │  Ctrl+C   → PAUSE (state saved)
  │  Error    → Retry with fresh context
  │  Quota    → Rotate API key, retry
  └─────────────────┘
```

### Session Limits

| Setting | Value | Configurable? |
|---------|-------|---------------|
| Max tool calls per session | 1,000 | No (hardcoded) |
| Time limit per session | None | N/A |
| Delay between sessions | 3 seconds | No |
| Typical session duration | 5-30 minutes | Varies |

### First Session (Initializer)

The first session is special - it uses the **Initializer Agent**:

- Reads `app_spec.txt`
- Creates `feature_list.json` with 200 test cases
- Sets up project structure
- Takes 10-20+ minutes

```bash
# Progress indicator during first session
[INFO] Fresh start - will use initializer agent
[WARN] The agent is generating 200 detailed test cases.
[WARN] This may appear to hang - it's working. Watch for Tool logs.
```

---

## Pause and Resume

The agent is designed to be **fully interruptible**. All progress is saved automatically.

### How to Pause

#### Method 1: Keyboard Interrupt (Recommended)

```bash
# While the agent is running, press:
Ctrl+C
```

The agent will:
- Complete any in-progress file writes
- Save state to `feature_list.json`
- Exit cleanly

#### Method 2: Limited Iterations

```bash
# Run only 5 sessions, then automatically stop
autonomous-coding --project-dir ./my_project --max-iterations 5
```

#### Method 3: Terminal Close

Even if you force-close the terminal, progress is preserved because:
- `feature_list.json` is updated after each feature
- Git commits are made regularly
- `claude-progress.txt` tracks session notes

### How to Resume

Simply run the **same command** again:

```bash
# Resume from where you left off
autonomous-coding --project-dir ./my_project --spec ecommerce
```

**What happens on resume:**

1. Detects `feature_list.json` exists → **not a fresh start**
2. Loads existing feature list and progress
3. Reads `claude-progress.txt` for context
4. Continues with the next failing feature

### State Persistence Files

| File | Purpose |
|------|---------|
| `feature_list.json` | Master list of all features with pass/fail status |
| `claude-progress.txt` | Session notes and implementation history |
| `.git/` | Git history of all changes |
| `token-consumption-*.json` | Token usage tracking per session |

### Multi-Day Workflow Example

```bash
# Day 1: Start building (run 10 sessions, then Ctrl+C)
autonomous-coding --project-dir ./my_shop --spec ecommerce
# Progress: 15/203 features complete

# Day 2: Resume (picks up where it left off)
autonomous-coding --project-dir ./my_shop --spec ecommerce
# Progress: 45/203 features complete

# Day 3: Run overnight with logging
nohup autonomous-coding --project-dir ./my_shop --spec ecommerce > build.log 2>&1 &

# Check progress anytime
tail -f build.log
grep "Progress:" build.log | tail -1
```

---

## API Configuration & Rotation

### Basic Configuration

Create a `.env` file in your project or working directory:

```bash
# Single API key (simplest)
ANTHROPIC_API_KEY="sk-ant-api03-..."
```

### Multi-Key Rotation

For long-running builds, configure multiple API keys for automatic rotation:

```bash
# .env file with multiple API key/endpoint pairs

# 1. Official Anthropic API (no model override - uses CLI default)
ANTHROPIC_API_KEY_1="sk-ant-api03-..."
ANTHROPIC_BASE_URL_1="https://api.anthropic.com"

# 2. Third-party API with custom model
ANTHROPIC_API_KEY_2="your-key-here"
ANTHROPIC_BASE_URL_2="https://api.example.com/v1"
ANTHROPIC_MODEL_2="custom-model-name"

# 3. Another provider
ANTHROPIC_API_KEY_3="another-key"
ANTHROPIC_BASE_URL_3="https://api.another.com/v1"
ANTHROPIC_MODEL_3="their-model-name"
```

### How Rotation Works

1. **Start**: Uses first available API key
2. **Quota Hit**: Detects rate limit or quota exhaustion
3. **Mark Exhausted**: Records the key with a cooling period
4. **Rotate**: Switches to next available key
5. **Retry**: Continues with new key

### Quota Types & Cooling Periods

| Quota Type | Cooling Period | Detection |
|------------|----------------|-----------|
| Rate Limit (429) | 60 seconds | HTTP 429 status |
| Session Expiry | 4 hours | HTTP 401/403 with session keywords |
| Daily Quota | Until next day (UTC) | "daily limit" in error |
| Weekly Quota | Until next Monday (UTC) | "weekly limit" in error |

### Model Override Behavior

When using `--model claude-sonnet-4-20250514` on CLI:

| Pair | Has Override? | Effective Model |
|------|---------------|-----------------|
| Pair 1 | No | `claude-sonnet-4-20250514` (from CLI) |
| Pair 2 | `ANTHROPIC_MODEL_2="custom"` | `custom` |
| Pair 3 | `ANTHROPIC_MODEL_3="another"` | `another` |

---

## Custom Specifications & Templates

### Built-in Templates

| Template | Description | Command |
|----------|-------------|---------|
| `ecommerce` | E-commerce platform with cart, checkout, admin | `--spec ecommerce` |
| `task_manager` | Task management app like Todoist | `--spec task_manager` |

### Creating a Custom Template

#### Step 1: Create the spec file

Create `templates/my_app_spec.txt`:

```xml
<project_specification>
  <project_name>My Custom App</project_name>

  <overview>
    A brief description of what you're building (2-3 sentences).
  </overview>

  <technology_stack>
    <frontend>
      <framework>React 18 with Vite</framework>
      <styling>Tailwind CSS</styling>
      <state_management>Zustand</state_management>
    </frontend>
    <backend>
      <runtime>Node.js with Express</runtime>
      <database>SQLite</database>
      <authentication>JWT</authentication>
    </backend>
  </technology_stack>

  <core_features>
    <feature_group name="Authentication">
      - User registration with email/password
      - Login/logout functionality
      - Password reset flow
    </feature_group>
    
    <feature_group name="Dashboard">
      - Overview with key metrics
      - Recent activity feed
    </feature_group>
  </core_features>

  <database_schema>
    <table name="users">
      - id (PRIMARY KEY)
      - email (UNIQUE)
      - password_hash
      - created_at
    </table>
  </database_schema>

  <api_endpoints_summary>
    <auth>
      - POST /api/auth/register
      - POST /api/auth/login
      - POST /api/auth/logout
    </auth>
  </api_endpoints_summary>

  <success_criteria>
    - All features are implemented and functional
    - Application is responsive on mobile and desktop
  </success_criteria>
</project_specification>
```

#### Step 2: Use your template

```bash
# Template naming: my_app_spec.txt → --spec my_app
autonomous-coding --project-dir ./my-project --spec my_app
```

### Template File Naming

The `--spec` flag searches for files in this order:

1. `templates/{name}_spec.txt`
2. `templates/{name}`
3. `templates/{name}.txt`

### Alternative: Direct Placement

```bash
# Option A: Place in prompts directory
cp my_spec.txt prompts/app_spec.txt
autonomous-coding --project-dir ./project

# Option B: Place directly in project
cp my_spec.txt ./project/app_spec.txt
autonomous-coding --project-dir ./project
```

### Template Structure Reference

| Section | Purpose | Required? |
|---------|---------|-----------|
| `<project_name>` | App name and tagline | Yes |
| `<overview>` | Brief description | Yes |
| `<technology_stack>` | Frontend, backend, database | Yes |
| `<core_features>` | Detailed feature list | Yes |
| `<database_schema>` | Tables and fields | Recommended |
| `<api_endpoints_summary>` | REST endpoints | Recommended |
| `<ui_layout>` | Page layouts | Optional |
| `<design_system>` | Colors, fonts | Optional |
| `<success_criteria>` | Definition of done | Optional |

### Tips for Better Specs

1. **Be Detailed**: More detail = better implementation
2. **Include Edge Cases**: Error states, empty states, loading states
3. **Specify UI Behavior**: How things should look and feel
4. **Define Test Steps**: How to verify each feature works
5. **Prioritize Features**: Order by importance
6. **Realistic Scope**: 50 features for demos, 200 for comprehensive apps

---

## Remote Execution (VS Code SSH)

Running `autonomous-coding` via VS Code Remote SSH requires additional considerations.

### SSH Connection Persistence

If your SSH connection drops, the process will be killed unless you use:

#### Option A: tmux (Recommended)

```bash
# Start a tmux session
tmux new -s coding

# Run the command
autonomous-coding --project-dir ./demo --spec ecommerce

# Detach: Ctrl+B, then D
# Reattach later: tmux attach -t coding
```

#### Option B: nohup

```bash
nohup autonomous-coding --project-dir ./demo --spec ecommerce > output.log 2>&1 &

# Check progress
tail -f output.log
```

#### Option C: screen

```bash
screen -S coding
autonomous-coding --project-dir ./demo --spec ecommerce
# Detach: Ctrl+A, then D
# Reattach: screen -r coding
```

### Environment Variables

Environment variables in `~/.bashrc` may not load in non-interactive SSH sessions.

**Solutions:**

```bash
# Option 1: Use .env file (recommended)
# The CLI automatically loads from .env

# Option 2: Source bashrc before running
source ~/.bashrc && autonomous-coding --project-dir ./demo

# Option 3: Export directly
export ANTHROPIC_API_KEY="sk-ant-..."
autonomous-coding --project-dir ./demo
```

### Network Access

Ensure the remote server can reach API endpoints:

```bash
# Test connectivity
curl -I https://api.anthropic.com

# If behind proxy
export HTTPS_PROXY="http://proxy.company.com:8080"
```

### Path Considerations

```bash
# Use absolute paths to avoid confusion
autonomous-coding --project-dir /home/user/my-project --spec ecommerce

# Or cd first
cd /home/user/my-project
autonomous-coding --project-dir . --spec ecommerce
```

### Headless Browser Testing (No GUI)

On servers without a display (no GUI), browser testing runs in **headless mode** automatically.

#### How It Works

The QA agent uses Playwright with `headless=True`:

```python
# From gates.py - already configured for headless
browser = p.chromium.launch(headless=True)
```

#### Installing Playwright on Headless Server

```bash
# Install Playwright
pip install playwright

# Install browser binaries (headless-compatible)
playwright install chromium

# Or install with all dependencies (recommended for Linux servers)
playwright install --with-deps chromium
```

#### Linux Server Dependencies

On Ubuntu/Debian servers, you may need system dependencies:

```bash
# Install system dependencies for Playwright
sudo apt-get update
sudo apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2

# Or use the --with-deps flag (installs everything)
playwright install --with-deps chromium
```

#### Virtual Display (Optional)

For tools that don't support headless mode, use `xvfb`:

```bash
# Install virtual framebuffer
sudo apt-get install -y xvfb

# Run with virtual display
xvfb-run autonomous-coding --project-dir ./demo --spec ecommerce

# Or set display manually
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 &
autonomous-coding --project-dir ./demo --spec ecommerce
```

#### Puppeteer (MCP Server)

The agent also uses Puppeteer via MCP for browser automation during development:

```bash
# Puppeteer needs Chrome/Chromium
# Install on Ubuntu/Debian
sudo apt-get install -y chromium-browser

# Or let Puppeteer download it
npx puppeteer browsers install chrome
```

#### Troubleshooting Headless Browser

| Issue | Solution |
|-------|----------|
| "Browser not found" | Run `playwright install chromium` |
| Missing dependencies | Run `playwright install --with-deps chromium` |
| Permission denied | Check file permissions, run as appropriate user |
| Timeout errors | Increase timeout, check network connectivity |
| Screenshots blank | Ensure virtual display is running (if needed) |

#### Verify Browser Works

```bash
# Test Playwright installation
python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); b = p.chromium.launch(headless=True); b.close(); p.stop(); print('OK')"

# Test with a simple script
python << 'EOF'
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://example.com")
    print(f"Title: {page.title()}")
    browser.close()
EOF
```

### Resource Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| RAM | 4 GB | 8+ GB |
| Disk Space | 1 GB | 5+ GB |
| CPU | 2 cores | 4+ cores |

```bash
# Check resources
free -h          # Memory
df -h .          # Disk space
nproc            # CPU cores
```

### Remote Monitoring

```bash
# Check if process is running
ps aux | grep autonomous-coding

# Monitor resource usage
top -p $(pgrep -f autonomous-coding)

# From local machine via SSH
ssh user@server "tail -f /path/to/build.log"
```

### Complete Remote Setup Checklist

```bash
# On remote server via VS Code SSH:

# 1. Install package
pip install autonomous-coding

# 2. Create .env file
cat > .env << 'EOF'
ANTHROPIC_API_KEY_1="sk-ant-..."
ANTHROPIC_BASE_URL_1="https://api.anthropic.com"
EOF

# 3. Test API connectivity
curl -s -o /dev/null -w "%{http_code}" https://api.anthropic.com

# 4. Start tmux session
tmux new -s coding

# 5. Run the command
autonomous-coding --project-dir . --spec ecommerce

# 6. Detach (Ctrl+B, D) - process continues

# 7. Reattach anytime
tmux attach -t coding
```

---

## Monitoring & Troubleshooting

### Check Progress

```bash
# Count passing/failing tests
grep -c '"passes": true' feature_list.json
grep -c '"passes": false' feature_list.json

# View recent session notes
tail -100 claude-progress.txt

# Check git history
git log --oneline -20
```

### Common Issues

#### "Appears to hang on first run"

This is normal during initialization. The agent is generating 200 test cases.

```bash
# Watch for tool output to confirm activity
[Tool: Write] - agent is working
[Tool: Bash] - agent is working
```

#### "Command blocked by security hook"

The agent tried to run a disallowed command. Add it to `ALLOWED_COMMANDS` in `src/core/security.py` if needed.

#### "API key not set"

```bash
# Set via environment
export ANTHROPIC_API_KEY="sk-ant-..."

# Or via .env file
echo 'ANTHROPIC_API_KEY="sk-ant-..."' > .env
```

#### "All API keys exhausted"

All configured keys hit quota limits. Options:
- Add more API keys to `.env`
- Wait for cooling period to expire
- Check quota status in provider dashboard

#### "Empty response"

Often indicates quota issues. The agent will automatically rotate keys.

### Logs and Reports

| File | Location | Purpose |
|------|----------|---------|
| Session output | stdout/stderr | Real-time progress |
| Progress notes | `claude-progress.txt` | Session history |
| Token usage | `token-consumption-*.json` | API usage tracking |
| Feature status | `feature_list.json` | Pass/fail status |
| QA reports | `qa-reports/` | Quality gate results |

### Estimated Build Times

| Scope | Features | Sessions | Time |
|-------|----------|----------|------|
| Quick Demo | 20-50 | 10-20 | 1-3 hours |
| Medium App | 50-100 | 30-50 | 5-10 hours |
| Full App | 150-200 | 80-150 | 15-30 hours |

---

## Quick Reference

### Essential Commands

| Task | Command |
|------|---------|
| Install | `pip install autonomous-coding` |
| Start/Resume | `autonomous-coding --project-dir ./project --spec ecommerce` |
| Limited run | `autonomous-coding --project-dir ./project --max-iterations 10` |
| Background | `nohup autonomous-coding --project-dir ./project > log.txt 2>&1 &` |
| Check progress | `grep -c '"passes": true' feature_list.json` |
| Pause | `Ctrl+C` |
| Resume | Same command as start |

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `ANTHROPIC_API_KEY` | Primary API key |
| `ANTHROPIC_API_KEY_N` | Numbered keys for rotation |
| `ANTHROPIC_BASE_URL_N` | Custom endpoints |
| `ANTHROPIC_MODEL_N` | Model override per endpoint |

### File Structure

```
my-project/
├── app_spec.txt              # Application specification
├── feature_list.json         # Feature tracking (source of truth)
├── claude-progress.txt       # Session notes
├── init.sh                   # Setup script (generated)
├── .claude_settings.json     # Security settings
├── token-consumption-*.json  # Usage tracking
├── client/                   # Frontend code
├── server/                   # Backend code
└── reports/                  # Test reports
```

---

## Next Steps

1. **Start small**: Use `--max-iterations 3` for your first run
2. **Customize**: Create your own spec for a unique application
3. **Scale up**: Run overnight for complete builds
4. **Contribute**: Share your templates and improvements

For more information:
- [README.md](../README.md) - Project overview
- [PUBLISHING.md](../PUBLISHING.md) - Package publishing guide
- [constitution.md](constitution.md) - Agent behavior guidelines
