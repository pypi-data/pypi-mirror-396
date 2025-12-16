"""
Claude SDK Client Configuration
===============================

Functions for creating and configuring the Claude Agent SDK client.
Supports API rotation via numbered environment variables.
"""

import json
import os
from pathlib import Path

from claude_code_sdk import ClaudeCodeOptions, ClaudeSDKClient
from claude_code_sdk.types import HookMatcher

from core.security import bash_security_hook
from utils.api_rotation import load_api_credentials
from utils.logger import log_info, log_success

# Puppeteer MCP tools for browser automation
PUPPETEER_TOOLS = [
    "mcp__puppeteer__puppeteer_navigate",
    "mcp__puppeteer__puppeteer_screenshot",
    "mcp__puppeteer__puppeteer_click",
    "mcp__puppeteer__puppeteer_fill",
    "mcp__puppeteer__puppeteer_select",
    "mcp__puppeteer__puppeteer_hover",
    "mcp__puppeteer__puppeteer_evaluate",
]

# Built-in tools
BUILTIN_TOOLS = [
    "Read",
    "Write",
    "Edit",
    "Glob",
    "Grep",
    "Bash",
]


def create_client(project_dir: Path, model: str) -> ClaudeSDKClient:
    """
    Create a Claude Agent SDK client with multi-layered security.

    Args:
        project_dir: Directory for the project
        model: Claude model to use

    Returns:
        Configured ClaudeSDKClient

    Security layers (defense in depth):
    1. Sandbox - OS-level bash command isolation prevents filesystem escape
    2. Permissions - File operations restricted to project_dir only
    3. Security hooks - Bash commands validated against an allowlist
       (see security.py for ALLOWED_COMMANDS)

    API Rotation Support:
    - Supports ANTHROPIC_BASE_URL environment variable for custom API endpoints
    - Supports numbered env vars (ANTHROPIC_API_KEY_1, ANTHROPIC_BASE_URL_1, etc.)
    - Falls back to single ANTHROPIC_API_KEY if numbered pairs not found
    """
    project_dir = Path(project_dir)

    # Load API credentials (supports numbered env vars for rotation)
    pairs = load_api_credentials()
    if not pairs:
        raise ValueError(
            "No API credentials found. Set ANTHROPIC_API_KEY or numbered pairs:\n"
            "  ANTHROPIC_API_KEY_1, ANTHROPIC_API_KEY_2, ...\n"
            "  ANTHROPIC_BASE_URL_1, ANTHROPIC_BASE_URL_2, ... (optional)\n"
            "  ANTHROPIC_MODEL_1, ANTHROPIC_MODEL_2, ... (optional, for 3rd party APIs)\n"
            "Get your API key from: https://console.anthropic.com/"
        )

    # Check if credentials were already set by the rotation system
    # If ANTHROPIC_API_KEY is already set and matches one of our pairs, use it
    current_api_key = os.environ.get("ANTHROPIC_API_KEY")
    current_base_url = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com")

    if current_api_key and any(current_api_key == key for key, _, _ in pairs):
        # Use the currently set credentials (from rotation)
        api_key = current_api_key
        base_url = current_base_url
    else:
        # Use first pair for initial setup
        api_key, base_url, _ = pairs[0]
        # Set environment variables for Claude SDK
        os.environ["ANTHROPIC_API_KEY"] = api_key
        if base_url != "https://api.anthropic.com":
            os.environ["ANTHROPIC_BASE_URL"] = base_url
        elif "ANTHROPIC_BASE_URL" in os.environ:
            del os.environ["ANTHROPIC_BASE_URL"]

    log_info(f"Using API endpoint: {base_url}", "API")
    log_info(f"Using model: {model}", "API")
    if len(pairs) > 1:
        log_info(f"API rotation available with {len(pairs)} key/endpoint/model triplets", "API")

    # Create comprehensive security settings
    # Note: Using relative paths ("./**") restricts access to project directory
    # since cwd is set to project_dir
    security_settings = {
        "sandbox": {"enabled": True, "autoAllowBashIfSandboxed": True},
        "permissions": {
            "defaultMode": "acceptEdits",  # Auto-approve edits within allowed directories
            "allow": [
                # Allow all file operations within the project directory
                "Read(./**)",
                "Write(./**)",
                "Edit(./**)",
                "Glob(./**)",
                "Grep(./**)",
                # Bash permission granted here, but actual commands are validated
                # by the bash_security_hook (see security.py for allowed commands)
                "Bash(*)",
                # Allow Puppeteer MCP tools for browser automation
                *PUPPETEER_TOOLS,
            ],
        },
    }

    # Ensure project directory exists before creating settings file
    project_dir.mkdir(parents=True, exist_ok=True)

    # Write settings to a file in the project directory
    settings_file = project_dir / ".claude_settings.json"
    with open(settings_file, "w") as f:
        json.dump(security_settings, f, indent=2)

    log_success(f"Created security settings at {settings_file}", "Security")
    log_info("Sandbox enabled (OS-level bash isolation)", "Security")
    log_info(f"Filesystem restricted to: {project_dir.resolve()}", "Security")
    log_info("Bash commands restricted to allowlist", "Security")
    log_info("MCP servers: puppeteer (browser automation)", "Security")

    return ClaudeSDKClient(
        options=ClaudeCodeOptions(
            model=model,
            system_prompt="You are an expert full-stack developer building a production-quality web application.",
            allowed_tools=[
                *BUILTIN_TOOLS,
                *PUPPETEER_TOOLS,
            ],
            mcp_servers={"puppeteer": {"command": "npx", "args": ["puppeteer-mcp-server"]}},
            hooks={
                "PreToolUse": [
                    HookMatcher(matcher="Bash", hooks=[bash_security_hook]),
                ],
            },
            max_turns=1000,
            cwd=str(project_dir.resolve()),
            settings=str(settings_file.resolve()),  # Use absolute path
        )
    )
