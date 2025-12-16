"""
Test Configuration
==================

Configures pytest and provides common fixtures for all tests.
"""

import sys
from pathlib import Path

# Add src to path for package imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Also add root for backward compatibility during migration
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

import pytest  # noqa: E402


@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary project directory for testing."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    return project_dir


@pytest.fixture
def sample_feature_list():
    """Return a sample feature list for testing."""
    return [
        {
            "id": 1,
            "description": "Test feature 1",
            "test_steps": ["Step 1", "Step 2"],
            "passes": False,
            "qa_validated": False,
        },
        {
            "id": 2,
            "description": "Test feature 2",
            "test_steps": ["Step 1", "Step 2", "Step 3"],
            "passes": True,
            "qa_validated": True,
        },
    ]
