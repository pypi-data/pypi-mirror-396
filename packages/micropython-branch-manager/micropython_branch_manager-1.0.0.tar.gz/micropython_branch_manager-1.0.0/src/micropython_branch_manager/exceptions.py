"""Custom exceptions for micropython-branch-manager."""

from typing import Any


class MBMError(Exception):
    """Base exception for micropython-branch-manager."""


class ConfigError(MBMError):
    """Configuration loading or validation error."""


class GitError(MBMError):
    """Git operation failed."""


class GitHubError(MBMError):
    """GitHub CLI operation failed."""


class GitHubCLINotFound(GitHubError):
    """gh CLI not installed or not in PATH."""


class RebaseConflictError(GitError):
    """Rebase stopped due to conflicts requiring manual resolution."""

    def __init__(
        self,
        message: str,
        conflicting_files: list[str] | None = None,
        pr_context: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.conflicting_files = conflicting_files or []
        self.pr_context = pr_context or {}


class MergeConflictError(GitError):
    """Merge stopped due to conflicts requiring manual resolution."""

    def __init__(self, message: str, conflicting_files: list[str] | None = None):
        super().__init__(message)
        self.conflicting_files = conflicting_files or []


class WorkingTreeDirtyError(GitError):
    """Working tree has uncommitted changes."""


class RemoteDivergenceError(GitError):
    """Remote branch has diverged from local branch."""

    def __init__(self, message: str, branch: str, remote_commits: int, local_commits: int):
        super().__init__(message)
        self.branch = branch
        self.remote_commits = remote_commits
        self.local_commits = local_commits
