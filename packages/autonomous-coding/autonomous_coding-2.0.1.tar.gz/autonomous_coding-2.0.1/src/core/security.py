"""
Security Hooks for Autonomous Coding Agent
==========================================

Pre-tool-use hooks that validate bash commands for security.
Uses an allowlist approach - only explicitly permitted commands can run.
"""

import os
import re
import shlex
from typing import Any

# Allowed commands for development tasks
# Minimal set needed for the autonomous coding demo
ALLOWED_COMMANDS = {
    # File inspection
    "ls",
    "cat",
    "head",
    "tail",
    "wc",
    "grep",
    "find",  # For finding files
    # File operations (agent uses SDK tools for most file ops, but cp/mkdir needed occasionally)
    "cp",
    "mv",
    "rm",
    "mkdir",
    "touch",
    "chmod",  # For making scripts executable; validated separately
    # Directory navigation
    "pwd",
    "cd",  # Change directory (shell builtin, but needed for compound commands)
    # Node.js development
    "npm",
    "npx",
    "node",
    "pnpm",
    "yarn",
    "vite",  # Vite dev server
    "next",  # Next.js
    "tsc",  # TypeScript compiler
    # Python development
    "python",
    "python3",
    "pip",
    "uv",
    # HTTP/API testing
    "curl",
    "wget",
    "jq",  # JSON processing
    # Shell scripting
    "bash",
    "sh",
    "echo",
    "printf",
    "true",
    "false",
    "test",
    "[",  # test alias
    "xargs",
    "sort",
    "uniq",
    "tr",
    "sed",
    "awk",
    "cut",
    "which",  # Find command location
    "whereis",  # Find command location
    "type",  # Shell builtin to check command type
    "command",  # Shell builtin to run command
    "env",  # Environment variables
    "export",  # Set environment variables
    "source",  # Source shell scripts
    ".",  # Source alias
    "date",  # Date/time
    "timeout",  # Run command with timeout
    "tee",  # Write to file and stdout
    "diff",  # Compare files
    "dirname",  # Get directory name
    "basename",  # Get base name
    "realpath",  # Get real path
    "readlink",  # Read symbolic link
    "stat",  # File statistics
    "file",  # Determine file type
    "less",  # Pager
    "more",  # Pager
    "tar",  # Archive
    "gzip",  # Compression
    "gunzip",  # Decompression
    "unzip",  # Unzip
    "zip",  # Zip
    # Version control
    "git",
    # Process management
    "ps",
    "lsof",
    "sleep",
    "pkill",  # For killing dev servers; validated separately
    "kill",
    # Script execution
    "init.sh",  # Init scripts; validated separately
    "start-servers.sh",  # Custom server start scripts
    # QA Agent quality gate commands
    "biome",  # TS/JS linting and formatting
    "vitest",  # TS/JS unit testing
    "playwright",  # Browser automation
    "pytest",  # Python unit testing
    "mypy",  # Python type checking
    "ruff",  # Python linting and formatting
}

# Commands that need additional validation even when in the allowlist
COMMANDS_NEEDING_EXTRA_VALIDATION = {"pkill", "chmod", "init.sh", "start-servers.sh", "rm"}


def is_command_allowed(command: str) -> bool:
    """
    Check if a command is in the allowed list.

    Args:
        command: Command name to check

    Returns:
        True if command is allowed
    """
    return command in ALLOWED_COMMANDS


def split_command_segments(command_string: str) -> list[str]:
    """
    Split a compound command into individual command segments.

    Handles command chaining (&&, ||, ;) but not pipes (those are single commands).

    Args:
        command_string: The full shell command

    Returns:
        List of individual command segments
    """
    # Split on && and || while preserving the ability to handle each segment
    # This regex splits on && or || that aren't inside quotes
    segments = re.split(r"\s*(?:&&|\|\|)\s*", command_string)

    # Further split on semicolons
    result = []
    for segment in segments:
        sub_segments = re.split(r'(?<!["\'])\s*;\s*(?!["\'])', segment)
        for sub in sub_segments:
            sub = sub.strip()
            if sub:
                result.append(sub)

    return result


def extract_commands(command_string: str) -> list[str]:
    """
    Extract command names from a shell command string.

    Handles pipes, command chaining (&&, ||, ;), and subshells.
    Returns the base command names (without paths).

    Args:
        command_string: The full shell command

    Returns:
        List of command names found in the string
    """
    commands = []

    # shlex doesn't treat ; as a separator, so we need to pre-process
    # Split on semicolons that aren't inside quotes (simple heuristic)
    # This handles common cases like "echo hello; ls"
    segments = re.split(r'(?<!["\'])\s*;\s*(?!["\'])', command_string)

    for segment in segments:
        segment = segment.strip()
        if not segment:
            continue

        try:
            tokens = shlex.split(segment)
        except ValueError:
            # Malformed command (unclosed quotes, etc.)
            # Return empty to trigger block (fail-safe)
            return []

        if not tokens:
            continue

        # Track when we expect a command vs arguments
        expect_command = True

        for token in tokens:
            # Shell operators indicate a new command follows
            if token in ("|", "||", "&&", "&"):
                expect_command = True
                continue

            # Skip shell keywords that precede commands
            if token in (
                "if",
                "then",
                "else",
                "elif",
                "fi",
                "for",
                "while",
                "until",
                "do",
                "done",
                "case",
                "esac",
                "in",
                "!",
                "{",
                "}",
            ):
                continue

            # Skip flags/options
            if token.startswith("-"):
                continue

            # Skip variable assignments (VAR=value)
            if "=" in token and not token.startswith("="):
                continue

            if expect_command:
                # Extract the base command name (handle paths like /usr/bin/python)
                cmd = os.path.basename(token)
                commands.append(cmd)
                expect_command = False

    return commands


def validate_pkill_command(command_string: str) -> tuple[bool, str]:
    """
    Validate pkill commands - only allow killing dev-related processes.

    Uses shlex to parse the command, avoiding regex bypass vulnerabilities.

    Returns:
        Tuple of (is_allowed, reason_if_blocked)
    """
    # Allowed process names for pkill
    allowed_process_names = {
        "node",
        "npm",
        "npx",
        "vite",
        "next",
    }

    try:
        tokens = shlex.split(command_string)
    except ValueError:
        return False, "Could not parse pkill command"

    if not tokens:
        return False, "Empty pkill command"

    # Separate flags from arguments
    args = []
    for token in tokens[1:]:
        if not token.startswith("-"):
            args.append(token)

    if not args:
        return False, "pkill requires a process name"

    # The target is typically the last non-flag argument
    target = args[-1]

    # For -f flag (full command line match), extract the first word as process name
    # e.g., "pkill -f 'node server.js'" -> target is "node server.js", process is "node"
    if " " in target:
        target = target.split()[0]

    if target in allowed_process_names:
        return True, ""
    return False, f"pkill only allowed for dev processes: {allowed_process_names}"


def validate_chmod_command(command_string: str) -> tuple[bool, str]:
    """
    Validate chmod commands - only allow making files executable with +x.

    Returns:
        Tuple of (is_allowed, reason_if_blocked)
    """
    try:
        tokens = shlex.split(command_string)
    except ValueError:
        return False, "Could not parse chmod command"

    if not tokens or tokens[0] != "chmod":
        return False, "Not a chmod command"

    # Look for the mode argument
    # Valid modes: +x, u+x, a+x, etc. (anything ending with +x for execute permission)
    mode = None
    files = []

    for token in tokens[1:]:
        if token.startswith("-"):
            # Skip flags like -R (we don't allow recursive chmod anyway)
            return False, "chmod flags are not allowed"
        elif mode is None:
            mode = token
        else:
            files.append(token)

    if mode is None:
        return False, "chmod requires a mode"

    if not files:
        return False, "chmod requires at least one file"

    # Only allow +x variants (making files executable)
    # This matches: +x, u+x, g+x, o+x, a+x, ug+x, etc.
    if not re.match(r"^[ugoa]*\+x$", mode):
        return False, f"chmod only allowed with +x mode, got: {mode}"

    return True, ""


def validate_init_script(command_string: str) -> tuple[bool, str]:
    """
    Validate init.sh script execution - only allow ./init.sh.

    Returns:
        Tuple of (is_allowed, reason_if_blocked)
    """
    try:
        tokens = shlex.split(command_string)
    except ValueError:
        return False, "Could not parse init script command"

    if not tokens:
        return False, "Empty command"

    # The command should be exactly ./init.sh (possibly with arguments)
    script = tokens[0]

    # Allow ./init.sh or paths ending in /init.sh
    if script == "./init.sh" or script.endswith("/init.sh"):
        return True, ""

    return False, f"Only ./init.sh is allowed, got: {script}"


def validate_start_servers_script(command_string: str) -> tuple[bool, str]:
    """
    Validate start-servers.sh script execution.

    Returns:
        Tuple of (is_allowed, reason_if_blocked)
    """
    try:
        tokens = shlex.split(command_string)
    except ValueError:
        return False, "Could not parse script command"

    if not tokens:
        return False, "Empty command"

    script = tokens[0]

    # Allow ./start-servers.sh or paths ending in /start-servers.sh
    if script == "./start-servers.sh" or script.endswith("/start-servers.sh"):
        return True, ""

    return False, f"Only ./start-servers.sh is allowed, got: {script}"


def validate_rm_command(command_string: str) -> tuple[bool, str]:
    """
    Validate rm commands - prevent dangerous operations.

    Returns:
        Tuple of (is_allowed, reason_if_blocked)
    """
    try:
        tokens = shlex.split(command_string)
    except ValueError:
        return False, "Could not parse rm command"

    if not tokens or tokens[0] != "rm":
        return False, "Not an rm command"

    # Check for dangerous flags
    dangerous_flags = {"-rf", "-fr", "--recursive", "-r"}
    has_recursive = False
    files = []

    for token in tokens[1:]:
        if token in dangerous_flags or token == "-r" or token == "-f":
            if "-r" in token or token == "--recursive":
                has_recursive = True
        elif not token.startswith("-"):
            files.append(token)

    # Block recursive deletion of root-like paths
    if has_recursive:
        dangerous_paths = {"/", "/*", ".", "..", "~", "~/", "$HOME"}
        for f in files:
            if f in dangerous_paths or f.startswith("/") and f.count("/") <= 2:
                return False, f"Dangerous recursive rm target: {f}"

    return True, ""


def get_command_for_validation(cmd: str, segments: list[str]) -> str:
    """
    Find the specific command segment that contains the given command.

    Args:
        cmd: The command name to find
        segments: List of command segments

    Returns:
        The segment containing the command, or empty string if not found
    """
    for segment in segments:
        segment_commands = extract_commands(segment)
        if cmd in segment_commands:
            return segment
    return ""


class SecurityHook:
    """Security hook class for validating bash commands."""

    def __init__(self, allowed_commands: set | None = None):
        """
        Initialize security hook.

        Args:
            allowed_commands: Set of allowed commands. Defaults to ALLOWED_COMMANDS.
        """
        self.allowed_commands = allowed_commands or ALLOWED_COMMANDS

    async def validate(
        self,
        input_data: dict[str, Any],
        tool_use_id: str | None = None,
        context: Any | None = None,
    ) -> dict[str, Any]:
        """
        Validate a bash command.

        Args:
            input_data: Dict containing tool_name and tool_input
            tool_use_id: Optional tool use ID
            context: Optional context

        Returns:
            Empty dict to allow, or {"decision": "block", "reason": "..."} to block
        """
        return await bash_security_hook(input_data, tool_use_id, context)


async def bash_security_hook(
    input_data: dict[str, Any],
    tool_use_id: str | None = None,  # noqa: ARG001
    context: Any | None = None,  # noqa: ARG001
) -> dict[str, Any]:
    """
    Pre-tool-use hook that validates bash commands using an allowlist.

    Only commands in ALLOWED_COMMANDS are permitted.

    Args:
        input_data: Dict containing tool_name and tool_input
        tool_use_id: Optional tool use ID
        context: Optional context

    Returns:
        Empty dict to allow, or {"decision": "block", "reason": "..."} to block
    """
    if input_data.get("tool_name") != "Bash":
        return {}

    command = input_data.get("tool_input", {}).get("command", "")
    if not command:
        return {}

    # Skip pure comment lines (shell comments starting with #)
    # Comments are valid shell syntax and should be allowed
    stripped = command.strip()
    if stripped.startswith("#"):
        # Check if it's a pure comment or a shebang (both are safe)
        # Multi-line commands may have comments, so only skip if the
        # entire first "command" before any operator is a comment
        first_line = stripped.split("\n")[0].strip()
        if first_line.startswith("#"):
            # It's a comment line - need to check if there are actual commands after
            # Remove comment lines and re-evaluate
            lines = command.split("\n")
            non_comment_lines = [
                line for line in lines if line.strip() and not line.strip().startswith("#")
            ]
            if not non_comment_lines:
                # Pure comments only - allow
                return {}
            # Reconstruct command without comment lines for validation
            command = "\n".join(non_comment_lines)

    # Extract all commands from the command string
    commands = extract_commands(command)

    if not commands:
        # Could not parse - fail safe by blocking
        return {
            "decision": "block",
            "reason": f"Could not parse command for security validation: {command}",
        }

    # Split into segments for per-command validation
    segments = split_command_segments(command)

    # Check each command against the allowlist
    for cmd in commands:
        if cmd not in ALLOWED_COMMANDS:
            return {
                "decision": "block",
                "reason": f"Command '{cmd}' is not in the allowed commands list",
            }

        # Additional validation for sensitive commands
        if cmd in COMMANDS_NEEDING_EXTRA_VALIDATION:
            # Find the specific segment containing this command
            cmd_segment = get_command_for_validation(cmd, segments)
            if not cmd_segment:
                cmd_segment = command  # Fallback to full command

            if cmd == "pkill":
                allowed, reason = validate_pkill_command(cmd_segment)
                if not allowed:
                    return {"decision": "block", "reason": reason}
            elif cmd == "chmod":
                allowed, reason = validate_chmod_command(cmd_segment)
                if not allowed:
                    return {"decision": "block", "reason": reason}
            elif cmd == "init.sh":
                allowed, reason = validate_init_script(cmd_segment)
                if not allowed:
                    return {"decision": "block", "reason": reason}
            elif cmd == "start-servers.sh":
                allowed, reason = validate_start_servers_script(cmd_segment)
                if not allowed:
                    return {"decision": "block", "reason": reason}
            elif cmd == "rm":
                allowed, reason = validate_rm_command(cmd_segment)
                if not allowed:
                    return {"decision": "block", "reason": reason}

    return {}
