"""
Command-Line Interface for Autonomous Coding Agent
===================================================

Provides CLI entry points for running the autonomous coding system.

Usage:
    # Run demo (default)
    autonomous-coding --project-dir ./my_project

    # Run with limited iterations
    autonomous-coding --project-dir ./my_project --max-iterations 3

    # Run orchestrator
    ac-orchestrator --project-dir ./my_project

    # Run QA agent
    ac-qa --project-dir ./my_project --feature-id 1
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv

# Try to load .env from current directory, then from package root
load_dotenv()  # Load from current directory
load_dotenv(Path(__file__).parent.parent / ".env")  # Load from package root


def main():
    """Main entry point for autonomous-coding CLI."""
    parser = argparse.ArgumentParser(
        description="Autonomous Coding Agent - Build applications with AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Quick demo (3 iterations)
    autonomous-coding --project-dir ./my_project --max-iterations 3

    # Full build with ecommerce template
    autonomous-coding --project-dir ./my_project --spec ecommerce

    # Build task manager app
    autonomous-coding --project-dir ./my_project --spec task_manager

    # Force update spec file from template
    autonomous-coding --project-dir ./my_project --spec ecommerce --force-spec

    # Use specific model
    autonomous-coding --project-dir ./my_project --model claude-sonnet-4-5-20250929

Available templates (in templates/ directory):
    - ecommerce     : E-commerce platform (ShopFlow)
    - task_manager  : Task management app (TaskFlow)
        """,
    )

    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path("./autonomous_demo_project"),
        help="Directory for the project (default: ./autonomous_demo_project)",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help="Maximum number of agent iterations (default: unlimited)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="claude-sonnet-4-5-20250929",
        help="Claude model to use (default: claude-sonnet-4-5-20250929)",
    )
    parser.add_argument(
        "--agent",
        type=str,
        choices=["initializer", "dev", "qa", "spec_validator"],
        default=None,
        help="Run specific agent type (used by orchestrator)",
    )
    parser.add_argument(
        "--spec",
        type=str,
        default=None,
        help="Template name to use (e.g., 'ecommerce', 'task_manager'). Uses templates/ directory.",
    )
    parser.add_argument(
        "--force-spec",
        action="store_true",
        help="Force update app_spec.txt even if it already exists in project",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="autonomous-coding 2.0.1",
    )

    args = parser.parse_args()

    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("\nGet your API key from: https://console.anthropic.com/")
        print("\nThen set it:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        sys.exit(1)

    # Handle specific agent types (used by orchestrator)
    if args.agent == "spec_validator":
        import uuid

        from core.orchestrator import write_agent_completion_signal
        from quality.spec_validator import run_spec_validator

        async def run_spec_validation():
            next_state, report = await run_spec_validator(args.project_dir)
            # Write completion signal for orchestrator
            write_agent_completion_signal(
                project_dir=args.project_dir,
                agent_type="SPEC_VALIDATOR",
                session_id=str(uuid.uuid4()),
                status="COMPLETE",
                next_state=next_state,
            )

        asyncio.run(run_spec_validation())
        return

    from agents.session import run_autonomous_agent

    # Run the demo
    asyncio.run(
        run_autonomous_agent(
            project_dir=args.project_dir,
            model=args.model,
            max_iterations=args.max_iterations,
            template_name=args.spec,
            force_spec=args.force_spec,
        )
    )


def demo():
    """Entry point for ac-demo command."""
    main()


def orchestrator():
    """Entry point for ac-orchestrator command."""
    parser = argparse.ArgumentParser(
        description="Orchestrator - Manage multi-agent workflow",
    )

    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path.cwd(),
        help="Project directory path",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit (for testing)",
    )

    args = parser.parse_args()

    from core.orchestrator import Orchestrator

    orch = Orchestrator(args.project_dir)

    if args.once:
        state = orch.run_once()
        print(json.dumps(state, indent=2))
    else:
        orch.run()


def qa_agent():
    """Entry point for ac-qa command."""
    parser = argparse.ArgumentParser(
        description="QA Agent - Run quality validation on features",
    )

    parser.add_argument(
        "--project-dir",
        type=Path,
        required=True,
        help="Project directory path",
    )
    parser.add_argument(
        "--feature-id",
        type=int,
        help="Feature ID to validate",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Validate all features",
    )

    args = parser.parse_args()

    from quality.qa_agent import QAAgent

    qa = QAAgent(args.project_dir)

    if args.feature_id:
        report = qa.run_quality_gates(feature_id=args.feature_id, feature_description="")
        report_path = qa.save_report(report)
        print(f"QA Report saved to: {report_path}")
        print(f"Status: {report['overall_status']}")
    elif args.all:
        print("Running QA on all features...")
        # Implementation would iterate through feature_list.json
    else:
        parser.print_help()


def spec_validator():
    """Entry point for ac-spec-validator command."""
    parser = argparse.ArgumentParser(
        description="Spec Validator - Validate app specification before coding",
    )

    parser.add_argument(
        "--project-dir",
        type=Path,
        required=True,
        help="Project directory path",
    )

    args = parser.parse_args()

    from quality.spec_validator import run_spec_validator

    asyncio.run(run_spec_validator(args.project_dir))


if __name__ == "__main__":
    main()
