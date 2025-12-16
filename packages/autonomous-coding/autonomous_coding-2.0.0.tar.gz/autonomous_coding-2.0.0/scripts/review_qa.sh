#!/bin/bash
# =============================================================================
# Autonomous Coding Agent - QA Report Review Tool
# =============================================================================
# This script helps review QA reports and feature progress from a project.
#
# Usage:
#   ./scripts/review_qa.sh PROJECT_DIR           # Review QA reports
#   ./scripts/review_qa.sh PROJECT_DIR --summary # Summary only
#   ./scripts/review_qa.sh PROJECT_DIR --failing # Show failing features
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Check arguments
if [ -z "$1" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: $0 PROJECT_DIR [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --summary    Show summary only"
    echo "  --failing    Show only failing features"
    echo "  --passing    Show only passing features"
    echo "  --latest     Show latest QA report details"
    echo ""
    echo "Examples:"
    echo "  $0 ./generations/my_project"
    echo "  $0 ./generations/my_project --summary"
    echo "  $0 ./generations/my_project --failing"
    exit 0
fi

PROJECT_DIR="$1"
shift

# Check if project exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}ERROR: Project directory not found: $PROJECT_DIR${NC}"
    exit 1
fi

# Parse options
SHOW_SUMMARY=false
SHOW_FAILING=false
SHOW_PASSING=false
SHOW_LATEST=false

for arg in "$@"; do
    case $arg in
        --summary) SHOW_SUMMARY=true ;;
        --failing) SHOW_FAILING=true ;;
        --passing) SHOW_PASSING=true ;;
        --latest) SHOW_LATEST=true ;;
    esac
done

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              QA Report Review Tool                             ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Project: $PROJECT_DIR${NC}"
echo ""

# Check for feature_list.json
FEATURE_LIST="$PROJECT_DIR/feature_list.json"
if [ ! -f "$FEATURE_LIST" ]; then
    echo -e "${YELLOW}⚠ No feature_list.json found${NC}"
    echo "  The project may not have been initialized yet."
    exit 1
fi

# Count features
TOTAL_FEATURES=$(cat "$FEATURE_LIST" | grep -c '"passes":' || echo 0)
PASSING_FEATURES=$(cat "$FEATURE_LIST" | grep -c '"passes": true' || echo 0)
FAILING_FEATURES=$((TOTAL_FEATURES - PASSING_FEATURES))

# Calculate progress
if [ "$TOTAL_FEATURES" -gt 0 ]; then
    PROGRESS=$((PASSING_FEATURES * 100 / TOTAL_FEATURES))
else
    PROGRESS=0
fi

# Display summary
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Feature Progress${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  Total Features:   ${CYAN}$TOTAL_FEATURES${NC}"
echo -e "  Passing:          ${GREEN}$PASSING_FEATURES${NC}"
echo -e "  Failing:          ${RED}$FAILING_FEATURES${NC}"
echo ""

# Progress bar
BAR_WIDTH=50
FILLED=$((PROGRESS * BAR_WIDTH / 100))
EMPTY=$((BAR_WIDTH - FILLED))
BAR=$(printf '█%.0s' $(seq 1 $FILLED 2>/dev/null))$(printf '░%.0s' $(seq 1 $EMPTY 2>/dev/null))
echo -e "  Progress: [${GREEN}$BAR${NC}] ${PROGRESS}%"
echo ""

# Exit if summary only
if [ "$SHOW_SUMMARY" = true ]; then
    exit 0
fi

# Show failing features
if [ "$SHOW_FAILING" = true ]; then
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}Failing Features${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # Use Python to parse JSON properly
    python3 << EOF
import json
with open("$FEATURE_LIST") as f:
    features = json.load(f)

failing = [f for f in features if not f.get('passes', False)]
if not failing:
    print("  No failing features! 🎉")
else:
    for f in failing[:20]:  # Show first 20
        fid = f.get('id', '?')
        desc = f.get('description', 'No description')[:60]
        print(f"  #{fid}: {desc}")
    
    if len(failing) > 20:
        print(f"\n  ... and {len(failing) - 20} more")
EOF
    echo ""
fi

# Show passing features
if [ "$SHOW_PASSING" = true ]; then
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}Passing Features${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    python3 << EOF
import json
with open("$FEATURE_LIST") as f:
    features = json.load(f)

passing = [f for f in features if f.get('passes', False)]
if not passing:
    print("  No passing features yet.")
else:
    for f in passing[:20]:  # Show first 20
        fid = f.get('id', '?')
        desc = f.get('description', 'No description')[:60]
        print(f"  #{fid}: {desc}")
    
    if len(passing) > 20:
        print(f"\n  ... and {len(passing) - 20} more")
EOF
    echo ""
fi

# Check for QA reports
QA_REPORTS_DIR="$PROJECT_DIR/qa-reports"
if [ -d "$QA_REPORTS_DIR" ]; then
    REPORT_COUNT=$(ls -1 "$QA_REPORTS_DIR"/*.json 2>/dev/null | wc -l | tr -d ' ')
    
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}QA Reports${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "  Reports available: ${CYAN}$REPORT_COUNT${NC}"
    
    if [ "$REPORT_COUNT" -gt 0 ]; then
        LATEST_REPORT=$(ls -1t "$QA_REPORTS_DIR"/*.json 2>/dev/null | head -1)
        echo -e "  Latest report: ${CYAN}$(basename "$LATEST_REPORT")${NC}"
        
        if [ "$SHOW_LATEST" = true ] && [ -f "$LATEST_REPORT" ]; then
            echo ""
            echo -e "${BLUE}Latest Report Details:${NC}"
            python3 << EOF
import json
with open("$LATEST_REPORT") as f:
    report = json.load(f)

print(f"  Feature ID: {report.get('feature_id', 'N/A')}")
print(f"  Status: {report.get('overall_status', 'N/A')}")
print(f"  Timestamp: {report.get('timestamp', 'N/A')}")

gates = report.get('gates', {})
print("\n  Gate Results:")
for gate, result in gates.items():
    status = "✓" if result.get('passed') else "✗"
    duration = result.get('duration_seconds', 0)
    print(f"    {status} {gate}: {duration:.2f}s")

fixes = report.get('priority_fixes', [])
if fixes:
    print("\n  Priority Fixes:")
    for fix in fixes[:5]:
        print(f"    - {fix.get('message', 'No message')[:70]}")
EOF
        fi
    fi
    echo ""
fi

# Check workflow state
WORKFLOW_STATE="$PROJECT_DIR/workflow-state.json"
if [ -f "$WORKFLOW_STATE" ]; then
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}Workflow State${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    python3 << EOF
import json
with open("$WORKFLOW_STATE") as f:
    state = json.load(f)

print(f"  Current State: {state.get('current_state', 'N/A')}")
print(f"  Next Agent: {state.get('next_agent', 'N/A')}")
print(f"  Last Updated: {state.get('timestamp', 'N/A')}")

history = state.get('transition_history', [])
if history:
    print(f"\n  Recent Transitions (last 5):")
    for t in history[-5:]:
        print(f"    {t.get('from_state')} → {t.get('to_state')}")
EOF
    echo ""
fi

# Check progress notes
PROGRESS_FILE="$PROJECT_DIR/claude-progress.txt"
if [ -f "$PROGRESS_FILE" ]; then
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}Progress Notes (last 20 lines)${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    tail -20 "$PROGRESS_FILE" | sed 's/^/  /'
    echo ""
fi

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Available commands:"
echo "  $0 $PROJECT_DIR --summary    # Summary only"
echo "  $0 $PROJECT_DIR --failing    # List failing features"
echo "  $0 $PROJECT_DIR --passing    # List passing features"
echo "  $0 $PROJECT_DIR --latest     # Show latest QA report details"
echo ""

