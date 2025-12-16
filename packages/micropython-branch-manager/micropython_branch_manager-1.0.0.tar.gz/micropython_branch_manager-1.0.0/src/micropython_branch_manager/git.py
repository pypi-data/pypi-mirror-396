"""Git operations wrapper for micropython-branch-manager."""

import subprocess
from pathlib import Path

from .exceptions import (
    GitError,
    MergeConflictError,
    RebaseConflictError,
    RemoteDivergenceError,
    WorkingTreeDirtyError,
)


class GitRepo:
    """Wrapper for git operations in a specific directory."""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path

    def run(self, *args: str, check: bool = True, capture: bool = True) -> str:
        """Execute git command, return stdout."""
        cmd = ["git", *args]
        result = subprocess.run(
            cmd,
            cwd=self.repo_path,
            capture_output=capture,
            text=True,
        )
        if check and result.returncode != 0:
            raise GitError(f"git {args[0]} failed: {result.stderr}")
        return result.stdout.strip() if result.stdout else ""

    def is_clean(self) -> bool:
        """Check if working tree is clean."""
        return self.run("status", "--porcelain") == ""

    def require_clean(self) -> None:
        """Raise if working tree has uncommitted changes."""
        if not self.is_clean():
            raise WorkingTreeDirtyError(
                "Working tree has uncommitted changes. Please commit or stash changes first."
            )

    def fetch(self, remote: str = "--all") -> None:
        """Fetch from remote(s)."""
        # Sync submodule URLs first to avoid stale references
        self.run("submodule", "sync", "--recursive", check=False)

        # Fetch from remotes - allow submodule errors but catch main repo errors
        cmd = ["git", "fetch", remote]
        result = subprocess.run(
            cmd,
            cwd=self.repo_path,
            capture_output=True,
            text=True,
        )
        # Only raise error if the main fetch failed (not just submodule errors)
        # Git fetch writes to stderr, check if there are non-submodule errors
        if result.returncode != 0:
            stderr = result.stderr.lower()
            # Allow submodule fetch errors as they don't affect main repo fetch
            if "submodule" not in stderr or (
                "fatal" in stderr and "submodule" not in stderr.split("fatal")[0]
            ):
                raise GitError(f"git fetch failed: {result.stderr}")

    def checkout(self, ref: str, create: bool = False, force: bool = False) -> None:
        """Checkout branch or ref."""
        args = ["checkout"]
        if create:
            args.append("-B" if force else "-b")
        args.append(ref)
        self.run(*args)

    def rebase(self, onto: str, update_refs: bool = True) -> None:
        """Rebase with merge commit preservation.

        Raises:
            RebaseConflictError: If conflicts require manual resolution
        """
        args = ["rebase", "--rebase-merges"]
        if update_refs:
            args.append("--update-refs")
        args.append(onto)

        try:
            self.run(*args)
        except GitError as e:
            # Check if this is a conflict situation
            status = self.run("status", "--porcelain", check=False)
            if "UU " in status or "AA " in status or "DD " in status:
                conflicting = [
                    line[3:]
                    for line in status.split("\n")
                    if line.startswith(("UU ", "AA ", "DD "))
                ]
                raise RebaseConflictError(
                    "Rebase stopped due to conflicts.\n"
                    "Conflicting files:\n  " + "\n  ".join(conflicting) + "\n\n"
                    "Please resolve conflicts manually, then run:\n"
                    "  git rebase --continue\n\n"
                    "Or to abort:\n"
                    "  git rebase --abort",
                    conflicting_files=conflicting,
                ) from e
            raise

    def merge(self, branch: str, message: str, no_ff: bool = True) -> None:
        """Merge branch with optional no-ff.

        Raises:
            MergeConflictError: If conflicts require manual resolution
        """
        args = ["merge"]
        if no_ff:
            args.append("--no-ff")
        args.extend([branch, "-m", message])

        try:
            self.run(*args)
        except GitError as e:
            status = self.run("status", "--porcelain", check=False)
            if "UU " in status or "AA " in status or "DD " in status:
                conflicting = [
                    line[3:]
                    for line in status.split("\n")
                    if line.startswith(("UU ", "AA ", "DD "))
                ]
                raise MergeConflictError(
                    "Merge stopped due to conflicts.\n"
                    "Conflicting files:\n  " + "\n  ".join(conflicting) + "\n\n"
                    "Please resolve conflicts manually, then run:\n"
                    "  git merge --continue\n\n"
                    "Or to abort:\n"
                    "  git merge --abort",
                    conflicting_files=conflicting,
                ) from e
            raise

    def push(self, remote: str, branch: str, force: bool = False) -> None:
        """Push branch to remote."""
        args = ["push"]
        if force:
            args.append("--force")
        args.extend([remote, branch])
        self.run(*args)

    def get_merge_base(self, ref1: str, ref2: str) -> str:
        """Get merge base commit."""
        return self.run("merge-base", ref1, ref2)

    def rev_parse(self, ref: str) -> str:
        """Resolve ref to commit hash."""
        return self.run("rev-parse", ref)

    def branch_exists(self, branch: str, remote: bool = False) -> bool:
        """Check if branch exists."""
        ref = f"refs/remotes/{branch}" if remote else f"refs/heads/{branch}"
        try:
            self.run("rev-parse", "--verify", ref)
            return True
        except GitError:
            return False

    def create_branch(self, name: str, start_point: str) -> None:
        """Create branch from start point."""
        self.run("branch", name, start_point)

    def set_branch_upstream(self, branch: str, upstream: str) -> None:
        """Set upstream tracking for a branch."""
        self.run("branch", f"--set-upstream-to={upstream}", branch)

    def ensure_remote(self, name: str, url: str) -> None:
        """Ensure remote exists with correct URL."""
        try:
            current = self.run("config", f"remote.{name}.url")
            if current != url:
                self.run("remote", "set-url", name, url)
        except GitError:
            self.run("remote", "add", name, url)

    def list_remotes(self) -> dict[str, str]:
        """List all remotes with URLs."""
        output = self.run("remote", "-v")
        remotes = {}
        for line in output.split("\n"):
            if line and "(fetch)" in line:
                parts = line.split()
                if len(parts) >= 2:
                    remotes[parts[0]] = parts[1]
        return remotes

    def get_log_subjects(self, range_spec: str) -> list[str]:
        """Get commit subjects in range."""
        output = self.run("log", "--format=%s", range_spec)
        return [line for line in output.split("\n") if line]

    def check_divergence(
        self, local_branch: str, remote_branch: str, force_push: bool = False
    ) -> None:
        """Check if remote branch has diverged from local branch.

        Args:
            local_branch: Local branch name
            remote_branch: Remote branch ref (e.g., 'origin/branch-name')
            force_push: If True, skip the divergence check

        Raises:
            RemoteDivergenceError: If remote has commits not in local branch
        """
        if force_push:
            return

        try:
            # Check if remote branch exists
            self.run("rev-parse", "--verify", remote_branch)
        except GitError:
            # Remote branch doesn't exist, no divergence
            return

        # Count commits in remote not in local
        try:
            remote_only = self.run("rev-list", "--count", f"{local_branch}..{remote_branch}")
            local_only = self.run("rev-list", "--count", f"{remote_branch}..{local_branch}")

            remote_count = int(remote_only) if remote_only else 0
            local_count = int(local_only) if local_only else 0

            if remote_count > 0:
                raise RemoteDivergenceError(
                    f"Remote branch '{remote_branch}' has {remote_count} commit(s) "
                    f"not in local branch '{local_branch}'.\n"
                    f"Local branch has {local_count} commit(s) not in remote.\n\n"
                    "This may indicate that the remote has been updated since your last fetch.\n"
                    "Options:\n"
                    "  1. Fetch and review remote changes first\n"
                    "  2. Use --force-push to overwrite remote (USE WITH CAUTION)\n"
                    "  3. Abort and investigate the divergence",
                    branch=local_branch,
                    remote_commits=remote_count,
                    local_commits=local_count,
                )
        except ValueError:
            # Error parsing commit counts, skip check
            pass
