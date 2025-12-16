"""
Agent Session Logic
===================

Core agent interaction functions for running autonomous coding sessions.
"""

import asyncio
import os
import time
from pathlib import Path

from claude_code_sdk import ClaudeSDKClient

from core.client import create_client
from core.progress import print_progress_summary, print_session_header
from core.prompts import (
    copy_spec_to_project,
    get_coding_prompt,
    get_initializer_prompt,
)
from utils.api_rotation import (
    APIRotationState,
    detect_quota_exhaustion,
)
from utils.logger import (
    log_api,
    log_error,
    log_info,
    log_section,
    log_success,
    log_tool,
    log_warn,
)
from utils.token_tracker import TokenTracker

# Configuration
AUTO_CONTINUE_DELAY_SECONDS = 3


async def run_agent_session(
    client: ClaudeSDKClient,
    message: str,
    project_dir: Path,  # noqa: ARG001
    token_tracker: TokenTracker | None = None,
) -> tuple[str, str, int, int]:
    """
    Run a single agent session using Claude Agent SDK.

    Args:
        client: Claude SDK client
        message: The prompt to send
        project_dir: Project directory path
        token_tracker: Optional token tracker for consumption reporting

    Returns:
        (status, response_text, input_tokens, output_tokens) where status is:
        - "continue" if agent should continue working
        - "error" if an error occurred
        - "quota_error" if quota exhausted (should trigger rotation)
    """
    log_api("Sending prompt to Claude Agent SDK...")

    start_time = time.time()
    input_tokens = 0
    output_tokens = 0

    try:
        # Send the query
        await client.query(message)

        # Collect response text and show tool use
        response_text = ""
        async for msg in client.receive_response():
            # Try to extract token usage from message
            if hasattr(msg, "usage"):
                usage = msg.usage
                if hasattr(usage, "input_tokens"):
                    input_tokens = max(input_tokens, usage.input_tokens or 0)
                if hasattr(usage, "output_tokens"):
                    output_tokens += usage.output_tokens or 0
            msg_type = type(msg).__name__

            # Handle AssistantMessage (text and tool use)
            if msg_type == "AssistantMessage" and hasattr(msg, "content"):
                for block in msg.content:
                    block_type = type(block).__name__

                    if block_type == "TextBlock" and hasattr(block, "text"):
                        response_text += block.text
                        print(block.text, end="", flush=True)
                    elif block_type == "ToolUseBlock" and hasattr(block, "name"):
                        log_tool(block.name, "executing")
                        if hasattr(block, "input"):
                            input_str = str(block.input)
                            if len(input_str) > 200:
                                print(f"   Input: {input_str[:200]}...", flush=True)
                            else:
                                print(f"   Input: {input_str}", flush=True)

            # Handle UserMessage (tool results)
            elif msg_type == "UserMessage" and hasattr(msg, "content"):
                for block in msg.content:
                    block_type = type(block).__name__

                    if block_type == "ToolResultBlock":
                        result_content = getattr(block, "content", "")
                        is_error = getattr(block, "is_error", False)

                        # Check if command was blocked by security hook
                        if "blocked" in str(result_content).lower():
                            log_error(f"BLOCKED: {result_content}", "Security")
                        elif is_error:
                            # Show errors (truncated)
                            error_str = str(result_content)[:500]
                            log_error(error_str, "Tool")
                        else:
                            # Tool succeeded - just show brief confirmation
                            log_success("Done", "Tool")

        print("\n" + "-" * 70 + "\n")

        # Calculate duration
        duration = time.time() - start_time

        # Record successful call in token tracker
        if token_tracker:
            token_tracker.record_call(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                duration_seconds=duration,
                success=True,
            )

        # Check if response indicates a quota/billing error
        # The SDK may print errors without raising exceptions
        is_quota_error, quota_type = detect_quota_exhaustion(None, response_text)
        if is_quota_error:
            log_warn(f"Detected quota error in response: {quota_type}", "API Rotation")
            return "quota_error", response_text, input_tokens, output_tokens

        # Also check for empty/very short responses which may indicate quota issues
        # The SDK sometimes prints errors directly without including them in the response
        if len(response_text.strip()) < 20:
            # If response is essentially empty, it's likely a billing/quota error
            log_warn(
                f"Very short response ({len(response_text)} chars) - possible quota issue", "API"
            )
            # Treat as quota error to trigger rotation
            return (
                "quota_error",
                "Empty response - possible API quota or billing issue",
                input_tokens,
                output_tokens,
            )

        return "continue", response_text, input_tokens, output_tokens

    except Exception as e:
        error_str = str(e)
        log_error(error_str, "Session")

        # Calculate duration
        duration = time.time() - start_time

        # Record failed call in token tracker
        if token_tracker:
            token_tracker.record_call(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                duration_seconds=duration,
                success=False,
                error=error_str[:200],
            )

        # Check if this is a quota/billing error that should trigger rotation
        is_quota_error, quota_type = detect_quota_exhaustion(None, error_str)

        if is_quota_error:
            log_warn(f"Detected quota error in exception: {quota_type}", "API Rotation")
            return "quota_error", error_str, input_tokens, output_tokens

        return "error", error_str, input_tokens, output_tokens


def _set_api_credentials(api_key: str, base_url: str, model_override: str | None = None) -> None:
    """Set API credentials in environment variables."""
    os.environ["ANTHROPIC_API_KEY"] = api_key
    if base_url != "https://api.anthropic.com":
        os.environ["ANTHROPIC_BASE_URL"] = base_url
    elif "ANTHROPIC_BASE_URL" in os.environ:
        del os.environ["ANTHROPIC_BASE_URL"]

    # Set model override if specified (for third-party Anthropic-compatible APIs)
    if model_override:
        os.environ["ANTHROPIC_MODEL_OVERRIDE"] = model_override
    elif "ANTHROPIC_MODEL_OVERRIDE" in os.environ:
        del os.environ["ANTHROPIC_MODEL_OVERRIDE"]


async def run_autonomous_agent(
    project_dir: Path,
    model: str,
    max_iterations: int | None = None,
    template_name: str | None = None,
    force_spec: bool = False,
) -> None:
    """
    Run the autonomous agent loop.

    Args:
        project_dir: Directory for the project
        model: Claude model to use
        max_iterations: Maximum number of iterations (None for unlimited)
        template_name: Optional template name (e.g., 'ecommerce', 'task_manager')
        force_spec: If True, always sync app_spec.txt from template
    """
    log_section("AUTONOMOUS CODING AGENT DEMO")
    log_info(f"Project directory: {project_dir}", "Config")
    log_info(f"Model: {model}", "Config")
    if template_name:
        log_info(f"Template: {template_name}", "Config")
    if max_iterations:
        log_info(f"Max iterations: {max_iterations}", "Config")
    else:
        log_info("Max iterations: Unlimited (will run until completion)", "Config")

    # Create project directory
    project_dir = Path(project_dir)
    project_dir.mkdir(parents=True, exist_ok=True)

    # Initialize API rotation state
    try:
        rotation_state = APIRotationState()
        log_success(
            f"API rotation initialized with {len(rotation_state.pairs)} key/endpoint pairs", "API"
        )
    except ValueError as e:
        log_error(str(e), "API")
        return

    # Get initial API credentials
    result = rotation_state.get_next_available_pair()
    if result is None:
        log_error("No available API credentials", "API")
        return

    current_pair_index, api_key, base_url, model_override = result
    _set_api_credentials(api_key, base_url, model_override)

    # Determine effective model (override takes precedence over CLI argument)
    effective_model = model_override if model_override else model

    # Initialize token tracker
    token_tracker = TokenTracker(project_dir)
    log_info(f"Token tracking enabled - report: {token_tracker.report_file}", "Tracking")

    # Check if this is a fresh start or continuation
    tests_file = project_dir / "feature_list.json"
    is_first_run = not tests_file.exists()

    if is_first_run:
        log_info("Fresh start - will use initializer agent", "Init")
        log_section("NOTE: First session takes 10-20+ minutes!")
        log_warn("The agent is generating 200 detailed test cases.", "Init")
        log_warn("This may appear to hang - it's working. Watch for Tool logs.", "Init")
        # Copy the app spec into the project directory for the agent to read
        copy_spec_to_project(project_dir, template_name=template_name, force=force_spec)
    else:
        log_info("Continuing existing project", "Init")
        # Optionally sync spec if force_spec is set
        if force_spec or template_name:
            copy_spec_to_project(project_dir, template_name=template_name, force=force_spec)
        print_progress_summary(project_dir)

    # Main loop
    iteration = 0
    consecutive_quota_errors = 0
    MAX_CONSECUTIVE_QUOTA_ERRORS = 10  # Stop if we cycle through all keys multiple times

    while True:
        iteration += 1

        # Check max iterations
        if max_iterations and iteration > max_iterations:
            log_warn(f"Reached max iterations ({max_iterations})", "Session")
            log_info("To continue, run the script again without --max-iterations", "Session")
            break

        # Print session header
        print_session_header(iteration, is_first_run)

        # Create client (fresh context)
        client = create_client(project_dir, effective_model)

        # Start token tracking session
        current_base_url = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
        token_tracker.start_session(endpoint=current_base_url, model=effective_model)

        # Choose prompt based on session type
        if is_first_run:
            prompt = get_initializer_prompt()
            is_first_run = False  # Only use initializer once
        else:
            prompt = get_coding_prompt()

        # Run session with async context manager
        async with client:
            status, response, in_tokens, out_tokens = await run_agent_session(
                client, prompt, project_dir, token_tracker
            )

        # End token tracking session
        token_tracker.end_session()
        token_tracker.save_report()

        # Handle status
        if status == "continue":
            consecutive_quota_errors = 0  # Reset counter on success
            log_success(f"Agent will auto-continue in {AUTO_CONTINUE_DELAY_SECONDS}s...", "Session")
            print_progress_summary(project_dir)
            await asyncio.sleep(AUTO_CONTINUE_DELAY_SECONDS)

        elif status == "quota_error":
            consecutive_quota_errors += 1

            if consecutive_quota_errors >= MAX_CONSECUTIVE_QUOTA_ERRORS:
                log_section("ALL API KEYS EXHAUSTED")
                log_error("All API keys have been tried multiple times.", "API")
                log_info("Please add more API keys to .env or wait for quota reset.", "API")
                break

            # Mark current pair as exhausted
            is_quota, quota_type = detect_quota_exhaustion(None, response)
            if quota_type:
                rotation_state.mark_exhausted(current_pair_index, quota_type)

            # Try to get next available pair
            result = rotation_state.get_next_available_pair()
            if result is None:
                log_section("ALL API KEYS EXHAUSTED")
                log_error("All API keys are currently in cooling period.", "API")
                log_info("Please add more API keys to .env or wait for quota reset.", "API")
                break

            current_pair_index, api_key, base_url, model_override = result
            _set_api_credentials(api_key, base_url, model_override)

            # Update effective model for the new pair
            effective_model = model_override if model_override else model
            log_warn(f"Switching to pair {current_pair_index + 1}: {base_url}", "API Rotation")
            if model_override:
                log_info(f"Using model override: {model_override}", "API Rotation")
            log_info(f"Will retry in {AUTO_CONTINUE_DELAY_SECONDS}s...", "API Rotation")
            await asyncio.sleep(AUTO_CONTINUE_DELAY_SECONDS)

            # Don't increment iteration counter - retry with new key
            iteration -= 1

        elif status == "error":
            consecutive_quota_errors = 0  # Reset counter
            log_error("Session encountered an error", "Session")
            log_info("Will retry with a fresh session...", "Session")
            await asyncio.sleep(AUTO_CONTINUE_DELAY_SECONDS)

        # Small delay between sessions
        if max_iterations is None or iteration < max_iterations:
            log_info("Preparing next session...", "Session")
            await asyncio.sleep(1)

    # Final summary
    log_section("SESSION COMPLETE")
    log_info(f"Project directory: {project_dir}", "Summary")
    print_progress_summary(project_dir)

    # Print token consumption report
    print(token_tracker.get_summary())

    # Print instructions for running the generated application
    log_section("TO RUN THE GENERATED APPLICATION")
    log_info(f"cd {project_dir.resolve()}", "Run")
    log_info("./init.sh           # Run the setup script", "Run")
    log_info("# Or manually:", "Run")
    log_info("npm install && npm run dev", "Run")
    log_info("Then open http://localhost:3000 (or check init.sh for the URL)", "Run")

    log_success("Done!")
