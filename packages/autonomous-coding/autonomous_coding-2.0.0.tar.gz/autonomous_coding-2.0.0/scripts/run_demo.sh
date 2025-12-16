#!/bin/bash
# =============================================================================
# Autonomous Coding Agent - Demo Runner
# =============================================================================
# This script runs the autonomous coding agent with sensible defaults
# for demonstration or production use.
#
# Usage:
#   ./scripts/run_demo.sh                    # Quick demo (3 iterations)
#   ./scripts/run_demo.sh --full             # Full build (unlimited)
#   ./scripts/run_demo.sh --spec ecommerce   # Use e-commerce template
#   ./scripts/run_demo.sh --project myapp    # Custom project name
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
DEMO_MODE="quick"
SPEC_TEMPLATE=""
PROJECT_NAME="demo_project"
MAX_ITERATIONS=3

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --full)
            DEMO_MODE="full"
            MAX_ITERATIONS=0
            shift
            ;;
        --spec)
            SPEC_TEMPLATE="$2"
            shift 2
            ;;
        --project)
            PROJECT_NAME="$2"
            shift 2
            ;;
        --iterations)
            MAX_ITERATIONS="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --full              Run full build (unlimited iterations)"
            echo "  --spec TEMPLATE     Use a template (task_manager, ecommerce)"
            echo "  --project NAME      Set project name (default: demo_project)"
            echo "  --iterations N      Set max iterations (default: 3 for demo)"
            echo "  --help              Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                          # Quick 3-iteration demo"
            echo "  $0 --full                   # Full autonomous build"
            echo "  $0 --spec task_manager      # Build task manager app"
            echo "  $0 --project myapp --full   # Full build to 'myapp' directory"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         Autonomous Coding Agent - Demo Runner                  ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${RED}ERROR: ANTHROPIC_API_KEY is not set${NC}"
    echo ""
    echo "Please set your API key first:"
    echo "  export ANTHROPIC_API_KEY='your-api-key-here'"
    echo ""
    echo "Get your key from: https://console.anthropic.com/account/keys"
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
        echo "Available templates:"
        ls "$PROJECT_ROOT/templates/"*.txt 2>/dev/null | xargs -I {} basename {} _spec.txt
        exit 1
    fi
fi

# Set up project directory
PROJECT_DIR="$PROJECT_ROOT/generations/$PROJECT_NAME"
mkdir -p "$PROJECT_DIR"
echo -e "${GREEN}✓ Project directory: $PROJECT_DIR${NC}"

# Display configuration
echo ""
echo -e "${BLUE}Configuration:${NC}"
echo "  Mode: $DEMO_MODE"
if [ "$MAX_ITERATIONS" -eq 0 ]; then
    echo "  Iterations: unlimited"
else
    echo "  Iterations: $MAX_ITERATIONS"
fi
echo "  Project: $PROJECT_NAME"
echo "  Spec: $(basename "$(readlink -f "$PROJECT_ROOT/prompts/app_spec.txt" 2>/dev/null || echo "$PROJECT_ROOT/prompts/app_spec.txt")")"
echo ""

# Confirm before full build
if [ "$DEMO_MODE" = "full" ]; then
    echo -e "${YELLOW}⚠ FULL BUILD MODE${NC}"
    echo "This will run until all features are complete (potentially many hours)."
    echo ""
    read -p "Continue? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
fi

# Build command
CMD="python autonomous_agent_demo.py --project-dir $PROJECT_DIR"
if [ "$MAX_ITERATIONS" -gt 0 ]; then
    CMD="$CMD --max-iterations $MAX_ITERATIONS"
fi

echo ""
echo -e "${BLUE}Running command:${NC}"
echo "  $CMD"
echo ""
echo -e "${BLUE}Starting autonomous agent...${NC}"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Run the agent
$CMD

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo -e "${GREEN}Agent session complete${NC}"
echo ""
echo "Project files are in: $PROJECT_DIR"
echo ""
echo "Next steps:"
echo "  1. Check progress: cat $PROJECT_DIR/claude-progress.txt"
echo "  2. View features: cat $PROJECT_DIR/feature_list.json | head -50"
echo "  3. Continue build: $0 --project $PROJECT_NAME --full"
echo ""

