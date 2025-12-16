"""Tests for custom exceptions."""

from micropython_branch_manager.exceptions import (
    MBMError,
    MergeConflictError,
    RebaseConflictError,
    RemoteDivergenceError,
)


def test_rebase_conflict_error_with_files():
    """RebaseConflictError stores conflicting files."""
    files = ["file1.py", "file2.py"]
    error = RebaseConflictError("Conflict occurred", conflicting_files=files)

    assert str(error) == "Conflict occurred"
    assert error.conflicting_files == files
    assert error.pr_context == {}
    assert isinstance(error, MBMError)


def test_rebase_conflict_error_with_pr_context():
    """RebaseConflictError stores PR context."""
    context = {"pr_number": 12345, "branch_name": "feature", "branch_title": "Add feature"}
    error = RebaseConflictError("Conflict in PR", pr_context=context)

    assert error.pr_context == context
    assert error.conflicting_files == []


def test_merge_conflict_error_attributes():
    """MergeConflictError stores conflicting files."""
    files = ["src/main.py", "tests/test_main.py"]
    error = MergeConflictError("Merge conflict", conflicting_files=files)

    assert str(error) == "Merge conflict"
    assert error.conflicting_files == files
    assert isinstance(error, MBMError)


def test_remote_divergence_error_attributes():
    """RemoteDivergenceError stores branch and commit counts."""
    error = RemoteDivergenceError(
        message="Branch diverged",
        branch="feature",
        remote_commits=5,
        local_commits=3,
    )

    assert str(error) == "Branch diverged"
    assert error.branch == "feature"
    assert error.remote_commits == 5
    assert error.local_commits == 3
    assert isinstance(error, MBMError)
