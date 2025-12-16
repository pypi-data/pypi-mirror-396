"""
Prompt Loading Utilities
========================

Functions for loading prompt templates from the prompts directory.
"""

import shutil
from pathlib import Path


def get_package_root() -> Path:
    """Get the package root directory."""
    # Start from the current file location
    current_file = Path(__file__)

    # Try to find via importlib.metadata (Python 3.8+)
    # This works when the package is installed
    try:
        from importlib.metadata import PackageNotFoundError, files

        try:
            package_files = files("autonomous-coding")
            if package_files:
                for file in package_files:
                    file_path = Path(file.locate())
                    # Find the site-packages root
                    parts = file_path.parts
                    if "site-packages" in parts:
                        idx = parts.index("site-packages")
                        site_packages = Path(*parts[: idx + 1])
                        # Check for .data directory (hatchling shared-data location)
                        # Format: autonomous_coding-X.Y.Z.data/data/
                        for item in site_packages.iterdir():
                            if item.name.startswith("autonomous_coding") and item.is_dir():
                                # Check for .data/data structure
                                data_path = item / "data"
                                if data_path.exists() and (data_path / "prompts").exists():
                                    return data_path
                        break
        except (PackageNotFoundError, AttributeError, ValueError, TypeError):
            pass
    except ImportError:
        pass

    # Development mode: go up from src/core/prompts.py
    dev_root = current_file.parent.parent.parent.parent
    if (dev_root / "prompts").exists():
        return dev_root

    # Fallback: check current working directory
    cwd = Path.cwd()
    if (cwd / "prompts").exists():
        return cwd

    # Default: return development mode path
    return dev_root


def get_prompts_dir() -> Path:
    """Get the prompts directory path."""
    # Try package root location first (works in both dev and installed)
    package_dir = get_package_root()
    prompts_dir = package_dir / "prompts"
    if prompts_dir.exists():
        return prompts_dir

    # Fallback to current working directory
    cwd_prompts = Path.cwd() / "prompts"
    if cwd_prompts.exists():
        return cwd_prompts

    # Create default prompts directory
    prompts_dir.mkdir(parents=True, exist_ok=True)
    return prompts_dir


def get_templates_dir() -> Path:
    """Get the templates directory path."""
    # Try package root location first (works in both dev and installed)
    package_dir = get_package_root()
    templates_dir = package_dir / "templates"
    if templates_dir.exists():
        return templates_dir

    # Fallback to current working directory
    cwd_templates = Path.cwd() / "templates"
    if cwd_templates.exists():
        return cwd_templates

    raise FileNotFoundError("Templates directory not found")


def get_template_path(template_name: str) -> Path:
    """
    Get the path to a template spec file.

    Args:
        template_name: Name of the template (e.g., 'ecommerce', 'task_manager')

    Returns:
        Path to the template file

    Raises:
        FileNotFoundError: If template doesn't exist
    """
    templates_dir = get_templates_dir()

    # Try with _spec.txt suffix first
    template_path = templates_dir / f"{template_name}_spec.txt"
    if template_path.exists():
        return template_path

    # Try exact name
    template_path = templates_dir / template_name
    if template_path.exists():
        return template_path

    # Try with .txt extension
    template_path = templates_dir / f"{template_name}.txt"
    if template_path.exists():
        return template_path

    raise FileNotFoundError(f"Template not found: {template_name}")


def load_prompt(name: str, prompts_dir: Path | None = None) -> str:
    """
    Load a prompt template from the prompts directory.

    Args:
        name: Name of the prompt (without extension)
        prompts_dir: Optional custom prompts directory

    Returns:
        Prompt content as string

    Raises:
        FileNotFoundError: If prompt file doesn't exist
    """
    if prompts_dir is None:
        prompts_dir = get_prompts_dir()

    prompt_path = prompts_dir / f"{name}.md"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt not found: {prompt_path}")

    return prompt_path.read_text()


def get_initializer_prompt(prompts_dir: Path | None = None) -> str:
    """Load the initializer prompt."""
    return load_prompt("initializer_prompt", prompts_dir)


def get_coding_prompt(prompts_dir: Path | None = None) -> str:
    """Load the coding agent prompt."""
    return load_prompt("coding_prompt", prompts_dir)


def get_qa_prompt(prompts_dir: Path | None = None) -> str:
    """Load the QA agent prompt."""
    return load_prompt("qa_prompt", prompts_dir)


def get_orchestrator_prompt(prompts_dir: Path | None = None) -> str:
    """Load the orchestrator prompt."""
    return load_prompt("orchestrator_prompt", prompts_dir)


def get_spec_validation_prompt(prompts_dir: Path | None = None) -> str:
    """Load the spec validation agent prompt."""
    return load_prompt("spec_validation_prompt", prompts_dir)


def copy_spec_to_project(
    project_dir: Path,
    template_name: str | None = None,
    prompts_dir: Path | None = None,
    force: bool = False,
) -> None:
    """
    Copy the app spec file into the project directory for the agent to read.

    Args:
        project_dir: Target project directory
        template_name: Optional template name (e.g., 'ecommerce', 'task_manager')
                      If provided, uses template directly instead of prompts/app_spec.txt
        prompts_dir: Optional custom prompts directory (used if template_name is None)
        force: If True, always copy even if destination exists
    """
    project_dir = Path(project_dir)
    spec_dest = project_dir / "app_spec.txt"

    # Determine source file
    if template_name:
        # Use template directly
        spec_source = get_template_path(template_name)
        print(f"Using template: {template_name}")
    else:
        # Use prompts/app_spec.txt
        if prompts_dir is None:
            prompts_dir = get_prompts_dir()
        spec_source = prompts_dir / "app_spec.txt"

    # Copy if needed
    if not spec_source.exists():
        print(f"Warning: Spec file not found: {spec_source}")
        return

    should_copy = force or not spec_dest.exists()

    if should_copy:
        project_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(spec_source, spec_dest)
        print("Copied app_spec.txt to project directory")
    elif spec_dest.exists():
        # Check if source is newer and warn
        if spec_source.stat().st_mtime > spec_dest.stat().st_mtime:
            print("Note: Template has been updated. Use --force-spec to sync.")
