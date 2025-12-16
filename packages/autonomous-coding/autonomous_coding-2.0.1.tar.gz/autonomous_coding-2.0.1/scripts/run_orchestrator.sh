#!/bin/bash
# =============================================================================
# Autonomous Coding Agent - Orchestrator Runner
# =============================================================================
# This script runs the full orchestrated workflow with all three agents:
# - Initializer Agent: Sets up project and creates feature list
# - Dev Agent: Implements features one by one
# - QA Agent: Validates features through 5 quality gates
#
# Usage:
#   ./scripts/run_orchestrator.sh                    # Run orchestrator
#   ./scripts/run_orchestrator.sh --project myapp    # Custom project name
#   ./scripts/run_orchestrator.sh --spec ecommerce   # Use e-commerce template
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default values
SPEC_TEMPLATE=""
PROJECT_NAME="orchestrated_project"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --spec)
            SPEC_TEMPLATE="$2"
            shift 2
            ;;
        --project)
            PROJECT_NAME="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --spec TEMPLATE     Use a template (task_manager, ecommerce)"
            echo "  --project NAME      Set project name (default: orchestrated_project)"
            echo "  --help              Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                          # Run with default spec"
            echo "  $0 --spec task_manager      # Build task manager app"
            echo "  $0 --project myapp          # Custom project name"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       Autonomous Coding Agent - Orchestrator Runner            ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${RED}ERROR: ANTHROPIC_API_KEY is not set${NC}"
    echo ""
    echo "Please set your API key first:"
    echo "  export ANTHROPIC_API_KEY='your-api-key-here'"
    exit 1
fi

echo -e "${GREEN}✓ API key is set${NC}"

# Activate virtual environment
cd "$PROJECT_ROOT"
if [ -d ".venv" ]; then
    echo -e "${BLUE}ℹ Activating virtual environment...${NC}"
    source .venv/bin/activate
else
    echo -e "${YELLOW}⚠ No virtual environment found. Running setup first...${NC}"
    ./scripts/setup.sh
    source .venv/bin/activate
fi

# Apply template if specified
if [ -n "$SPEC_TEMPLATE" ]; then
    TEMPLATE_PATH="$PROJECT_ROOT/templates/${SPEC_TEMPLATE}_spec.txt"
    if [ -f "$TEMPLATE_PATH" ]; then
        echo -e "${BLUE}ℹ Using template: ${SPEC_TEMPLATE}${NC}"
        cp "$TEMPLATE_PATH" "$PROJECT_ROOT/prompts/app_spec.txt"
        echo -e "${GREEN}✓ Template copied to prompts/app_spec.txt${NC}"
    else
        echo -e "${RED}ERROR: Template not found: $TEMPLATE_PATH${NC}"
        exit 1
    fi
fi

# Set up project directory
PROJECT_DIR="$PROJECT_ROOT/generations/$PROJECT_NAME"
mkdir -p "$PROJECT_DIR"
echo -e "${GREEN}✓ Project directory: $PROJECT_DIR${NC}"

# Display workflow diagram
echo ""
echo -e "${BLUE}Orchestrated Workflow:${NC}"
echo ""
echo "  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐"
echo "  │ INITIALIZER │ ──► │  DEV AGENT  │ ──► │  QA AGENT   │"
echo "  │   AGENT     │     │             │     │             │"
echo "  │             │     │ Implements  │     │ 5 Quality   │"
echo "  │ Creates     │     │ features    │     │ Gates       │"
echo "  │ features    │     │ one by one  │     │             │"
echo "  └─────────────┘     └─────────────┘     └──────┬──────┘"
echo "                            ▲                     │"
echo "                            │    (if failed)      │"
echo "                            └─────────────────────┘"
echo ""

# Warning about long runtime
echo -e "${YELLOW}⚠ WARNING: This will run until ALL features pass QA.${NC}"
echo "  - This can take many hours (potentially 10+ hours for 200 features)"
echo "  - Each feature goes through: DEV → QA → (retry if failed)"
echo "  - Progress is saved automatically; you can resume with Ctrl+C"
echo ""

read -p "Continue? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

# Run the orchestrator
echo ""
echo -e "${BLUE}Starting orchestrator...${NC}"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

python orchestrator.py --project-dir "$PROJECT_DIR"

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo -e "${GREEN}Orchestrator session complete${NC}"
echo ""
echo "Project files are in: $PROJECT_DIR"
echo ""
echo "Review artifacts:"
echo "  - Workflow state: cat $PROJECT_DIR/workflow-state.json"
echo "  - QA reports: ls $PROJECT_DIR/qa-reports/"
echo "  - Progress: cat $PROJECT_DIR/claude-progress.txt"
echo ""

