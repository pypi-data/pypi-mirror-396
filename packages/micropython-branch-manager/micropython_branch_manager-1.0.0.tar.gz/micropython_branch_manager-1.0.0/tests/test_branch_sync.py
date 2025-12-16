"""Tests for branch synchronization logic."""

from subprocess import CompletedProcess
from unittest.mock import patch

from micropython_branch_manager.branch_sync import (
    extract_branches_from_merges,
    sync_config_with_branches,
    validate_branches,
)
from micropython_branch_manager.config import BranchConfig, MicroPythonConfig
from micropython_branch_manager.git import GitRepo
from micropython_branch_manager.github import PRInfo


def test_extract_branches_from_merges_empty(tmp_path):
    """extract_branches returns empty list if no merges."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = CompletedProcess(
            [], 0, stdout="Initial commit\nAdd feature\n", stderr=""
        )
        git = GitRepo(tmp_path)

        branches = extract_branches_from_merges(git, "upstream/master", "main")

        assert branches == []


def test_extract_branches_from_merges_single(tmp_path):
    """extract_branches finds single merge."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = CompletedProcess(
            [], 0, stdout="Merge branch 'feature-1'\n\nAdd feature\n", stderr=""
        )
        git = GitRepo(tmp_path)

        branches = extract_branches_from_merges(git, "upstream/master", "main")

        assert branches == ["feature-1"]


def test_extract_branches_from_merges_multiple(tmp_path):
    """extract_branches finds multiple merges in order."""
    with patch("subprocess.run") as mock_run:
        # Git log shows newest first, so feature-2 comes before feature-1
        # But extract_branches reverses to get oldest first
        mock_run.return_value = CompletedProcess(
            [],
            0,
            stdout=(
                "Merge branch 'feature-2'\n\nAdd feature 2\n\n"
                "Merge branch 'feature-1'\n\nAdd feature 1\n"
            ),
            stderr="",
        )
        git = GitRepo(tmp_path)

        branches = extract_branches_from_merges(git, "upstream/master", "main")

        # Should be oldest first
        assert branches == ["feature-1", "feature-2"]


def test_sync_config_adds_new_branches():
    """sync_config_with_branches adds missing branches."""
    config = MicroPythonConfig(
        integration_branch="main",
        branches=[BranchConfig(name="existing", remote="origin")],
    )
    detected = ["existing", "new-branch"]
    pr_cache = {
        "new-branch": PRInfo(
            number=123,
            branch="new-branch",
            title="Add new feature",
            url="https://github.com/micropython/micropython/pull/123",
            state="OPEN",
            author="testuser",
        )
    }

    modified = sync_config_with_branches(config, detected, pr_cache)

    assert modified is True
    assert len(config.branches) == 2
    new_branch = config.get_branch("new-branch")
    assert new_branch is not None
    assert new_branch.pr_number == 123
    assert new_branch.title == "Add new feature"


def test_sync_config_preserves_existing():
    """sync_config_with_branches preserves existing branch data."""
    config = MicroPythonConfig(
        integration_branch="main",
        branches=[
            BranchConfig(name="feature-1", remote="custom", pr_number=100, title="Old title"),
            BranchConfig(name="feature-2", remote="origin"),
        ],
    )
    detected = ["feature-1", "feature-2"]
    pr_cache = {}

    sync_config_with_branches(config, detected, pr_cache)

    # No new branches added, but order may change
    assert len(config.branches) == 2
    feature1 = config.get_branch("feature-1")
    assert feature1.remote == "custom"
    assert feature1.pr_number == 100
    assert feature1.title == "Old title"


def test_validate_branches_warnings():
    """validate_branches returns warnings for mismatches."""
    config = MicroPythonConfig(
        integration_branch="main",
        branches=[
            BranchConfig(name="feature-1"),
            BranchConfig(name="removed-branch"),
        ],
    )
    detected = ["feature-1", "new-branch"]

    warnings = validate_branches(config, detected)

    assert len(warnings) == 2
    # Check for missing from history warning
    assert any("removed-branch" in w and "not found in merge history" in w for w in warnings)
    # Check for missing from config info
    assert any("new-branch" in w and "will be added" in w for w in warnings)
