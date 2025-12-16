"""
Tests for RBAC Pre-Commit Hook
==============================

Tests for Phase 6 (T076-T089): RBAC Enforcement
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path

import pytest


class TestPreCommitHook:
    """Tests for the pre-commit hook RBAC enforcement."""

    @pytest.fixture
    def git_repo(self):
        """Create a temporary git repository with the pre-commit hook."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)

            # Initialize git repo
            subprocess.run(["git", "init"], cwd=repo_dir, capture_output=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo_dir,
                capture_output=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo_dir,
                capture_output=True,
            )

            # Copy pre-commit hook
            hooks_dir = repo_dir / ".git" / "hooks"
            hooks_dir.mkdir(parents=True, exist_ok=True)

            # Read our pre-commit hook
            hook_source = Path(__file__).parent.parent / "hooks" / "pre-commit"
            if hook_source.exists():
                hook_content = hook_source.read_text()
                hook_dest = hooks_dir / "pre-commit"
                hook_dest.write_text(hook_content)
                hook_dest.chmod(0o755)

            # Create initial feature_list.json
            feature_list = [
                {
                    "id": 1,
                    "description": "Test feature",
                    "passes": False,
                    "qa_validated": False,
                }
            ]
            with open(repo_dir / "feature_list.json", "w") as f:
                json.dump(feature_list, f, indent=2)

            # Initial commit
            subprocess.run(["git", "add", "."], cwd=repo_dir, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "Initial commit", "--no-verify"],
                cwd=repo_dir,
                capture_output=True,
            )

            yield repo_dir

    def test_hook_exists_and_executable(self, git_repo):
        """Test that the pre-commit hook exists and is executable."""
        hook_path = git_repo / ".git" / "hooks" / "pre-commit"
        assert hook_path.exists(), "Pre-commit hook should exist"
        assert os.access(hook_path, os.X_OK), "Pre-commit hook should be executable"

    def test_qa_agent_can_modify_passes(self, git_repo):
        """Test T087: QA Agent can modify passes field."""
        # Modify passes field
        with open(git_repo / "feature_list.json") as f:
            features = json.load(f)
        features[0]["passes"] = True
        with open(git_repo / "feature_list.json", "w") as f:
            json.dump(features, f, indent=2)

        # Stage the change
        subprocess.run(["git", "add", "feature_list.json"], cwd=git_repo)

        # Commit with AGENT_TYPE=QA
        env = os.environ.copy()
        env["AGENT_TYPE"] = "QA"
        result = subprocess.run(
            ["git", "commit", "-m", "QA update"],
            cwd=git_repo,
            capture_output=True,
            text=True,
            env=env,
        )

        assert result.returncode == 0, f"QA Agent should be able to commit: {result.stderr}"

    def test_dev_agent_blocked_from_passes(self, git_repo):
        """Test T086: Dev Agent cannot modify passes field."""
        # Modify passes field
        with open(git_repo / "feature_list.json") as f:
            features = json.load(f)
        features[0]["passes"] = True
        with open(git_repo / "feature_list.json", "w") as f:
            json.dump(features, f, indent=2)

        # Stage the change
        subprocess.run(["git", "add", "feature_list.json"], cwd=git_repo)

        # Try to commit with AGENT_TYPE=DEV
        env = os.environ.copy()
        env["AGENT_TYPE"] = "DEV"
        result = subprocess.run(
            ["git", "commit", "-m", "Dev update"],
            cwd=git_repo,
            capture_output=True,
            text=True,
            env=env,
        )

        # Should be blocked
        assert result.returncode != 0, "Dev Agent should be blocked from modifying passes"
        assert "RBAC VIOLATION" in result.stdout or "RBAC VIOLATION" in result.stderr

    def test_unknown_agent_blocked(self, git_repo):
        """Test T088: Unknown agent type is blocked from modifying protected fields."""
        # Modify passes field
        with open(git_repo / "feature_list.json") as f:
            features = json.load(f)
        features[0]["passes"] = True
        with open(git_repo / "feature_list.json", "w") as f:
            json.dump(features, f, indent=2)

        # Stage the change
        subprocess.run(["git", "add", "feature_list.json"], cwd=git_repo)

        # Try to commit without AGENT_TYPE set
        env = os.environ.copy()
        env.pop("AGENT_TYPE", None)  # Remove AGENT_TYPE if present
        result = subprocess.run(
            ["git", "commit", "-m", "Unknown agent update"],
            cwd=git_repo,
            capture_output=True,
            text=True,
            env=env,
        )

        # Should be blocked
        assert result.returncode != 0, "Unknown agent should be blocked"

    def test_dev_agent_can_modify_non_protected_fields(self, git_repo):
        """Test that Dev Agent can modify non-protected fields."""
        # Modify description field (not protected)
        with open(git_repo / "feature_list.json") as f:
            features = json.load(f)
        features[0]["description"] = "Updated description"
        with open(git_repo / "feature_list.json", "w") as f:
            json.dump(features, f, indent=2)

        # Stage the change
        subprocess.run(["git", "add", "feature_list.json"], cwd=git_repo)

        # Commit with AGENT_TYPE=DEV
        env = os.environ.copy()
        env["AGENT_TYPE"] = "DEV"
        result = subprocess.run(
            ["git", "commit", "-m", "Dev update description"],
            cwd=git_repo,
            capture_output=True,
            text=True,
            env=env,
        )

        # Should succeed (description is not protected)
        assert result.returncode == 0, f"Dev should modify description: {result.stderr}"

    def test_no_verify_bypass(self, git_repo):
        """Test T089: --no-verify bypasses the hook."""
        # Modify passes field
        with open(git_repo / "feature_list.json") as f:
            features = json.load(f)
        features[0]["passes"] = True
        with open(git_repo / "feature_list.json", "w") as f:
            json.dump(features, f, indent=2)

        # Stage the change
        subprocess.run(["git", "add", "feature_list.json"], cwd=git_repo)

        # Commit with --no-verify (bypass hook)
        env = os.environ.copy()
        env["AGENT_TYPE"] = "DEV"  # Would normally be blocked
        result = subprocess.run(
            ["git", "commit", "-m", "Emergency bypass", "--no-verify"],
            cwd=git_repo,
            capture_output=True,
            text=True,
            env=env,
        )

        assert result.returncode == 0, "--no-verify should bypass the hook"

    def test_non_feature_list_changes_allowed(self, git_repo):
        """Test that changes to other files are always allowed."""
        # Create and modify a different file
        (git_repo / "other_file.txt").write_text("Hello, world!")
        subprocess.run(["git", "add", "other_file.txt"], cwd=git_repo)

        # Commit without AGENT_TYPE
        env = os.environ.copy()
        env.pop("AGENT_TYPE", None)
        result = subprocess.run(
            ["git", "commit", "-m", "Add other file"],
            cwd=git_repo,
            capture_output=True,
            text=True,
            env=env,
        )

        assert result.returncode == 0, "Other files should always be committable"

    def test_qa_validated_field_protected(self, git_repo):
        """Test that qa_validated field is also protected."""
        # Modify qa_validated field
        with open(git_repo / "feature_list.json") as f:
            features = json.load(f)
        features[0]["qa_validated"] = True
        with open(git_repo / "feature_list.json", "w") as f:
            json.dump(features, f, indent=2)

        # Stage the change
        subprocess.run(["git", "add", "feature_list.json"], cwd=git_repo)

        # Try to commit with AGENT_TYPE=DEV
        env = os.environ.copy()
        env["AGENT_TYPE"] = "DEV"
        result = subprocess.run(
            ["git", "commit", "-m", "Dev update qa_validated"],
            cwd=git_repo,
            capture_output=True,
            text=True,
            env=env,
        )

        # Should be blocked
        assert result.returncode != 0, "Dev Agent should be blocked from qa_validated"


class TestAuditLogging:
    """Tests for T083-T084: Audit logging."""

    @pytest.fixture
    def git_repo_with_log(self):
        """Create a temporary git repository with logging enabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)

            # Initialize git repo
            subprocess.run(["git", "init"], cwd=repo_dir, capture_output=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo_dir,
                capture_output=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo_dir,
                capture_output=True,
            )

            # Copy pre-commit hook
            hooks_dir = repo_dir / ".git" / "hooks"
            hooks_dir.mkdir(parents=True, exist_ok=True)

            hook_source = Path(__file__).parent.parent / "hooks" / "pre-commit"
            if hook_source.exists():
                hook_content = hook_source.read_text()
                hook_dest = hooks_dir / "pre-commit"
                hook_dest.write_text(hook_content)
                hook_dest.chmod(0o755)

            # Create initial feature_list.json
            feature_list = [{"id": 1, "description": "Test", "passes": False}]
            with open(repo_dir / "feature_list.json", "w") as f:
                json.dump(feature_list, f, indent=2)

            # Initial commit
            subprocess.run(["git", "add", "."], cwd=repo_dir, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "Initial", "--no-verify"],
                cwd=repo_dir,
                capture_output=True,
            )

            yield repo_dir

    def test_log_file_created_on_modification(self, git_repo_with_log):
        """Test that log file is created when feature_list.json is modified."""
        # Modify feature_list.json (non-protected field)
        with open(git_repo_with_log / "feature_list.json") as f:
            features = json.load(f)
        features[0]["description"] = "Updated"
        with open(git_repo_with_log / "feature_list.json", "w") as f:
            json.dump(features, f, indent=2)

        subprocess.run(["git", "add", "feature_list.json"], cwd=git_repo_with_log)

        env = os.environ.copy()
        env["AGENT_TYPE"] = "DEV"
        subprocess.run(
            ["git", "commit", "-m", "Update"],
            cwd=git_repo_with_log,
            capture_output=True,
            env=env,
        )

        log_file = git_repo_with_log / ".git" / "hooks" / "pre-commit.log"
        assert log_file.exists(), "Log file should be created"

    def test_violation_logged(self, git_repo_with_log):
        """Test that RBAC violations are logged."""
        # Modify passes field
        with open(git_repo_with_log / "feature_list.json") as f:
            features = json.load(f)
        features[0]["passes"] = True
        with open(git_repo_with_log / "feature_list.json", "w") as f:
            json.dump(features, f, indent=2)

        subprocess.run(["git", "add", "feature_list.json"], cwd=git_repo_with_log)

        env = os.environ.copy()
        env["AGENT_TYPE"] = "DEV"
        subprocess.run(
            ["git", "commit", "-m", "Violation"],
            cwd=git_repo_with_log,
            capture_output=True,
            env=env,
        )

        log_file = git_repo_with_log / ".git" / "hooks" / "pre-commit.log"
        if log_file.exists():
            log_content = log_file.read_text()
            assert "VIOLATION=YES" in log_content or "ERROR" in log_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
