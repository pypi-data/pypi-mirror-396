#!/bin/bash
# =============================================================================
# Autonomous Coding Agent - Environment Setup Script
# =============================================================================
# This script sets up the complete development environment for running
# the autonomous coding agent system using uv as the package manager.
#
# Usage:
#   ./scripts/setup.sh           # Full setup
#   ./scripts/setup.sh --check   # Check environment only
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_header() {
    echo -e "\n${BLUE}===================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# =============================================================================
# Environment Checks
# =============================================================================

check_python() {
    print_info "Checking Python installation..."
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f1)
        PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f2)
        
        if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 10 ]; then
            print_success "Python $PYTHON_VERSION found"
            return 0
        else
            print_error "Python 3.10+ required, found $PYTHON_VERSION"
            return 1
        fi
    else
        print_error "Python 3 not found"
        return 1
    fi
}

check_uv() {
    print_info "Checking uv installation..."
    if command_exists uv; then
        UV_VERSION=$(uv --version 2>&1 | head -1)
        print_success "uv found: $UV_VERSION"
        return 0
    else
        print_warning "uv not found, installing..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        # Add to PATH for current session
        export PATH="$HOME/.cargo/bin:$PATH"
        if command_exists uv; then
            print_success "uv installed successfully"
            return 0
        else
            print_error "Failed to install uv"
            return 1
        fi
    fi
}

check_node() {
    print_info "Checking Node.js installation..."
    if command_exists node; then
        NODE_VERSION=$(node --version | cut -d'v' -f2)
        NODE_MAJOR=$(echo "$NODE_VERSION" | cut -d'.' -f1)
        
        if [ "$NODE_MAJOR" -ge 18 ]; then
            print_success "Node.js v$NODE_VERSION found"
            return 0
        else
            print_warning "Node.js 18+ recommended, found v$NODE_VERSION"
            return 0
        fi
    else
        print_error "Node.js not found"
        return 1
    fi
}

check_pnpm() {
    print_info "Checking pnpm installation..."
    if command_exists pnpm; then
        PNPM_VERSION=$(pnpm --version)
        print_success "pnpm $PNPM_VERSION found"
        return 0
    else
        print_warning "pnpm not found, will install..."
        npm install -g pnpm
        return 0
    fi
}

check_claude_cli() {
    print_info "Checking Claude Code CLI..."
    if command_exists claude; then
        CLAUDE_VERSION=$(claude --version 2>&1 || echo "unknown")
        print_success "Claude CLI found: $CLAUDE_VERSION"
        return 0
    else
        print_warning "Claude CLI not found, installing..."
        npm install -g @anthropic-ai/claude-code
        return 0
    fi
}

check_api_key() {
    print_info "Checking Anthropic API key..."
    if [ -n "$ANTHROPIC_API_KEY" ]; then
        # Mask the key for display
        KEY_PREFIX="${ANTHROPIC_API_KEY:0:10}"
        print_success "ANTHROPIC_API_KEY is set (${KEY_PREFIX}...)"
        return 0
    else
        print_warning "ANTHROPIC_API_KEY not set"
        echo ""
        echo "  To set your API key, run:"
        echo "    export ANTHROPIC_API_KEY='your-api-key-here'"
        echo ""
        echo "  Or add it to your shell profile (~/.zshrc or ~/.bashrc)"
        return 1
    fi
}

# =============================================================================
# Setup Functions
# =============================================================================

setup_uv_project() {
    print_header "Setting up Python environment with uv"
    
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
    
    cd "$PROJECT_DIR"
    
    print_info "Syncing dependencies with uv..."
    uv sync
    
    print_info "Installing dev dependencies..."
    uv sync --all-extras
    
    print_success "Python environment ready"
}

setup_playwright() {
    print_header "Setting up Playwright"
    
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
    
    cd "$PROJECT_DIR"
    
    print_info "Installing Playwright browsers..."
    uv run python -m playwright install chromium
    
    print_success "Playwright ready"
}

setup_node_deps() {
    print_header "Setting up Node.js dependencies"
    
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
    
    cd "$PROJECT_DIR"
    
    if [ -f "package.json" ]; then
        print_info "Installing Node.js dependencies..."
        pnpm install
        print_success "Node.js dependencies installed"
    else
        print_info "No package.json found, skipping Node.js setup"
    fi
}

install_git_hooks() {
    print_header "Installing Git hooks"
    
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
    
    cd "$PROJECT_DIR"
    
    if [ -f "hooks/pre-commit" ]; then
        cp hooks/pre-commit .git/hooks/pre-commit
        chmod +x .git/hooks/pre-commit
        print_success "Pre-commit hook installed"
    else
        print_info "No pre-commit hook found in hooks/"
    fi
}

# =============================================================================
# Main Script
# =============================================================================

main() {
    print_header "Autonomous Coding Agent - Environment Setup (uv)"
    
    # Check mode
    CHECK_ONLY=false
    if [ "$1" = "--check" ]; then
        CHECK_ONLY=true
    fi
    
    # Run checks
    echo ""
    print_header "Checking Prerequisites"
    
    CHECKS_PASSED=true
    
    check_python || CHECKS_PASSED=false
    check_uv || CHECKS_PASSED=false
    check_node || CHECKS_PASSED=false
    check_pnpm || CHECKS_PASSED=false
    check_claude_cli || CHECKS_PASSED=false
    check_api_key || CHECKS_PASSED=false
    
    if [ "$CHECK_ONLY" = true ]; then
        if [ "$CHECKS_PASSED" = true ]; then
            print_header "All checks passed!"
            exit 0
        else
            print_header "Some checks failed"
            exit 1
        fi
    fi
    
    # Run setup
    setup_uv_project
    setup_playwright
    setup_node_deps
    install_git_hooks
    
    # Final summary
    print_header "Setup Complete!"
    
    echo "Next steps:"
    echo ""
    echo "  1. Set your API key (if not already done):"
    echo "     export ANTHROPIC_API_KEY='your-api-key'"
    echo ""
    echo "  2. Run commands with uv:"
    echo "     uv run python autonomous_agent_demo.py --project-dir ./test_project --max-iterations 2"
    echo ""
    echo "  3. Or run the orchestrator:"
    echo "     uv run python orchestrator.py --project-dir ./my_project"
    echo ""
    echo "  4. Run tests:"
    echo "     uv run pytest tests/ -v"
    echo ""
    
    print_success "Environment is ready!"
}

main "$@"
